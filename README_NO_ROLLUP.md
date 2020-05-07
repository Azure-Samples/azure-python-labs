# Real-Time Analytics on Azure Database for PostgreSQL - Hyperscale (Citus) (preview)

Azure Database for PostgreSQL is a managed service that you use to run, manage, and scale highly available PostgreSQL databases in the cloud. This Quickstart shows you how to create an Azure Database for PostgreSQL - Hyperscale (Citus) (preview) server group using the Azure portal. You'll explore distributed data: sharding tables across nodes, ingesting sample data, and run queries that are automatically parallelized across multiple nodes. 

## Prerequisites

If you are **not** at an event, please see [REQUIREMENTS](REQUIREMENTS.md) to install the prerequisites for this lab.

## Create and distribute tables

Once connected to the Hyperscale coordinator node using psql, you can complete some basic tasks.

Within Hyperscale servers there are three types of tables:

- Distributed or sharded tables (spread out to help scaling for performance and parallelization)
- Reference tables (multiple copies maintained)
- Local tables (tables you don't join to, typically administration/logging tables)

In this quickstart, we'll set up some distributed tables, learn how they work, and show how they make analytics faster.  

The data model we're going to work with is simple: user and event data from our GitHub repo. Events include fork creation, git commits related to an organization, and more.

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

As you can see, we've got perfectly normal SQL running in a distributed environment with no changes to our actual queries. This is a very powerful tool for scaling PostgreSQL to any size you need without dealing with the traditional complexity of distributed systems
