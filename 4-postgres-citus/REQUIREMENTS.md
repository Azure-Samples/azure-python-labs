# REQUIREMENTS

- Azure Subscription (e.g. [Free](https://aka.ms/azure-free-account) or [Student](https://aka.ms/azure-student-account))
- An **Azure Database for PostgreSQL-Hyperscale Server-Basic Tier** (Detailed steps are listed [here](https://docs.microsoft.com/en-us/azure/postgresql/quickstart-create-hyperscale-basic-tier)). For this lab, we will start with Azure Basic Tier- run queries & capture performance benchmarks and later scale it to Standard Tier to see the performance improvements introduced by horizantal scaling of nodes.
- You will also need [psql](https://www.postgresql.org/download/) (Ver 11 is recommended), which is included in [Azure Cloud Shell](https://docs.microsoft.com/en-ca/azure/cloud-shell/overview).
- [Optional] If you want you can also run Citus open source on your laptop as a single Docker container!
```ssh
# run PostgreSQL with Citus on port 5500
docker run -d --name citus -p 5500:5432 -e POSTGRES_PASSWORD=mypassword citusdata/citus
```


