# Real Time Transactional and Analytical Processing on Azure Database for PostgreSQL - Hyperscale (Citus)

Azure Database for PostgreSQL is a fully managed database-as-a-service based on the open-source Postgres relational database engine. The Hyperscale (Citus) deployment option enables you to scale queries horizontally- across multiple machines, to serve applications that require greater scale and performance. Citus transforms Postgres into a distributed database with features like sharding, a distributed SQL engine, reference tables, and distributed tables. The combination of parallelism, keeping more data in memory, and higher I/O bandwidth can lead to significant performance improvements

With the latest release, Citus 10 is now available in preview on Azure Hyperscale(Citus) with exsiting new capabilities like Columnar Storage, sharding on a single node Postgres machine, Joins between Local PostgreSQL & Citus tables and much more.

In this lab, we will learn about some of the superpowers that Citus brings to the table by distributing data across multiple nodes. We will explore:

- How to create an Azure Database for PostgreSQL-Hyperscale(Citus) using Azure Portal
- Concepts of Sharding on Hyperscale(Citus) Basic Tier
- Creating schemas and ingesting data into an Hyperscale(Citus) instance
- Using Columnar Storage to reduce storage cost and speedup analytical queries
- Scaling the Hyperscale(Citus)-Basic Tier to Standard Tier
- Rebalancing the data and capturing performance improvements

To test the new features of Citus you can either use:

