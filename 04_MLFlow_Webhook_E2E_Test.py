# Databricks notebook source
# MAGIC %md 
# MAGIC #Creating MLflow Webhooks to enable automation
# MAGIC 
# MAGIC MLflow webhooks enable you to listen to Model Registry events, such as when a model version is created or when that version is transitioned into a production environment, to automatically trigger actions. These webhooks allow you to automate your MLOps processes and integrate your machine learning pipeline with other CI/CD tools such as Azure DevOps. In this scenario, we will trigger the Azure DevOps pipeline that creates and uploads the Docker image anytime a version of our ML Model is transitioned into the production stage.
# MAGIC 
# MAGIC MLflow webhooks can be created through the Databricks REST API or using the Python library `databricks-registry-webhooks`. Here is the important section of Python code that creates the MLflow webhook to track when the “sensor_model” gets transitioned into production.

# COMMAND ----------

# MAGIC %md
# MAGIC To call the Databricks Job, we pass the Job ID we captured earlier to the JobSpec function. There are multiple Webhook events that can be configured such as when a new version of the ML model gets created (MODEL_VERSION_CREATED) or when a new ML model is registered in MLflow registry (REGISTERED_MODEL_CREATED). For this example, we are configuring the Webhook to be triggered anytime a version of the ML model is transitioned into the production stage.

# COMMAND ----------

# MAGIC %pip install databricks-registry-webhooks git+https://github.com/databricks-academy/dbacademy@v1.0.13 git+https://github.com/databricks-industry-solutions/notebook-solution-companion@safe-print-html --quiet --disable-pip-version-check

# COMMAND ----------

# DBTITLE 1,Get configs such as model names that are consistent throughout this accelerator
# MAGIC %run ./config/notebook_config

# COMMAND ----------

# MAGIC %md In the blog, we asked you to follow these [steps](https://learn.microsoft.com/en-us/azure/databricks/workflows/jobs/jobs) to create a Databricks Job and point that job to notebook 02. 
# MAGIC Here we automated this step with `NotebookSolutionCompanion` to ensure consistent job creation.

# COMMAND ----------

from databricks_registry_webhooks import RegistryWebhooksClient, JobSpec
from solacc.companion import NotebookSolutionCompanion

# COMMAND ----------

job_json = {
  "timeout_seconds": 28800,
  "max_concurrent_runs": 1,
  "tags": {
      "usage": "solacc_testing",
      "group": "MFG",
      "accelerator": "edge-ml-for-manufacturing"
  },
  "tasks": [

      {
          "job_cluster_key": "edge_ml_cluster",
          "notebook_task": {
              "notebook_path": f"03_Trigger_AzureDevOps_Job"
          },
          "task_key": "edge_ml_03"
      }
  ],
  "job_clusters": [
      {
          "job_cluster_key": "edge_ml_cluster",
          "new_cluster": {
              "spark_version": "11.3.x-cpu-ml-scala2.12",
          "spark_conf": {
              "spark.databricks.delta.formatCheck.enabled": "false"
              },
              "num_workers": 1,
              "node_type_id": {"AWS": "i3.xlarge", "MSA": "Standard_DS3_v2", "GCP": "n1-highmem-4"},
              "custom_tags": {
                  "usage": "solacc_testing",
                  "group": "MFG",
                  "accelerator": "edge-ml-for-manufacturing"
              },
          }
      }
  ]
}

# COMMAND ----------

# DBTITLE 1,We automate the creation of a simple job for Notebook 02
nsc = NotebookSolutionCompanion()
job_params = nsc.customize_job_json(job_json, "webhook-ml-edge-deploy", nsc.solacc_path, nsc.cloud)

# we will use this job_id in webhook definition 
job_id = nsc.create_or_update_job_by_name(job_params)
print(f"Job id is {job_id}")


# COMMAND ----------

# DBTITLE 1,Create webhook
job_spec = JobSpec(job_id=job_id, access_token=access_token)

job_webhook = RegistryWebhooksClient().create_webhook(
  model_name=model_name,
  events=["TRANSITION_REQUEST_CREATED", "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"],
  job_spec=job_spec,
  description="Job webhook trigger",
  status="ACTIVE"
)

print(job_webhook)

# COMMAND ----------

RegistryWebhooksClient().list_webhooks(model_name=model_name)

# COMMAND ----------

# MAGIC %md Now that we have everything in place, let's proceed to test out the deployment.

# COMMAND ----------

# MAGIC %md
# MAGIC #End-to-end Testing
# MAGIC One of the benefits of using MLflow is the model versioning capabilities that it provides. Every time a new run is registered to an existing model in MLflow, a new version of that model is automatically created. This allows ML engineers to track and monitor the performance of new model versions and compare that to older versions. If a new version performs better with new data being received, they can promote that version to “Production” and automatically push that through the CI/CD pipeline that deployed these models to the edge. The same applies to scenarios where a new model version is not performing as expected and we need to roll back to a previous working version of the model.
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/model_versions_mlflow.png?raw=true" width=75%/>
# MAGIC 
# MAGIC 
# MAGIC We tag the Docker images with the version of the model that was used to create the image. Using that approach, we can easily keep track of the model versions deployed to edge devices and either update or rollback as conditions in the field change and model drift occurs.

# COMMAND ----------

import mlflow
from mlflow.tracking.client import MlflowClient

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

# MAGIC %md This model stage transition should have triggered a run in the Azure DevOps Pipeline we deployed. A successful run may look like:
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/azdevops-pipeline-run.png?raw=true" width=75%/>
# MAGIC 
# MAGIC You should also verify the container deployment in the container registry.
# MAGIC 
# MAGIC After testing this deployment pattern, if you not intend to leave the webhook around, make sure to clean it up.

# COMMAND ----------

# DBTITLE 0,After the webhook has been tested, let's clean it up.
import time
time.sleep(60)

RegistryWebhooksClient().delete_webhook(id=job_webhook.id)
