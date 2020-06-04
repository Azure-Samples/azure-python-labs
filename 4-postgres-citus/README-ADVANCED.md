# Real-Time Analytics on Azure Database for PostgreSQL - Hyperscale (Citus)

Azure Database for PostgreSQL is a managed service that you use to run, manage, and scale highly available PostgreSQL databases in the cloud. This Quickstart shows you how to create an Azure Database for PostgreSQL - Hyperscale (Citus) server group using the Azure portal. You'll explore distributed data: sharding tables across nodes, ingesting sample data, running queries that execute on multiple nodes, and learn how to use rollup queries to make real-time analytics even faster.

## Prerequisites

If you are **not** at an event, please see [REQUIREMENTS](REQUIREMENTS.md) to install the prerequisites for this lab.

## Create and distribute tables

Once connected to the Hyperscale coordinator node using psql, you can complete some basic tasks.

Within Hyperscale servers there are three types of tables:

- Distributed or sharded tables (spread out to help scaling for performance and parallelization)
- Reference tables (multiple copies maintained)
- Local tables (tables you don't join to, typically administration/logging tables)

In this quickstart, we'll set up some distributed tables, learn how they work, and show how they make analytics faster.  

The data model we're going to work with is simple: user and event data from GitHub. Events include fork creation, git commits related to an organization, and more.

Connect to the Hyperscale coordinator using psql:

```bash
# if you are at an event, run the following lines to get your connection string automatically
i=$(az account show | jq -r '.user.name |= split("@")[0] | .user.name |= split("-")[1] | .user.name')
if [ "$i" = "null" ]; then i='1'; else echo $i; fi
CONNECTION_STRING=$(az keyvault secret show --vault kv190700 --name citus-${i} | jq -r .value)
# CONNECTION_STRING will be in the format:
# "host={server_name}.postgres.database.azure.com port=5432 dbname=citus user=citus password={your_password} sslmode=require"

# connect to server (if not at an event, replace $CONNECTION_STRING with your connection string)
psql "$CONNECTION_STRING"
```

Once you've connected via psql using the above command, let's create our tables. In the psql console run:

```sql
-- re-initializing database
DROP OWNED BY citus;

CREATE TABLE github_events
(
    event_id bigint,
    event_type text,
    event_public boolean,
    repo_id bigint,
    payload jsonb,
    repo jsonb,
    user_id bigint,
    org jsonb,
    created_at timestamp with time zone
);

CREATE TABLE github_users
(
    user_id bigint,
    url text,
    login text,
    avatar_url text,
    gravatar_id text,
    display_login text
);
```

The `payload` field of `github_events` has a JSONB datatype. JSONB is the JSON datatype in binary form in Postgres. The datatype makes it easy to store a flexible schema in a single column.

Postgres can create a `GIN` index on this type, which will index every key and value within it. With an  index, it becomes fast and easy to query the payload with various conditions. Let's go ahead and create a couple of indexes before we load our data. In psql:

```sql
CREATE INDEX event_type_index ON github_events (event_type);
CREATE INDEX payload_index ON github_events USING GIN (payload jsonb_path_ops);
```

Next we’ll take those Postgres tables on the coordinator node and tell Hyperscale to shard them across the workers. To do so, we’ll run a query for each table specifying the key to shard it on. In the current example we’ll shard both the events and users table on `user_id`, causing all database entries on each of these tables with the same `user_id` to be on the same node in your cluster:

```sql
SELECT create_distributed_table('github_events', 'user_id');
SELECT create_distributed_table('github_users', 'user_id');
```

We're ready to load data. In psql still, shell out to download the files:

```sql
\! curl -O https://examples.citusdata.com/users.csv
\! curl -O https://examples.citusdata.com/events.csv
```

Next, load the data from the files into the distributed tables:

```sql
\copy github_events from 'events.csv' WITH CSV
\copy github_users from 'users.csv' WITH CSV
```

## Run queries

Now it's time for the fun part, actually running some queries. Let's start with a simple `count (*)` to see how much data we loaded:

```sql
SELECT count(*) from github_events;
```

That worked nicely. We'll come back to that sort of aggregation in a bit, but for now let’s look at a few other queries. Within the JSONB `payload` column there's a good bit of data, but it varies based on event type. `PushEvent` events contain a size that includes the number of distinct commits for the push. We can use it to find the total number of commits per hour:

```sql
SELECT date_trunc('hour', created_at) AS hour,
       sum((payload->>'distinct_size')::int) AS num_commits
FROM github_events
WHERE event_type = 'PushEvent'
GROUP BY hour
ORDER BY hour;
```

So far the queries have involved the github\_events exclusively, but we can combine this information with github\_users. Since we sharded both users and events on the same identifier (`user_id`), the rows of both tables with matching user IDs will be [colocated](https://docs.citusdata.com/en/stable/sharding/data_modeling.html#colocation) on the same database nodes and can easily be joined.

If we join on `user_id`, Hyperscale can push the join execution down into shards for execution in parallel on worker nodes. For example, let's find the users who created the greatest number of repositories:

```sql
SELECT login, count(*)
FROM github_events ge
JOIN github_users gu
ON ge.user_id = gu.user_id
WHERE event_type = 'CreateEvent' AND
      payload @> '{"ref_type": "repository"}'
GROUP BY login
ORDER BY count(*) DESC;
```

## Rolling up data

The previous query works fine in the early stages, but its performance degrades as your data scales. Even with distributed processing, it's faster to pre-compute the data than to recalculate it repeatedly.

We can ensure our dashboard stays fast by regularly rolling up the raw data into an aggregate table. You can experiment with the aggregation duration. We used a per-minute aggregation table, but you could break data into 5, 15, or 60 minutes instead.

First, we're going to create and distribute a rollup table:

```sql
-- sum of events per repo per user per minute
CREATE TABLE github_rollup_1min
(
    event_type text,
    repo_id bigint,
    user_id bigint,
    total_events bigint,
    ingest_time TIMESTAMPTZ
);

-- last invoked time
CREATE TABLE latest_rollup (
  minute timestamptz PRIMARY KEY,

  CHECK (minute = date_trunc('minute', minute))
);

SELECT create_distributed_table('github_rollup_1min', 'user_id');
```

To run this roll-up more easily, we're going to put it into a plpgsql function. Run these commands in psql to create the rollup_http_request function.

```sql
-- initialize to a time long ago
INSERT INTO latest_rollup VALUES ('10-10-1901');

-- create rollup function
CREATE OR REPLACE FUNCTION rollup_http_request() RETURNS void AS $$
DECLARE
  curr_rollup_time timestamptz := date_trunc('minute', now());
  last_rollup_time timestamptz := minute from latest_rollup;
BEGIN
  INSERT INTO github_rollup_1min (
    event_type,repo_id,user_id,total_events,ingest_time
  ) SELECT
    event_type,
    repo_id,
    user_id,
    count(1) AS total_events,
    date_trunc('minute', created_at) AS ingest_minute
    FROM github_events 
  -- roll up only data new since last_rollup_time
  WHERE date_trunc('minute', created_at) <@
          tstzrange(last_rollup_time, curr_rollup_time, '(]')
  GROUP BY event_type,repo_id,user_id,ingest_minute
  ORDER BY user_id,event_type;

  -- update the value in latest_rollup so that next time we run the
  -- rollup it will operate on data newer than curr_rollup_time
  UPDATE latest_rollup SET minute = curr_rollup_time;
END;
$$ LANGUAGE plpgsql;
```

Now that we have the rollup query, let's run it:

```sql
SELECT rollup_http_request();
```

Now that our data is aggregated, let's take a look at our new analytics table to see what users were most active when and what they were doing then:

```sql
SELECT user_id,ingest_time,sum(total_events)
FROM github_rollup_1min 
GROUP by 1,2 
ORDER by 3 desc 
LIMIT 5;
```

As you can see, we've got some very useful information for user activity dashboards, and thanks to the rollup query precomputing some of the sums, we're able to get aggregate results very quickly. This will let us build extremely responsive applications that give detailed information over huge datasets. 