- [Citus 10 Open Source](https://www.citusdata.com/download/) or;
- [Hyperscale(Citus) on Azure Database for PostgreSQL](https://docs.microsoft.com/en-us/azure/postgresql/hyperscale-overview)

**Note:** You can even run Citus on [Docker](https://docs.citusdata.com/en/v10.0/installation/single_node_docker.html). But Docker image is intended to be used for development or testing purposes only and for production workloads.

## Prerequisites

Please follow the steps listed under [REQUIREMENTS](REQUIREMENTS.md) to install the prerequisites for this lab.

## Connecting to the Hyperscale(Citus) Database

Connecting to an Azure Database for PostgreSQL-Hyperscale(Citus) database requires the fully qualified server name and login credentials. You can get this information from the Azure portal.

1. In the [Azure portal](https://portal.azure.com/), search for and select your Azure Database for PostgreSQL-Hyperscale(Citus) server name. 
1. On the server's **Overview** page, copy the fully qualified **Server name**. The fully qualified **Server name** is always of the form *\<my-server-name>.postgres.database.azure.com*. For Hyperscale(Citus) the default **Admin username** is always **'Citus'**.
1. You will also need your **Admin password** which you chose when you created the server, otherwise you can reset it using the `Reset password` button on `Overview` page.

Note: Make sure you have created a [server-level firewall rule](https://docs.microsoft.com/en-us/azure/postgresql/quickstart-create-server-database-portal#configure-a-server-level-firewall-rule) to allow traffic from the IP address of the machine you will be using to connect to the database. If you are connected to a remote machine via SSH, you can find your current IP address via the terminal using `dig +short myip.opendns.com @resolver1.opendns.com`.

## Creating Schema and Data Distribution on Citus

As we are now able to connect to the Hyperscale(Citus) server, let us move forward and define the table structure. For this lab, we will use a small sample of Covid-19 time-series data for UK and try to get some insights on the vaccination drive.

You can create the tables by using standard PostgreSQL CREATE TABLE commands as shown below:

```sql
-- re-initializing database
DROP OWNED BY citus;

CREATE SCHEMA IF NOT EXISTS covid19;

CREATE TABLE covid19.area_reference
(
    id integer NOT NULL DEFAULT nextval('area_reference_id_seq'::regclass),
    area_type character varying(15) COLLATE pg_catalog."default" NOT NULL,
    area_code character varying(12) COLLATE pg_catalog."default" NOT NULL,
    area_name character varying(120) COLLATE pg_catalog."default" NOT NULL,
    unique_ref character varying(26) COLLATE pg_catalog."default" NOT NULL DEFAULT "substring"(((now())::character varying)::text, 0, 26),
    CONSTRAINT area_reference_pkey PRIMARY KEY (area_type, area_code),
    CONSTRAINT area_reference_id_key UNIQUE (id),
    CONSTRAINT unq_area_reference_ref UNIQUE (unique_ref)
);


CREATE TABLE covid19.metric_reference
(
    id integer NOT NULL DEFAULT nextval('metric_reference_id_seq'::regclass),
    metric character varying(120) COLLATE pg_catalog."default" NOT NULL,
    released boolean NOT NULL DEFAULT false,
    metric_name character varying(150) COLLATE pg_catalog."default",
    source_metric boolean NOT NULL DEFAULT false,
    CONSTRAINT metric_reference_pkey PRIMARY KEY (id),
    CONSTRAINT metric_reference_metric_key UNIQUE (metric)
);


CREATE TABLE covid19.release_reference
(
    id integer NOT NULL DEFAULT nextval('release_reference_id_seq'::regclass),
    "timestamp" timestamp without time zone NOT NULL,
    released boolean NOT NULL DEFAULT false,
    CONSTRAINT release_reference_pkey PRIMARY KEY (id),
    CONSTRAINT release_reference_timestamp_key UNIQUE ("timestamp")
);


CREATE TABLE covid19.time_series
(
    hash character varying(24) COLLATE pg_catalog."default" NOT NULL,
    partition_id character varying(26) COLLATE pg_catalog."default" NOT NULL,
    release_id integer NOT NULL,
    area_id integer NOT NULL,
    metric_id integer NOT NULL,
    date date NOT NULL,
    payload jsonb DEFAULT '{"value": null}'::jsonb
) PARTITION BY LIST (date) ;

-- Partitions SQL

CREATE TABLE covid19.time_series_250421 OF covid19.time_series
    FOR VALUES IN ('2021-04-25');

CREATE TABLE covid19.time_series_260421 OF covid19.time_series
    FOR VALUES IN ('2021-04-26');

CREATE TABLE covid19.time_series_270421 OF covid19.time_series
    FOR VALUES IN ('2021-04-27');

CREATE TABLE covid19.time_series_280421 OF covid19.time_series
    FOR VALUES IN ('2021-04-28');

CREATE TABLE covid19.time_series_290421 OF covid19.time_series
    FOR VALUES IN ('2021-04-29');
    
CREATE TABLE covid19.time_series_300421 OF covid19.time_series
    FOR VALUES IN ('2021-04-30');

```
Now that the schema is ready, we can focus on deciding the right distribution starategy to shard tables accross nodes on Citus cluster to gain maximum performance.

| Sr. | Table Type        | Description |
|-----|-------------------|-------------|
| 1   | Distributed Table | Tables horizontally partitioned across worker nodes.Helps in scaling and parallelism. |
| 2   | Reference Table   | Tables that are replicated on each node. Generally, tables which are smaller in size but are used frequently in JOINs|
| 3   | Local Table       | Tables that stays on coordinator node. Generally, the ones with no dependencies or JOINS. |


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


The `payload` field of `time_series` has a JSONB datatype. JSONB is the JSON datatype in binary form in Postgres. The datatype makes it easy to store a flexible schema in a single column.

Postgres can create a `GIN` index on this type, which will index every key and value within it. With an index, it becomes fast and easy to query the payload with various conditions. Let's go ahead and create a couple of indexes before we load our data. In psql:




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

As you can see, we've got perfectly normal SQL running in a distributed environment with no changes to our actual queries. This is a very powerful tool for scaling PostgreSQL to any size you need without dealing with the traditional complexity of distributed systems.

## Next steps (Optional)

You have successfully completed this lab. If you are interested in learning about advanced functionality, you can continue to the [Rolling up data](README-ADVANCED.md#Rolling-up-data) section in the [Advanced](README-ADVANCED.md#Rolling-up-data) version of this lab, or refer to our [Quickstart](https://docs.microsoft.com/azure/postgresql/quickstart-create-hyperscale-portal#create-an-azure-database-for-postgresql---hyperscale-citus) documentation in the future to create your own database.
