# Databricks notebook source
from pyspark.sql.types import *
from pyspark.sql.functions import *
import mlflow.spark
import mlflow.sklearn

mlflow.spark.autolog()

spark.conf.set("spark.databricks.io.cache.enabled", True)

# COMMAND ----------

# MAGIC %md Import Delta Data

# COMMAND ----------

dataDf = spark.table('mcdata.dltsensorstreambronze').orderBy('datetime').limit(10000)
display(dataDf)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Dynamically generate synthetic data to be used to build ML model

# COMMAND ----------

data_df = (spark.range(10000*1000)
    .select(col("id").alias("timestamp_id"), (col("id")%10).alias("device_id"))
    .withColumn("sensor1", rand() * 1)
    .withColumn("sensor2", rand() * 2)
    .withColumn("sensor3", rand() * 3)
    .withColumn("sensor4", rand() * 3)
    .withColumn("sensor5", (col("sensor1") + col("sensor2") + col("sensor3") + col("sensor4")) + rand())
)    

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Display a sample of the data that was generated

# COMMAND ----------

display(data_df)

# COMMAND ----------

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

df = data_df.toPandas()
  
x = df.drop(["timestamp_id", "device_id", "sensor5"], axis=1)
y = df[["sensor5"]]
train_x, test_x, train_y, test_y = train_test_split(x,y,test_size=0.30, random_state=30)

# COMMAND ----------

import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.ensemble import RandomForestRegressor

df = dataDf.drop('_rescued_data').dropna().toPandas()
  
x = df.drop(["datetime", "device", "sensor5"], axis=1)
y = df[["sensor5"]]
train_x, test_x, train_y, test_y = train_test_split(x,y,test_size=0.30, random_state=30)

# COMMAND ----------

# MAGIC %md Manual Loggging

# COMMAND ----------

maxDepth = 5
maxFeatures = 4
nEstimators = 10
criterion = "mse"

mlflow.sklearn.autolog(disable=True)
with mlflow.start_run(run_name = "skl_randfor_manual"):

 # Fit, train, and score the model
  model = RandomForestRegressor(max_depth = maxDepth, max_features = maxFeatures, n_estimators = nEstimators, criterion = criterion)
  model.fit(train_x, train_y)
  preds = model.predict(test_x)

  # Log Paramater
  mlflow.log_param("max_depth", maxDepth)
  mlflow.log_param("max_features", maxFeatures)
  mlflow.log_param("n_estimators", nEstimators)
  mlflow.log_param("criterion", criterion)

  # Log Model
  mlflow.sklearn.log_model(model, "model")

  # Get Metrics
  mse = mean_squared_error(test_y, preds)
  r2 = r2_score(test_y, preds)

  # Log Metrics
  mlflow.log_metric('training_mse', mse)
  mlflow.log_metric('training_r2_score', r2)

  mlflow.end_run()

# COMMAND ----------

# MAGIC %md Auto Logging

# COMMAND ----------

maxDepth = 5
maxFeatures = 4
nEstimators = 10
criterion = "mse"

mlflow.sklearn.autolog()
with mlflow.start_run(run_name = "skl_randfor_autolog"):
    
 # Fit, train, and score the model
  model = RandomForestRegressor(max_depth = maxDepth, max_features = maxFeatures, n_estimators = nEstimators, criterion = criterion)
  model.fit(train_x, train_y)
  preds = model.predict(test_x)
  run_id = mlflow.active_run().info.run_id

  mlflow.end_run()

# COMMAND ----------

# MAGIC %md Hyperparameter Tuning with HyperOpt

# COMMAND ----------

from hyperopt import fmin, tpe, hp, SparkTrials, Trials, STATUS_OK
from hyperopt.pyll import scope
import numpy as np

#Hyper-parameter search spark
search_space = {
    'max_depth': hp.choice('max_depth', range(1,20)),
    'max_features': hp.choice('max_features', range(1,4)),
    'n_estimators': hp.choice('n_estimators', range(1,20)),
    'criterion': hp.choice('criterion', ["mse", "mae"])
}

def train_model(params):
  mlflow.sklearn.autolog()
  with mlflow.start_run(nested=True):
        
   # Fit, train, and score the model
    model = RandomForestRegressor(**params)
    model.fit(train_x, train_y)
    preds = model.predict(test_x)

    return {'status': STATUS_OK, 'loss': mean_squared_error(test_y, preds)} #, 'params': model.get_params()}
  
with mlflow.start_run(run_name='skl_randfor_hyperopt'):
  best_params = fmin(
    fn = train_model,
    space = search_space,
    algo = tpe.suggest,
    max_evals = 10,
    trials = SparkTrials(5)
  )
