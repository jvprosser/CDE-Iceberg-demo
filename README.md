# CDE-Iceberg-demo
Using Wine quality dataset https://www.kaggle.com/datasets/yasserh/wine-quality-dataset

I split the file into two halves and put them into my home folder on S3

1. Go to CDE HOME
2. talk about the uI
3. Go to the sessions and start one up
4. Paste this code in a session

'tablename = 'jvp_icewine_test'

df = spark.read.options(header='True', inferSchema='True', delimiter=',') \
  .csv("s3a://go01-demo/user/jprosser/winedata/wine-quality-1.csv")

df.printSchema()

df.writeTo(tablename)\
     .tableProperty("write.format.default", "orc")\
     .using("iceberg")\
     .create()

spark.sql(f"SELECT * FROM {tablename}").show(10)

print ("Getting row count")

spark.sql(f"SELECT count(*) FROM {tablename}").show(10)'

5. paste this

'spark.sql(f"SELECT * FROM default.{tablename}.snapshots").show()'

and talk about this being an iceberg table and that we have our first snapshot.

6. Create a job by uploading pyspark_sql_iceberg.py and run it
7. While its running, go look at the resource that was created containing the file. Talk about resources

## Airflow
1. Click on jobs and describe the UI
2. Create an AIRFLOW job and give it a name and select editor
3. Drag a shell script over and click on the title to change it from script_1 to Check Env
4. Drag a CDE job over and point to our recently created pyspark job
5. Connect the shell script to the cde job
6. Drag a CDW query over and paste 'select count(*) from default.jvp_icewine_test' ALSO make sure to add the VW connection 'jvp-cdw-hive-demo'
7. Connect the CDE job to the CDW query
8. Run the job and look at the results.

## CDW & Iceberg table management
1. go back to the session and show the snapshots again.
2. now go to CDW and talk about it, show visualization
3. Go into a Hive Warehouse HUE session and select count(*)
4. 'select count(*) from default.jvp_icewine_test'
5. Select the snapshots again and point out that the last 2 snapshots are duplicates since we ran the pyspark job twice
6. result should be ~7k
'SELECT * FROM default.jvp_icewine_test.snapshots;'
6. Alter the table to go back one snapshot
'ALTER TABLE default.jvp_icewine_test EXECUTE ROLLBACK(PUT_YOUR_SNAPSHOT_HERE); '

7. Now result should be 4898
'select count(*) from default.jvp_icewine_test'

## CML
1. create a project with this git
2. run the prelim commands
