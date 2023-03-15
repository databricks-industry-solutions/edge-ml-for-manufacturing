# Databricks notebook source
# MAGIC %md
# MAGIC One of the benefits of using MLflow is the model versioning capabilities that it provides. Every time a new run is registered to an existing model in MLflow, a new version of that model is automatically created. This allows ML engineers to track and monitor the performance of new model versions and compare that to older versions. If a new version performs better with new data being received, they can promote that version to “Production” and automatically push that through the CI/CD pipeline that deployed these models to the edge. The same applies to scenarios where a new model version is not performing as expected and we need to roll back to a previous working version of the model.
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/model_versions_mlflow.png?raw=true" />
# MAGIC 
# MAGIC 
# MAGIC In this solution accelerator, we are tagging the Docker images with the version of the model that was used to create the image. Using that approach, we can easily keep track of the model versions deployed to edge devices and either update or rollback as conditions in the field change and model drift occurs.

# COMMAND ----------

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
  archive_existing_versions=True
)
