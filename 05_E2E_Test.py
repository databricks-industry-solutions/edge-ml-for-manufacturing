# Databricks notebook source
# MAGIC %md
# MAGIC #End-to-end Testing
# MAGIC One of the benefits of using MLflow is the model versioning capabilities that it provides. Every time a new run is registered to an existing model in MLflow, a new version of that model is automatically created. This allows ML engineers to track and monitor the performance of new model versions and compare that to older versions. If a new version performs better with new data being received, they can promote that version to “Production” and automatically push that through the CI/CD pipeline that deployed these models to the edge. The same applies to scenarios where a new model version is not performing as expected and we need to roll back to a previous working version of the model.
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/model_versions_mlflow.png?raw=true" width=65%/>
# MAGIC 
# MAGIC 
# MAGIC In this solution accelerator, we are tagging the Docker images with the version of the model that was used to create the image. Using that approach, we can easily keep track of the model versions deployed to edge devices and either update or rollback as conditions in the field change and model drift occurs.

# COMMAND ----------

import mlflow
from mlflow.tracking.client import MlflowClient

# COMMAND ----------

# MAGIC %run ./config/notebook_config

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC To test the entire deployment process end-to-end all we need to know is to transition the ML Model to the **Production** stage using code below. As soon as that code gets executed:
# MAGIC 
# MAGIC 1. MLFlow Webhook triggers a Azure Databricks job and passes information about the model that trigger the webhook
# MAGIC 2. Using the model information, the Databricks job retreives the "Run ID" and "Model Version" from the Model Registry and then triggers the Azure DevOps pipeline passing those values as parameters
# MAGIC 3. Azure DevOps pipelines downloads ML Model with information it received from the Databricks job. It then creates a Docker image and pushes that image to the container registry tagging the image with the corresponding model version
# MAGIC 4. Any Edge device can now download that model as a Docker container and perform local inference

# COMMAND ----------

client = MlflowClient()

model_details = client.get_latest_versions(model_name)[0]

client.transition_model_version_stage(
  name=model_details.name,
  version=model_details.version,
  stage='Production',  
  archive_existing_versions=True
)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Image below shows the Docker image published to Azure Container Registry with the corresponding model version as the Docker image tag
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/acr-mlmodel.png?raw=true" width=65%/>
