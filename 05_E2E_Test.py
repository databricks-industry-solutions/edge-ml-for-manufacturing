# Databricks notebook source
import mlflow
from mlflow.tracking.client import MlflowClient

# COMMAND ----------

# MAGIC %run ./config/notebook_config

# COMMAND ----------

client = MlflowClient()

model_details = client.get_latest_versions(model_name)[0]

client.transition_model_version_stage(
  name=model_details.name,
  version=model_details.version,
  stage='Production',
  archive=True
)
