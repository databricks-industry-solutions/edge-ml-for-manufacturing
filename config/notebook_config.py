# Databricks notebook source
# DBTITLE 1,Get access info from notebook context
ctx = dbutils.notebook.entry_point.getDbutils().notebook().getContext()
access_token = ctx.apiToken().getOrElse(None)
databricks_token = access_token
databricks_host = ctx.apiUrl().getOrElse(None)

# COMMAND ----------

# DBTITLE 1,Define model names 
model_name = "sensor_model" 

# COMMAND ----------

# DBTITLE 1,Set mlflow experiment so that the logging steps works in jobs as well
import mlflow
username = ctx.userName().getOrElse(None)
experiment_path = '/Users/{}/edge_ml'.format(username)
mlflow.set_experiment(experiment_path)

# COMMAND ----------

print(f"Defined model_name, databricks_token, databricks_host.")

# COMMAND ----------


