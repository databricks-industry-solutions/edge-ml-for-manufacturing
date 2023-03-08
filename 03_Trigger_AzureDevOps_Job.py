# Databricks notebook source
# MAGIC %md
# MAGIC ###Create Databricks Job to trigger Azure DevOps pipeline	
# MAGIC 
# MAGIC There are multiple ways to trigger an Azure DevOps pipeline - it can be triggered manually, on a schedule, or by an external event via an API request. In our case, we will use a Databricks Job to trigger the Azure DevOps pipeline. The purpose of this Databricks Job is to capture information about the model that we want to deploy such as the Run ID and the version of the model and then trigger the Azure DevOps pipeline and pass that information in the API request. 

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Define Parameters, install Azure DevOps package and import Python libraries
# MAGIC 
# MAGIC An MLFlow webhook will call this notebook and will pass a message as a parameter with the information of the trigger event. We will create a parameter in the notebook using the Databricks Widgets API to capture that message and use throughout the notebook. We also have to install the azure-devops package use PIP and then import the required libraries to authenticate against Azure DevOps and trigger the CI/CD pipeline.

# COMMAND ----------

# Install azure-devops python package

%pip install azure-devops

# COMMAND ----------

# MAGIC %run ./config/notebook_config

# COMMAND ----------

# Import all required libraries to parse parameters and connect to Azure DevOps

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.pipelines.models import RunPipelineParameters,Variable
import mlflow
from mlflow import MlflowClient
import json

# COMMAND ----------

# Capture event message from MLFlow Webhook payload
dbutils.widgets.text("event_message", "")
webhook_payload = dbutils.widgets.get("event_message")
webhook_payload = webhook_payload.replace('\\','')
print(webhook_payload)

# Parse event message to get model_name

payload_json = json.loads(webhook_payload)
model_name = payload_json["model_name"]
print(model_name)


# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Trigger Azure DevOps Pipeline
# MAGIC 
# MAGIC After capturing the model name that triggered this Databricks job, we can now retrieve the run_id and the version of the model. We will pass those two as parameters when triggering the Azure DevOps Pipeline.
# MAGIC 
# MAGIC Additionally, we need to retrieve the access token and organization url values that were previously set in a secret scope. With all these values we can now trigger the Azure DevOps pipeline.

# COMMAND ----------

# Get run_id from model name

client = mlflow.MlflowClient()
run_id = client.get_latest_versions(model_name, stages=["Production"])[0].run_id
model_version = client.get_latest_versions(model_name, stages=["Production"])[0].version
print(run_id)

# COMMAND ----------

# Set access token and organization URL variables by retrieving values from Secrets scope
access_token = dbutils.secrets.get(scope = "solution-accelerator-cicd", key = "azure_devops_access_token")
organization_url = dbutils.secrets.get(scope = "solution-accelerator-cicd", key = "azure_devops_organization_url") 
azure_devops_project = dbutils.secrets.get(scope = "solution-accelerator-cicd", key = "azure_devops_project") 
azure_devops_pipeline_id = "1"

# Create a connection to the Azure DevOps Org
credentials = BasicAuthentication('', access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Create a pipeline client
pipeline_client = connection.clients_v6_0.get_pipelines_client()

# Define parameters that will be passed to the pipeline
run_parameters = RunPipelineParameters(template_parameters = {"run_id":run_id, "model_version":model_version, "databricks_host": databricks_host, "databricks_token": databricks_token})

# Trigger pipeline
runPipeline = pipeline_client.run_pipeline(run_parameters=run_parameters,project=azure_devops_project, pipeline_id=azure_devops_pipeline_id)
print("Pipeline has been triggered")


# COMMAND ----------

# MAGIC %md
# MAGIC Once the job gets created, you can open the job details in Databricks UI and capture the Job ID located on the top right corner of the window. This Job ID will be used in the next section.
# MAGIC 
# MAGIC ###TODO grab the image from blog
