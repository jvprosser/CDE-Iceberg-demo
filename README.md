# CDE-Iceberg-demo
Using the open source Wine quality dataset https://www.kaggle.com/datasets/yasserh/wine-quality-dataset

>Thanks to Sujith K Mandala for the wine-quality-analysis-eda notebook.

I split the file into two halves and put them into an S3 folder.

## PREP
1. Clone this repo and update parameters.conf

2. Replace WWW and my-sandbox01 with your prefix and datalake in the source files and README
    `sed -i '.bak' -e 's/ZZZ/WWW/g' -e 's/BUCKET/my-sandbox01/g' *.py *.md *.conf`
4. Drop table if exists default.ZZZ_winedata;
5. Copy/upload the 2 csv files to s3a://BUCKET/tmp
6. Create a CDE VC if needed, with Spark3, Iceberg and Session support
7. Add an airflow connector to your CDE VC for your CDW Hive VW and call it cdw-hive-demo

`   Connection type = hive client wrapper, host = host from jdbc conn string, login/password from workload account`

6. Install the cde CLI if needed,
7. If you see `Error: error in Session endpoint healthcheck <html>` when you test the cde command line, it means you need to
8. Get the jobs api url for this virtual cluster and update the vcluster-endpoint in ~/.cde/config.yaml
9. Prewarm your hive VW
10. Make sure your CML workspace has model registry enabled!



## CDE
3. Go to CDE HOME
4. talk about the UI
5. Go to the sessions and start one up and name it ZZZ-demo
6. While that is starting,
7. Go bacl to Home and show the details of your VC  e.g. config and Iceberg support
**What is Apache Iceberg?**
>Apache Iceberg is a new open table format targeted for petabyte-scale analytic datasets.

>Developers love it because it supports ACID transactions, Time Travel, Rollback, and in-place schema evolution. Keep in mind that "ACID" is datalake ACID not OLTP ACID - for rapid row updates use Kudu


>Architects love it because it supports streaming and batch ingestion, multi-and hybrid cloud deployments, it's open source, and also engine agnostic.

7. Go to the sessions and start one up and name it ZZZ-demo
8. Once it comes up:
9. go to the CLI and enter ` ./cde session interact --name ZZZ-demo`
10. enter a trivial python command like `2+2`
11. then go the the interact tab and you should see this activity there as well.
12. Paste this code in a session:

```
tablename = 'ZZZ_winedata'

df = spark.read.options(header='True', inferSchema='True', delimiter=',').csv("s3a://BUCKET/tmp/wine-quality-1.csv")

df.printSchema()
```

```
df.writeTo(tablename).tableProperty("write.format.default", "parquet").tableProperty("format-version" , "2").using("iceberg").createOrReplace()
spark.sql(f"SELECT * FROM {tablename}").show(10)

print ("Getting row count")
spark.sql(f"SELECT count(*) FROM {tablename}").show(10)
```


7. Go back to interact and paste this code:

```
spark.sql(f"SELECT * FROM default.{tablename}.history").show()

spark.sql(f"SELECT * FROM default.{tablename}.snapshots").show()
```


Talk about this being an iceberg table and that we have our first snapshot!

>Now that we have our code working, let's put it in a job and run it that way!

## Job
1. Show that the code for CDE_pyspark_sql_iceberg.py is just like what we ran in the session but there's some session setup and the data file is different.
2. Create a file-based Spark3 job by uploading CDE_pyspark_sql_iceberg.py, creating a resource called ZZZ-Resource and save+run it.
3. Go to the jobs page and describe it.
4. Go to job runs and describe the page
5. Go to resources, look at was created for the job. Talk about resources.
6. go back to job runs and look at logs, SparkUI, etc

> Now that our job is working let's start to operationalize it with Airflow!

## Airflow
1. Click on jobs and create an AIRFLOW job and give it a name and select editor, then click the 'Create' button.
2. Select 'Editor' from the menubar.
3. Drag a shell script over and click on the title to change it from script_1 to Check Env - `echo "starting ETL JOB!"`
4. Drag a CDE job over and point to our recently created pyspark job
5. Connect the shell script to the cde job
6. Drag a CDW query over and paste 'select count(*) from default.ZZZ_winedata' ALSO make sure to add the VW connection 'cdw-hive-demo'
7. Connect the CDE job to the CDW query
8. Start the job and look at the job run for it.
9. Go to the Airflow UI and drill in
10. Go to Logs and drill in, show log for each DAG task.

## Iceberg table management and CDW
1. Go back to the session and show the snapshots again.
3. Now go to CDW and talk about it, show visualization
4. Go into a Hive Warehouse HUE session and get the row count

`SELECT COUNT(*) FROM default.ZZZ_winedata;`

6. Select the snapshots again and point out that the last 2 snapshots are duplicates since we ran the pyspark job twice:


```
SELECT * FROM default.ZZZ_winedata.history;

SELECT * FROM default.ZZZ_winedata.snapshots;
```

8. The result should be 7347, which is more than desired.

6. Alter the table to go back one snapshot

`ALTER TABLE default.ZZZ_winedata EXECUTE ROLLBACK(PUT_YOUR_SNAPSHOT_HERE); `

7. Now result should be 4898 from
`select count(*) from default.ZZZ_winedata`

## CML  This demo shows MLFlow. while it works in the demo AWS env it is not GA.
1. Create a project with this git and upload parameters.conf.
2. Start a JupiterLab session with extra CPU and RAM
3. Start a terminal and execute `bash -x setup.sh`.
4. ( If this is a git branch, execute `git checkout <branchname>` )
5. Load the EDA notebook and step through most of it.
6. Start another session with a workbench running Spark3
7. Get the first snapshot ID from HUE and assign it to `first_snapshot` at the top
>I'm using the first snapshot because I always want to train the model using the same dataset.  In Q4, there will be support for Iceberg Tags and Branching, which can be used to attach meaningful labels these snapshots.
8. Confirm that the CONNECTION_NAME variable matches the *Spark Data Lake*  Data "Connection Code Snippet" element.
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

```
{
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
