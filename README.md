# CDE-Iceberg-demo
Using the open source Wine quality dataset https://www.kaggle.com/datasets/yasserh/wine-quality-dataset

>Thanks to Sujith K Mandala for the wine-quality-analysis-eda notebook.

I split the file into two halves and put them into an S3 folder.

## PREP
1. Clone this repo and replace ZZZ with your namespace in this file, CDE_pyspark_sql_iceberg.py, and wine_train.py
2. replace BUCKET with your datalake. i.e. `sed -i '.bak' -e 's/ZZZ/WWW/g' -e 's/BUCKET/my-sandbox01/g' *.py *.md`
3. Drop table if exists default.ZZZ_winedata;
4. Get the jobs api url for this virtual cluster and update the vcluster-endpoint in ~/.cde/config.yaml
5. Create a CDE VC if needed, with Spark3, Iceberg and session support
6. Add an airflow connector to your CDE VC for your CDW Hive VW and call it cdw-hive-demo

`   Connection type = hive client wrapper, host = host from jdbc driver, login/password from workload account`

6. Install the cde CLI if needed,
7. Prewarm your hive VW


## CDE
3. Go to CDE HOME
4. talk about the UI
5. Show your VC and show the config and Iceberg support
**What is Apache Iceberg?**
>Apache Iceberg is a new open table format targeted for petabyte-scale analytic datasets. 

>Developers love it because it supports ACID transactions, Time Travel, Rollback, and in-place schema evolution.

>Architects love it because it supports streaming and batch ingestion, multi-and hybrid cloud deployments, it's open source, and also engine agnostic.

7. Go to the sessions and start one up and name it ZZZ-demo
8. Once it comes up:
9. go to the CLI and enter ` ./cde session interact --name ZZZ-demo`
10. then go the the interact tab
11. Paste this code in a session: 

```
tablename = 'ZZZ_winedata'

df = spark.read.options(header='True', inferSchema='True', delimiter=',').csv("s3a://BUCKET/tmp/wine-quality-1.csv")
  
df.printSchema()
```

```
df.writeTo(tablename).tableProperty("write.format.default", "orc").using("iceberg").createOrReplace()   
spark.sql(f"SELECT * FROM {tablename}").show(10)

print ("Getting row count")
spark.sql(f"SELECT count(*) FROM {tablename}").show(10)
```


7. Go back to interact and paste this code:

`spark.sql(f"SELECT * FROM default.{tablename}.snapshots").show()`

Talk about this being an iceberg table and that we have our first snapshot!

>Now that we have our code working, let's put it in a job and run it that way!

## Job
1. Show that the code for pyspark_sql_iceberg.py is just like what we ran in the session but there's some session setup and the data file is different.
2. Go to the jobs page and describe it.
3. Create a job by uploading CDE_pyspark_sql_iceberg.py and save+run it.
4. Go to job runs and describe the page
5. Go to resources, look at was created for the job. Talk about resources. 
6. go back to job runs and look at logs, SparkUI, etc

> Now that our job is working let's start to operationalize it with Airflow!

## Airflow
1. Click on jobs and describe the UI
2. Create an AIRFLOW job and give it a name and select editor
3. Drag a shell script over and click on the title to change it from script_1 to Check Env - `echo "starting ETL JOB!"`
4. Drag a CDE job over and point to our recently created pyspark job
5. Connect the shell script to the cde job
6. Drag a CDW query over and paste 'select count(*) from default.ZZZ_winedata' ALSO make sure to add the VW connection 'cdw-hive-demo'
7. Connect the CDE job to the CDW query
8. Start the job and look at the job run for it.
9. Go to the Airflow UI and drill in
10. Go to Logs and drill in, show log for each DAG task.

## Iceberg table management and CDW
1. go back to the session and show the snapshots again.
3. now go to CDW and talk about it, show visualization
4. Go into a Hive Warehouse HUE session and select count(*)
5. 'select count(*) from default.ZZZ_winedata'
6. Select the snapshots again and point out that the last 2 snapshots are duplicates since we ran the pyspark job twice:

`SELECT * FROM default.ZZZ_winedata.snapshots;`

8. result should be 7347

6. Alter the table to go back one snapshot

`ALTER TABLE default.ZZZ_winedata EXECUTE ROLLBACK(PUT_YOUR_SNAPSHOT_HERE); `

7. Now result should be 4898
'select count(*) from default.ZZZ_winedata'

## CML  This demo shows MLFlow. while it works in the demo AWS env it is not GA.
1. Create a project with this git
2. Start a JupiterLab session with extra CPU and RAM 
3. Start a terminal and execute `bash -x setup.sh`. - This takes longer than is desireable....
4. ( If this is a git branch, execute `git checkout <branchname>` )
5. Load the EDA notebook and step through most of it.
6. Start another session with a workbench running Spark3
7. Get the first snapshot ID from HUE and assign it to `first_snapshot` at the top
>I'm using the first snapshot because I always want to train the model using the same dataset
8. Confirm that the CONNECTION_NAME variable matches the correct Data "Connection Code Snippet" element.
9. Step through the sections of the file executing in chunks.
10. Note that we are loading the same data but from an even earlier snapshot, because we always want to train from a known dataset.
11. Run the code 2 or 3 more times to generate more experiment data. The hyperparameters are randomly generated.
12. Look at the experiments.
13. Check two experiments and click the Compare button on the right.
14. Look at the plots, zoom in
16. Pick one and scroll down to artifacts
17. Click on model, discuss
18. Click *Register Model* button and fill in the form. Pick a suitable name.
19. Click on Model Deployments, discuss, click on *New Model*
20. Select *Deploy registered model*
21. in the *Registered Model* field, select the model name from above.
22. uncheck *Enable Authentication*

>Note: MLFlow uses pandas JSON format and so the example input needs to be in the format below:

Enter Example Input

```{
  "columns": [
    "alcohol",
    "chlorides",
    "citric acid",
    "density",
    "fixed acidity",
    "free sulfur dioxide",
    "pH",
    "residual sugar",
    "sulphates",
    "total sulfur dioxide",
    "volatile acidity"
  ],
  "data": [
    [
      12.8,
      0.029,
      0.48,
      0.98,
      6.2,
      29,
      3.33,
      1.2,
      0.39,
      75,
      0.66
    ]
  ]
}
```

And Sample Response:

`{    "quality": 6 }`

23. Click *Deploy*
24. Once deployment completes, click on the model, discuss [ The monitoring tab is showing errors, so don't click on it! ]
26. Click on *Test* button at bottom.
27. Talk about how to access this as a REST endpoint or set up an Application around it.


## Viz
1. If there's time, go to the data tab you opened earlier.
2. go to Datasets
3. select 'default-hive-data'
4. click New Dataset ( from table - default - ZZZ_winedata )
5. click on Fields - edit fields
6. convert some of the measures to dimensions - density, ph, alcohol, quality
7. click new dashboard on the right.
