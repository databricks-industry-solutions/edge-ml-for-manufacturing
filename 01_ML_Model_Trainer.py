# Databricks notebook source
# MAGIC %md
# MAGIC 
# MAGIC ### Deploying and Maintaining Machine Learning Models on the “Edge” in Manufacturing
# MAGIC 
# MAGIC Edge computing is a computing paradigm that refers to devices that store, process data and make decisions very close to where that data is being generated. Edge computing has existed for a long time but the “Edge” has become more relevant over the last few years as more companies move their storage and compute capacity to the cloud but still have the need to keep some compute processing running on-premise to meet certain business or technical requirements. In manufacturing, it is very common to see local servers deployed at manufacturing sites that are used to collect and store data from various machines/sensors in a manufacturing plant and apply AI/ML models to incoming data to analyze patterns and anomalies in the data.
# MAGIC 
# MAGIC 
# MAGIC ### TODO add image from blog
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/edge_diagram.png?raw=true" />
# MAGIC      
# MAGIC The ML-optimized runtime in Databricks contains popular ML frameworks such as PyTorch, TensorFlow, and scikit-learn. We will build a basic Random Forest ML model in Databricks that will later be deployed to edge devices to execute inferences directly on the manufacturing floor. This solution accelerator will focus on deploying an ML Model built on Databricks to edge devices. 

# COMMAND ----------

# MAGIC %md
# MAGIC ### Generate sample data to be used throughout the rest of the notebook
# MAGIC 
# MAGIC Before data scientists can start working on building ML models, the first step in any data solution is to let the data engineers build reliable pipelines to ingest and transform the bronze (raw data) into the silver and gold datasets that can be used by downstream processes (see medallion architecture) and by data scientists that want to analyze and use the data to build ML models. The Delta Live Tables framework makes it very easy to build and manage these ETL pipelines. 
# MAGIC 
# MAGIC However, we will not discuss ETL or Delta Live Tables as we are only focusing on the actual deployment of ML models to the Edge. The next few cells will generate artificial "IoT/Sensor" data coming from machines located on the shop floor of a manufacturing plant. We'll then use that data to train a Random Forest that will be deployed to an edge device.

# COMMAND ----------

# Import all required libraries

from pyspark.sql.types import *
from pyspark.sql.functions import *
import mlflow.spark
import mlflow.sklearn
from mlflow.tracking.client import MlflowClient

# Turn on MLFLow's autologging of parameters from Spark
mlflow.spark.autolog()

# COMMAND ----------

# MAGIC %run ./config/notebook_config

# COMMAND ----------

# MAGIC %md
# MAGIC The code below will create a synthetic Spark Dataframe with 10 million rows. Each row will contain randomly generated data from 5 sensors. The ML Model that will train below will attempt to predict the value of sensor 5 using the other 4 sensors as inputs to the model.

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
# MAGIC It is always a best practice to split up the input dataset into train and test datasets. The code below will split that up and will allocate 70% of the records to the training dataset to build the ML model and 30% to the testing dataset that can be used later to evaluate the performance of the model. Keep in mind that this data was artificially generated and in a real-world environment there are better approaches to properly split time-series data. This Solution Accelearator is focused on ML Edge deployment and not on best practices for building/training ML models.

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

#Turn on MLFlow's autologging of parameters from scikit-learn 
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
# MAGIC 
# MAGIC In the Databricks UI, you should now see a new model registered on the “Models” page. As the model improves and evolves (with new data or better algorithms), new versions of the model can be created and they will be displayed on this page as well.

# COMMAND ----------

model_uri = "runs:/{run_id}/model".format(run_id=run_id)
model_details = mlflow.register_model(model_uri=model_uri, name=model_name)
