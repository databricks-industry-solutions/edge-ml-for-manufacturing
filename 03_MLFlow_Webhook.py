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

# MAGIC %pip install databricks-registry-webhooks

# COMMAND ----------

from databricks_registry_webhooks import RegistryWebhooksClient, JobSpec

# COMMAND ----------

# MAGIC %md
# MAGIC Use the Job ID from the last step of the 02_Trigger_AzureDevOps_Job notebook

# COMMAND ----------

job_id = "<YOUR_DATABRICKS_JOB_ID>"
model_name = "sensor_model"

access_token = dbutils.secrets.get(scope = "<YOUR_SCOPE", key = "<YOUR_TOKEN_KEY>")

# COMMAND ----------

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

# Uncomment code below to list any webhooks created for a particular model
# RegistryWebhooksClient().list_webhooks(model_name=model_name)

# COMMAND ----------

# MAGIC %md
# MAGIC ###Configure edge device
# MAGIC 
# MAGIC The last step of this automated process is to configure the Edge devices, running Azure IoT Edge, to point to the repo in Azure Container Registry (ACR) that contains the ML Model. Azure IoT Edge devices use a deployment manifest to tell the device which modules to install and how to configure them to work together. For this example, we will push the deployment manifest to a single Azure IoT Edge but in a real-world scenario with multiple edge devices, it would make more sense to configure an automated deployment that pushes the deployment manifest to all devices in the field that meets a set of defined conditions. 
# MAGIC 
# MAGIC To push the deployment manifest to a single device, you can open the IoT Hub service in the Azure Portal and navigate to the IoT Edge device that we are interested in. You click on “Set Modules” and then select “Add IoT Edge Module”. In that screen you can enter the container registry and repository information where the ML model will be uploaded. Once you apply and submit those changes, a deployment manifest is pushed to the Edge devices instructing that device to download that Docker image and start the container.
# MAGIC 
# MAGIC ###TODO add image
