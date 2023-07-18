# The data set used in this example is from http://archive.ics.uci.edu/ml/datasets/Wine+Quality
# P. Cortez, A. Cerdeira, F. Almeida, T. Matos and J. Reis.
# Modeling wine preferences by data mining from physicochemical properties. In Decision Support Systems, Elsevier, 47(4):547-553, 2009.


#!pip install pandas numpy scikit-learn
#!mkdir data
#!touch data/features.txt

import os
import warnings
import sys
from numpy.random import default_rng

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet

import mlflow
import mlflow.sklearn
import configparser

config = configparser.ConfigParser()
config.read('./parameters.conf')

data_lake_name =config.get("general","data_lake_name")
s3BucketName   =config.get("general","s3BucketName")
tablename      =config.get("general","tablename")
expname        =config.get("general","CMLExperimentName")

CONNECTION_NAME = "<get Spark Data Lake connector name  from 'data' button in CML>"
first_snapshot=<GET THIS FROM CDW>

import cml.data_v1 as cmldata

def eval_metrics(actual, pred):
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return rmse, mae, r2



if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    np.random.seed(40)

    import cml.data_v1 as cmldata
    conn = cmldata.get_connection(CONNECTION_NAME)
    spark = conn.get_spark_session()

    # Sample usage to run query through spark
    EXAMPLE_SQL_QUERY = "show databases"
    spark.sql(EXAMPLE_SQL_QUERY).show()

    #spark.sparkContext.getConf().getAll()

    # get a snapshot so we always train with the same data
    data = spark.read\
    .option("snapshot-id", first_snapshot)\
    .format("iceberg")\
    .load(f"default.{tablename}").toPandas()
    # show the number of rows - should be 2449
    data.shape[0]
    # Split the data into training and test sets. (0.75, 0.25) split.
    train, test = train_test_split(data)

    # The predicted column is "quality" which is a scalar from [3, 9]
    train_x = train.drop(["quality"], axis=1)
    test_x = test.drop(["quality"], axis=1)
    train_y = train[["quality"]]
    test_y = test[["quality"]]

    rng = default_rng()

    alpha = rng.random()
    l1_ratio = rng.random()
    mlflow.set_experiment(expname)
    with mlflow.start_run():
        lr = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=42)
        lr.fit(train_x, train_y)

        predicted_qualities = lr.predict(test_x)

        (rmse, mae, r2) = eval_metrics(test_y, predicted_qualities)

        print("Elasticnet model (alpha=%f, l1_ratio=%f):" % (alpha, l1_ratio))
        print("  RMSE: %s" % rmse)
        print("  MAE: %s" % mae)
        print("  R2: %s" % r2)
        
        mlflow.log_param("iceberg_snapshot",first_snapshot)
        mlflow.log_param("alpha", alpha)
        mlflow.log_param("l1_ratio", l1_ratio)
        mlflow.log_metric("rmse", rmse)
        mlflow.log_metric("r2", r2)
        mlflow.log_metric("mae", mae)

        mlflow.sklearn.log_model(lr, "model")
        with open("data/features.txt", 'w+') as f:
          f.write(train_x.to_string())
        # Writes all files in "data" to root artifact_uri/states
        mlflow.log_artifacts("data", artifact_path="states")
    ## Artifacts are stored in project directory under /home/cdsw/.experiments/<experiment_id>/<run_id>/artifacts
    mlflow.end_run()
