# Real Time Transactional and Analytical Processing on Azure Database for PostgreSQL - Hyperscale (Citus)

Azure Database for PostgreSQL is a fully managed database-as-a-service based on the open-source Postgres relational database engine. The Hyperscale (Citus) deployment option enables you to scale queries horizontally- across multiple machines, to serve applications that require greater scale and performance. Citus transforms Postgres into a distributed database with features like sharding, a distributed SQL engine, reference tables, and distributed tables. The combination of parallelism, keeping more data in memory, and higher I/O bandwidth can lead to significant performance improvements

With the latest release, Citus 10 is now available in preview on Azure Hyperscale(Citus) with new capabilities like Columnar Storage, sharding on a single node Postgres machine, Joins between Local PostgreSQL & Citus tables and much more.

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

**Note:** You can even run Citus on [Docker](https://docs.citusdata.com/en/v10.0/installation/single_node_docker.html). But please note that the docker image is intended to be used for development or testing purposes only and not for production workloads.

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

SET search_path='covid19';

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
) PARTITION BY RANGE (date) ;

CREATE INDEX time_series_metric_id_idx ON covid19.time_series_dist USING btree (metric_id ASC NULLS LAST);

-- Partitions SQL

CREATE TABLE covid19.time_series_250421_to_290421 OF covid19.time_series
    FOR VALUES FROM ('2021-04-25') TO ('2021-04-29');

CREATE TABLE covid19.time_series_300421_to_040521 OF covid19.time_series
    FOR VALUES FROM ('2021-04-30') TO ('2021-05-04');
```

Now that the schema is ready, we can focus on deciding the right distribution strategy to shard tables across nodes on Citus cluster and data ingestion. Below table describes the different types of table on Citus cluster:

| Sr. | Table Type        | Description |
|-----|-------------------|-------------|
| 1   | Distributed Table | Large tables that are horizontally partitioned across worker nodes.Helps in scaling and parallelism. |
| 2   | Reference Table   | Tables that are replicated on each node. Generally, tables which are smaller in size but are used frequently in JOINs|
| 3   | Local Table       | Tables that stays on coordinator node. Generally, the ones with no dependencies or JOINS. |

In our case `time_series` is the largest table that holds real time Covid19 data for various metrics across different areas in UK, and others are supporting tables with less data- which when joined with `time_series` helps in building useful analytics.


Next we’ll take these Postgres tables on the coordinator node and tell Hyperscale(Citus) to either distribute or replicate them across the workers. To do so, we’ll run a query for each table specifying the key to shard it on. In the current example we’ll shard `time_series` table on `area_id`, and make other three tables are reference tables to avoid cross shard operations.

```sql
SELECT create_distributed_table('time_series', 'area_id');

SELECT create_reference_table('area_reference');
SELECT create_reference_table('metric_reference');
SELECT create_reference_table('release_reference');
```

We're ready to load the data. In psql, shell out to download the files:

```sql
curl -O https://raw.githubusercontent.com/sudhanshuvishodia/azure-python-labs/patch-1/4-postgres-citus/data/area_reference.csv
curl -O https://raw.githubusercontent.com/sudhanshuvishodia/azure-python-labs/patch-1/4-postgres-citus/data/metric_reference.csv
curl -O https://raw.githubusercontent.com/sudhanshuvishodia/azure-python-labs/patch-1/4-postgres-citus/data/release_reference.csv
curl -O https://raw.githubusercontent.com/sudhanshuvishodia/azure-python-labs/patch-1/4-postgres-citus/data/time_seriesaa.csv
curl -O https://raw.githubusercontent.com/sudhanshuvishodia/azure-python-labs/patch-1/4-postgres-citus/data/time_seriesab.csv
curl -O https://raw.githubusercontent.com/sudhanshuvishodia/azure-python-labs/patch-1/4-postgres-citus/data/time_seriesac.csv
curl -O https://raw.githubusercontent.com/sudhanshuvishodia/azure-python-labs/patch-1/4-postgres-citus/data/time_seriesad.csv
```

Next, load the data from the files into the distributed tables:

```sql
\copy covid19.area_reference from 'area_reference.csv' WITH CSV
\copy covid19.metric_reference from 'metric_reference.csv' WITH CSV
\copy covid19.release_reference from 'release_reference.csv' WITH CSV
\copy covid19.time_series from 'time_seriesaa.csv' WITH CSV
\copy covid19.time_series from 'time_seriesab.csv' WITH CSV
\copy covid19.time_series from 'time_seriesac.csv' WITH CSV
\copy covid19.time_series from 'time_seriesad.csv' WITH CSV
```

## Running Queries

Now it's time for the fun part, actually running some queries. Let's start with a simple `count (*)` to see how much data we loaded:

```sql
SELECT count(*) from covid19.time_series;
```
Let us now check the storage space consumed by the partition that stores old data `time_series_250421_to_290421`:

```sql
select pg_size_pretty(citus_total_relation_size('time_series_250421_to_290421'));
```

That worked nicely. We'll come back to that sort of aggregation in a bit, but for now we will see the benefit that we get with Columnar storage introduced with Citus 10. We have partitioned `time_series` table into two- `time_series_250421_to_290421` for old data and `time_series_300421_to_040521` for more recent data. As data grows, you can compress your old partitions to save storage cost just by running below simple command:

```sql
SELECT alter_table_set_access_method('time_series_250421_to_290421', 'columnar');
```

Check the table size again post compression now. See the difference that **Columnar** brings in. If you noticed, relation `time_series` now has both columnar storage as well as row-based storage. This is what we call as `HTAP`- wherein the same database can be used for both analytical and transactional workloads.


