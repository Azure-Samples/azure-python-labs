1. First, set up connection
python3 lab_script.py writeConfig "host=coshepar-lab.postgres.database.azure.com port=5432 dbname=postgres user=lab@coshepar-lab password=password sslmode=require"

2. Next, let's create a table and load some data
python3 lab_script.py loadData data.csv

3. Let's look at our average temperatures:

python3 lab_script.py getAverageTemperatures

4. Add an index to make one of the queries faster. Do this through PSQL?

python3 lab_script.py runSQL "CREATE INDEX idx_raw_data_1 ON raw_data USING GIST (location);"

5. Run this to populate the "devices" table:

python3 lab_script.py populateDevices

5. Pick a city and Bing search to get its coordinates, find the nearest device, and get average temperature for it. 

Find closest device:

python3 lab_script.py getNearestDevice 47.7 122.03

Get  the average temperature of that device:

python3 lab_script.py getDeviceAverage 5


TODO: add more city data


6. Something clever with json to dict?


Bonus: Add code to detect whether the data is in Fahrenheit or Celsius. 
