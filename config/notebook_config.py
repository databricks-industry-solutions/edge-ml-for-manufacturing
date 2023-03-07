# Databricks notebook source
# DBTITLE 1,Get access token from notebook environment
access_token = dbutils.notebook.entry_point.getDbutils().notebook().getContext().apiToken().getOrElse(None)
username = dbutils.notebook.entry_point.getDbutils().notebook().getContext().userName().getOrElse(None)

# COMMAND ----------

# DBTITLE 1,Define model names 
model_name = "sensor_model" 

# COMMAND ----------

# DBTITLE 1,Set mlflow experiment so that the logging steps works in jobs as well
import mlflow
mlflow.set_experiment('/Users/{}/edge_ml'.format(username))
