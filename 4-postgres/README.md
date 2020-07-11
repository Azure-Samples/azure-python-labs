# Explore Azure Database for PostgreSQL with Python

In this lab, you will learn how to import data into an Azure Database for PostgreSQL instance using a python script and the `psycopg2` module. Once the data is loaded, you will be exploring a dataset meant to simulate an "IoT", or Internet of Things, use case. This dataset contains simulated weather data from weather sensors in cities across the world.

To store this dataset, we have tables containing geospatial information stored using Postgres's [PostGIS data type](https://postgis.net/) as well as JSON content stored in Postgres's [jsonb datatype](https://www.postgresql.org/docs/11/functions-json.html). We are accessing the data using functions built into a python script provided as part of this lab. The script relies on `psycopg2` to connect to Postgres and load or fetch data.  



## Prerequisites
- Azure Subscription (e.g. [Free](https://aka.ms/azure-free-account) or [Student](https://aka.ms/azure-student-account))
- An Azure Database for PostgreSQL (Create via [Portal](https://docs.microsoft.com/en-us/azure/postgresql/quickstart-create-server-database-portal) or [Azure CLI](https://docs.microsoft.com/en-us/azure/postgresql/quickstart-create-server-database-azure-cli)) 
- [Python](https://www.python.org/downloads/) 3.4+
- Latest [pip](https://pip.pypa.io/en/stable/installing/) package installer

## Install the Python libraries for PostgreSQL
The [psycopg2](https://pypi.python.org/pypi/psycopg2/) module enables connecting to and querying a PostgreSQL database, and is available as a Linux, macOS, or Windows [wheel](https://pythonwheels.com/) package. Install the binary version of the module, including all the dependencies. For more information about `psycopg2` installation and requirements, see [Installation](http://initd.org/psycopg/docs/install.html). 

To install `psycopg2`, open a terminal or command prompt and run the command `pip install psycopg2`.

We will also install `fire`, required by our CLI tool, `pg-lab.py`, by running the command `pip install fire`.


## Get database connection information

Connecting to an Azure Database for PostgreSQL database requires the fully qualified server name and login credentials. You can get this information from the Azure portal.

1. In the [Azure portal](https://portal.azure.com/), search for and select your Azure Database for PostgreSQL server name. 
1. On the server's **Overview** page, copy the fully qualified **Server name** and the **Admin username**. The fully qualified **Server name** is always of the form *\<my-server-name>.postgres.database.azure.com*, and the **Admin username** is always of the form *\<my-admin-username>@\<my-server-name>*. 
1. You will also need your **Admin password** which you chose when you created the server, otherwise you can reset it using the `Reset password` button.

Note: make sure you have created a [server-level firewall rule](https://docs.microsoft.com/en-us/azure/postgresql/quickstart-create-server-database-portal#configure-a-server-level-firewall-rule) to allow traffic from the IP address of the machine you will be using to connect to the database. If you are connected to a remote machine via SSH, you can find your current IP address via the terminal using `dig +short myip.opendns.com @resolver1.opendns.com`.

## How to run the Python examples

1. First, we need to get the script [pg-lab.py](pg-lab.py), as well as [data.csv](data.csv) onto our local machine. You may download them manually, or `git clone` this repository and `cd` into the correct `4-postgres/` directory as follows:

   ```
   git clone https://github.com/Azure-Samples/azure-python-labs.git
   cd azure-python-labs/4-postgres/
   ```

1. Then, we need to set up the Postgres connection we're going to be using for the rest of this lab. The following script writes the connection string to a .config file in the current directory via the [writeConfig](pg-lab.py#L5) function. To run this, set some environment variables which we use to create the connection string from the values :

    ```
    export SERVER_NAME='pg200700.postgres.database.azure.com'
    export ADMIN_USERNAME='myadmin@pg200700'
    export ADMIN_PASSWORD='...'
    python3 pg-lab.py writeConfig "host=${SERVER_NAME} port=5432 dbname=postgres user=${ADMIN_USERNAME} password=${ADMIN_PASSWORD} sslmode=require"
    ```

1. Next, let's create a table and load some data from a local CSV file, [data.csv](data.csv). The [loadData](pg-lab.py#L27) function of the lab script will automatically connect to the database, create our tables if they don't exist, and then use a COPY command to load our data into the `raw_data` table from `data.csv`. All we need to do is invoke that function with the name of the data file. 

    ```
    python3 pg-lab.py loadData data.csv
    ```

1. Now that the data is loaded, let's look at a sample of the data to see what we're working with. [pg-lab.py](pg-lab.py) has a few functions built in to process data and give us some results, so to keep things simple let's start with [getAverageTemperatures](pg-lab.py#L77). This function automatically pulls data, loads it into a dict for processing, and gives us average temperartures per location. This is a very inefficient function, so you'll probably notice that it is slow. 

    ```
    python3 pg-lab.py getAverageTemperatures
    ```

1. We're going to be using geospatial data for the next part of this lab, so to prepare for that let's add a geospatial index to speed things up in advance. PostGIS can use [GIST indexes](https://postgis.net/workshops/postgis-intro/indexing.html) to make spatial lookups much faster, so if we create an index and specify the [GIST type](https://www.postgresql.org/docs/current/textsearch-indexes.html), we'll get great results. To make this easier, [pg-lab.py](pg-lab.py) has a built-in [runSQL](pg-lab.py#L70) function to run arbitrary SQL for this lab.

    ```
    python3 pg-lab.py runSQL "CREATE INDEX idx_raw_data_1 ON raw_data USING GIST (location);"
    ```

1. There's one more thing we need to do before we can run all of the queries we want to. Right now, we've only got data in our `raw_data` table, and it has a record for every device and every minute. This means that, if we just want to look up basic information such as what city a device is in, we've got to query a big table, which can be slow. To fix this, [pg-lab.py](pg-lab.py) has a [populateDevices](pg-lab.py#L20) function that will perform an `INSERT INTO SELECT` to automatically populate the `device_list` table with summary information on our devices. Creating aggregate or summary tables like this is an excellent way to speed up application performance!

    ```
    python3 pg-lab.py populateDevices
    ```

1. Now that we've got our database ready to go, let's start using our application. For this part of the lab, we're going to figure out what the average device was at the nearest sensor to a location of our choice. We'll start by picking any city that you like, anywhere in the world, and doing a Bing search for the city and the word "coordinates". For example, if you'd want to see temperature data for Lima, Peru, you'd get to [this result page](https://www.bing.com/search?q=Lima%2C+Peru+coordinates), where we get a latitude and longitude of -12.057977° N, -77.03713° E. Now that we've got some coordinates to test with, we'll find the nearest device so we can get suitable information. The [getNearestDevice](pg-lab.py#L55) function will query our new `device_list` table using the `ST_Distance` PostGIS function to figure out what the closest device is. 


    ```
    python3 pg-lab.py getNearestDevice -12.057977 -77.03713
    ```

1. Now that we've found the device, we can get the average temperature of that device from our raw_data table using the [getDeviceAverage](pg-lab.py#L63) function. Unlike the inefficient query from step 3, we're having Postgres generate the average for us. This is a huge improvement in performance, as we need to move much less data over the network and Postgres is very well optimized to run analtyical queries.  

    ```
    python3 pg-lab.py getDeviceAverage 5
    ```


Bonus objective: [getAverageTemperatures](pg-lab.py#L77) pulls a lot of data it doesn't need to. Rewrite it to do the average calculation in pure SQL instead!

## (Optional) Delete your Azure Database for PostgreSQL

If you have created an Azure Database for PostgreSQL for the purposes of this lab and you *do not* want to keep and continue to be billed for it, you can delete it via the Azure Portal (see: [delete resources](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/manage-resources-portal#delete-resources)).
