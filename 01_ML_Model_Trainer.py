# Databricks notebook source
# MAGIC %md
# MAGIC ### Generate sample data to be used throughout the rest of the notebook
# MAGIC 
# MAGIC This solution accelerator will focus on deploying an ML Model built on Databricks to edge devices. To build an ML Model, we need a dataset that we can use to train the model. The next few cells will generate artificial "IoT/Sensor" data that we'll be used to train a Random Forest.

# COMMAND ----------

# Import all required libraries

from pyspark.sql.types import *
from pyspark.sql.functions import *
import mlflow.spark
import mlflow.sklearn

mlflow.spark.autolog()

spark.conf.set("spark.databricks.io.cache.enabled", True)

# COMMAND ----------

# MAGIC %md
# MAGIC Code below will create a synthetic Spark Dataframe with 10 million rows. Each row will contain randomly generated data from 5 sensors. The ML Model that will train below will attemp to predict the value of sensor 5 using the other 4 sensors as inputs to the model.

# COMMAND ----------

data_df = (spark.range(10000000)
    .select(col("id").alias("timestamp_id"), (col("id")%10).alias("device_id"))
    .withColumn("sensor1", rand() * 1)
    .withColumn("sensor2", rand() * 2)
    .withColumn("sensor3", rand() * 3)
    .withColumn("sensor4", rand() * 3)
    .withColumn("sensor5", (col("sensor1") + col("sensor2") + col("sensor3") + col("sensor4")) + rand())
)    

# COMMAND ----------

display(data_df)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Create training and test datasets
# MAGIC 
# MAGIC This solution accelerator is focused on the deployment of ML models at the edge and not on the process of building/training machine learning models. However, it is always a best practice to split up the input dataset into train and test datasets. The code below will split that up and will allocate 70% of the records to the training dataset to build the ML model and 30% to the testing dataset that can be used later to evaluate the performance of the model.

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
# MAGIC 
# MAGIC We will now create a Random Forest algorithm using the training dataset and track the whole experiment using MLFlow autologging capabilities.

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

# MAGIC %md
# MAGIC ### Register ML Model
# MAGIC 
# MAGIC Finally, we'll use the run_id of the model we just built to register that model into the MLFlow Registry. The edge devices can now download this model directly from MLFlow to run locally in those devices.

# COMMAND ----------

model_name = "sensor_model"
model_uri = "runs:/{run_id}/model".format(run_id=run_id)
model_details = mlflow.register_model(model_uri=model_uri, name=model_name)
