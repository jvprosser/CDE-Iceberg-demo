# CDE-Iceberg-demo
Using Wine quality dataset https://www.kaggle.com/datasets/yasserh/wine-quality-dataset

I split the file into two halves and put them into my home folder on S3
## PREP
1. Get on VPN
2. drop table default.jvp_icewine_test;
3. Get the jobs api url for this virtual cluster and update the vcluster-endpoint in ~/.cde/config.yaml
5. add an airflow connector to your hive VW and call it jvp-cde-hive-demo
6. Connection type = hive client wrapper, host = host from jdbc driver, login/password from workload account
7. install the cde CLI,
7. Create a CDE VC if needed, with Iceberg and session support
8. prewarm your hive VW


## CDE
3. Go to CDE HOME
4. talk about the UI
5. Show your VC and show the config and Iceberg support
**What is Apache Iceberg?**
>Apache Iceberg is a new open table format targeted for petabyte-scale analytic datasets. 

>Developers love it because it supports ACID transactions, Time Travel, Rollback, and in-place schema evolution.

>Architects love it because it supports streaming and batch ingestion, multi-and hybrid cloud deployments, it's open source, and also engine agnostic.

7. Go to the sessions and start one up and name it Fanatics-demo
8. Once it comes up:
9. go to the CLI and enter ` ./cde session interact --name Fanatics-demo`
10. then go the the interact tab
11. Paste this code in a session: 

`tablename = 'jvp_icewine_test'
df = spark.read.options(header='True', inferSchema='True', delimiter=',') \
  .csv("s3a://go01-demo/user/jprosser/winedata/wine-quality-1.csv")
  
df.printSchema()

df.writeTo(tablename)\
     .tableProperty("write.format.default", "orc")\
     .using("iceberg")\
     .create()
     
spark.sql(f"SELECT * FROM {tablename}").show(10)

print ("Getting row count")

spark.sql(f"SELECT count(*) FROM {tablename}").show(10)
`


7. Go back to interact and paste this code:

`spark.sql(f"SELECT * FROM default.{tablename}.snapshots").show()`

Talk about this being an iceberg table and that we have our first snapshot!

6. Create a job by uploading pyspark_sql_iceberg.py and run it
8. While its running, go look at the resource that was created containing the file. Talk about resources

## Airflow
1. Click on jobs and describe the UI
2. Create an AIRFLOW job and give it a name and select editor
3. Drag a shell script over and click on the title to change it from script_1 to Check Env - `echo "starting ETL JOB!"`
4. Drag a CDE job over and point to our recently created pyspark job
5. Connect the shell script to the cde job
6. Drag a CDW query over and paste 'select count(*) from default.jvp_icewine_test' ALSO make sure to add the VW connection 'jvp-cdw-hive-demo'
7. Connect the CDE job to the CDW query
8. Run the job and look at the results.

## CDW & Iceberg table management
1. go back to the session and show the snapshots again.
3. now go to CDW and talk about it, show visualization
4. Go into a Hive Warehouse HUE session and select count(*)
5. 'select count(*) from default.jvp_icewine_test'
6. Select the snapshots again and point out that the last 2 snapshots are duplicates since we ran the pyspark job twice
7. result should be 7347
'SELECT * FROM default.jvp_icewine_test.snapshots;'
6. Alter the table to go back one snapshot
'ALTER TABLE default.jvp_icewine_test EXECUTE ROLLBACK(PUT_YOUR_SNAPSHOT_HERE); '

7. Now result should be 4898
'select count(*) from default.jvp_icewine_test'

## CML
1. Create a project with this git
2. in another tab, start the DataViz app (it takes a bit to run.)
3. Start a session with extra CPU and RAM to run a python notebook.
4. Load the EDA notebook and step through most of it.
5. Start another session and load wine_train.py
6. Start a terminal and execute `bash -x setup.sh`
7. GO and get the first snapshot ID from HUE and put it in the file at the top
8. step through the sections of the file executing in chunks.
9. note that we are loading the same data but from an even earlier snapshot, because we always want to train from a known dataset.
10. Run the files 2 or 3 more times.
11. go and look at the experiments. Compare them.
12. Mention that you won't deploy a model at this point, but can schedule a followup for later.

## Viz
1. If there's time, go to the data tab you opened earlier.
2. go to Datasets
3. select 'default-hive-data'
4. click New Dataset ( from table - default - jvp_icewine_test )
5. click on Fields - edit fields
6. convert some of the measures to dimensions - density, ph, alcohol, quality
7. click new dashboard on the right.
