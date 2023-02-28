# Databricks notebook source
# MAGIC %md You may find this solution accelerator notebook at https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing

# COMMAND ----------

# MAGIC %pip install databricks-registry-webhooks

# COMMAND ----------

from databricks_registry_webhooks import RegistryWebhooksClient, JobSpec

# COMMAND ----------

job_id = "922792279829219"
model_name = "AUIoTSensorModel"
access_token = dbutils.secrets.get(scope = "andres-scope", key = "db_token")

# COMMAND ----------

job_spec = JobSpec(job_id=job_id, access_token=access_token)

job_webhook = RegistryWebhooksClient().create_webhook(
  model_name=model_name,
  events=["TRANSITION_REQUEST_CREATED", "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"],
  job_spec=job_spec,
  description="Job webhook trigger",
  status="TEST_MODE"
)

print(job_webhook)

#

# http_webhook = RegistryWebhooksClient().create_webhook(
#   events=["TRANSITION_REQUEST_CREATED", "MODEL_VERSION_TRANSITIONED_TO_PRODUCTION"],
#   http_url_spec=http_url_spec,
#   model_name=model_name,
#   status="TEST_MODE"
# )
# http_webhook

# COMMAND ----------

# Uncomment code below to transition a webhook from "TEST_MODE" to "ACTIVE"

# http_webhook = RegistryWebhooksClient().update_webhook(
#   id=job_webhook.id,
#   status="ACTIVE"
# )

# COMMAND ----------

# Uncomment code below to test a particular webhook that was previously created by passing the webhook id
#vtest = RegistryWebhooksClient().test_webhook(job_webhook.id)


# COMMAND ----------

# Uncomment code below to list any webhooks created for a particular model
RegistryWebhooksClient().list_webhooks(model_name="AUIoTSensorModel")

# COMMAND ----------

# Uncomment code below to delete any webhook by providing the webhook id
# RegistryWebhooksClient().delete_webhook(id="a6321f572fed4c90abad82f8e815ecf6")
