# Databricks notebook source
pip install azure-devops

# COMMAND ----------

# Import all required libraries to parse parameters and connect to Azure DevOps

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from azure.devops.v6_0.pipelines.models import RunPipelineParameters,Variable
import mlflow
from mlflow import MlflowClient
import json

# COMMAND ----------

# Obtain model_name from webhook payload

webhook_payload = dbutils.widgets.get("event_message")
webhook_payload = webhook_payload.replace('\\','')
print(webhook_payload)
payload_json = json.loads(webhook_payload)
model_name = payload_json["model_name"]
print(model_name)


# COMMAND ----------

# Get run_id from model name

client = mlflow.MlflowClient()
run_id = client.get_latest_versions(model_name, stages=["Production"])[0].run_id
model_version = client.get_latest_versions(model_name, stages=["Production"])[0].version
print(run_id)

# COMMAND ----------

# Set access token and organization URL variables by retrieving values from Secrets store
access_token = dbutils.secrets.get(scope = "<SECRET_SCOPE>", key = "<SECRET_KEY>")
organization_url = dbutils.secrets.get(scope = "<SECRET_SCOPE>", key = "<SECRET_KEY>")

# Create a connection to the Azure DevOps Org
credentials = BasicAuthentication('', access_token)
connection = Connection(base_url=organization_url, creds=credentials)

# Create a pipeline client
pipeline_client = connection.clients_v6_0.get_pipelines_client()

# Define parameters that will be passed to the pipeline
run_parameters = RunPipelineParameters(template_parameters = {"run_id":run_id, "model_version":model_version})

# Run pipeline
runPipeline = pipeline_client.run_pipeline(run_parameters=run_parameters,project="<AZURE_DEVOPS_PROJECT_", pipeline_id=<AZURE_DEVOPS_PIPELINE_ID>)
print("Pipeline has been triggered")

