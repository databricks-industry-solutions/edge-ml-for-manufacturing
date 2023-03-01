# Databricks notebook source
from pyspark.sql.types import *
from pyspark.sql.functions import *
import mlflow.spark
import mlflow.sklearn

mlflow.spark.autolog()

spark.conf.set("spark.databricks.io.cache.enabled", True)

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

# MAGIC %md
# MAGIC 
# MAGIC ### Create training and test datasets

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

# MAGIC %md
# MAGIC 
# MAGIC ### Build a simple ML Random Forest model

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
