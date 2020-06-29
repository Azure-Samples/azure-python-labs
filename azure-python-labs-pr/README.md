# Explore Azure Database for PostgreSQL with Python

In this lab, you will learn how to import data into an Azure Database for PostgreSQL instance using a python script and the `psycopg2` module.

## Prerequisites
- An Azure account with an active subscription. [Create an account for free](https://azure.microsoft.com/free/?ref=microsoft.com&utm_source=microsoft.com&utm_medium=docs&utm_campaign=visualstudio).
- [Python](https://www.python.org/downloads/) 2.7.9+ or 3.4+.
- Latest [pip](https://pip.pypa.io/en/stable/installing/) package installer.

## Install the Python libraries for PostgreSQL
The [psycopg2](https://pypi.python.org/pypi/psycopg2/) module enables connecting to and querying a PostgreSQL database, and is available as a Linux, macOS, or Windows [wheel](https://pythonwheels.com/) package. Install the binary version of the module, including all the dependencies. For more information about `psycopg2` installation and requirements, see [Installation](http://initd.org/psycopg/docs/install.html). 

To install `psycopg2`, open a terminal or command prompt and run the command `pip install psycopg2`.

We will also install `fire`, required by our CLI tool, `pg-lab.py`, by running the command `pip install fire`.


## Get database connection information
Connecting to an Azure Database for PostgreSQL database requires the fully qualified server name and login credentials. You can get this information from the Azure portal.

1. In the [Azure portal](https://portal.azure.com/), search for and select your Azure Database for PostgreSQL server name. 
1. On the server's **Overview** page, copy the fully qualified **Server name** and the **Admin username**. The fully qualified **Server name** is always of the form *\<my-server-name>.postgres.database.azure.com*, and the **Admin username** is always of the form *\<my-admin-username>@\<my-server-name>*. 

## How to run the Python examples

1. First, we need to set up the Postgres connection we're going to be using for the rest of this lab. The following script writes the connection string to a .config file in the current directory, so all we need to do is use the string from the previous step in the following argument:

```
python3 pg-lab.py writeConfig "host=postgis-lab.postgres.database.azure.com port=5432 dbname=postgres user=lab@coshepar-lab password=<password> sslmode=require"
```

2. Next, let's create a table and load some data. The loadData function of the lab script is designed to create all of our tables and then populate the raw_data table from the CSV provided, so all we need to do is invoke that function with the name of the data file. 

```bash
python3 pg-lab.py loadData data.csv
```

3. Let's look at the built-in getAverageTemperatures script to see what kind of data we're looking at:

```bash
python3 pg-lab.py getAverageTemperatures
```

4. Add an index to make one of the queries faster. We've got a runSQL command to run arbitrary SQL to make our lives easier

```
python3 pg-lab.py runSQL "CREATE INDEX idx_raw_data_1 ON raw_data USING GIST (location);"
```

5. Run this to populate the "devices" table:

```
python3 pg-lab.py populateDevices
```

5. Pick a city and Bing search to get its coordinates, find the nearest device, and get average temperature for it. 

Find closest device:

```
python3 pg-lab.py getNearestDevice 47.7 122.03
```

Get  the average temperature of that device:

```
python3 pg-lab.py getDeviceAverage 5
```



6. Something clever with json to dict?


Bonus: Add code to detect whether the data is in Fahrenheit or Celsius. 
Other bonus: getAverageTemperatures pulls a lot of data it doesn't need to. Rewrite it to do the average calculation in pure SQL instead!
