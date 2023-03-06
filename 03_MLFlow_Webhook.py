# Databricks notebook source
# MAGIC %md 
# MAGIC ###Creating MLflow Webhooks to enable automation
# MAGIC 
# MAGIC MLflow webhooks enable you to listen to Model Registry events, such as when a model version is created or when that version is transitioned into a production environment, to automatically trigger actions. These webhooks allow you to automate your MLOps processes and integrate your machine learning pipeline with other CI/CD tools such as Azure DevOps. In this scenario, we will trigger the Azure DevOps pipeline that creates and uploads the Docker image anytime a version of our ML Model is transitioned into the production stage.
# MAGIC 
# MAGIC MLflow webhooks can be created through the Databricks REST API or using the Python library databricks-registry-webhooks. Here is the important section of Python code that creates the MLflow webhook to track when the “sensor_model” gets transitioned into production.

# COMMAND ----------

# MAGIC %md
# MAGIC To call the Databricks Job, we pass the Job ID we captured earlier to the JobSpec function. There are multiple Webhook events that can be configured such as when a new version of the ML model gets created (MODEL_VERSION_CREATED) or when a new ML model is registered in MLFlow registry (REGISTERED_MODEL_CREATED). For this example, we are configuring the Webhook to be triggered anytime a version of the ML model is transitioned into the production stage.

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
              "notebook_path": f"02_Trigger_AzureDevOps_Job"
          },
          "task_key": "edge_ml_02"
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


# http_webhook = RegistryWebhooksClient().create_webhook(
#   events=["TRANSITION_REQUEST_CREATED", "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"],
#   http_url_spec=http_url_spec,
#   model_name=model_name,
#   status="TEST_MODE"
# )
# http_webhook

# COMMAND ----------

# Uncomment code below to test a particular webhook that was previously created by passing the webhook id
vtest = RegistryWebhooksClient().test_webhook(job_webhook.id)
vtest

# COMMAND ----------

# Uncomment code below to list any webhooks created for a particular model
RegistryWebhooksClient().list_webhooks(model_name=model_name)

# COMMAND ----------

# Uncomment code below to transition a webhook from "TEST_MODE" to "ACTIVE"

# http_webhook = RegistryWebhooksClient().update_webhook(
#   id=job_webhook.id,
#   status="ACTIVE"
# )

# COMMAND ----------

# Uncomment code below to delete any webhook by providing the webhook id
# RegistryWebhooksClient().delete_webhook(id=job_webhook.id)

