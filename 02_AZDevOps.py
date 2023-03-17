# Databricks notebook source
# MAGIC %md
# MAGIC ### Integrating with Azure DevOps and Azure Container Registry
# MAGIC 
# MAGIC This section of the Solution Accelerator is be done outside Databricks. We are using Azure DevOps as the CI/CD tool to download, test and push a Docker image containing the ML model to an Azure Container Registry. Although we are leveraging this Azure services to build the automation, the pattern we are presenting here does not depend on any of those services, and other CI/CD solutions and/or image repositories such as Jenkins and Docker registry are fully supported as well. This automated deployment pipeline we are building will help us scale the deployment of ML Models to multiple Edge devices.
# MAGIC 
# MAGIC More information on how to create an Azure DevOps Organization and how to deploy Azure Container Registry can be found at the following links:
# MAGIC 
# MAGIC - https://learn.microsoft.com/en-us/azure/devops/organizations/accounts/create-organization?view=azure-devops
# MAGIC - https://learn.microsoft.com/en-us/azure/container-registry/container-registry-get-started-portal?tabs=azure-cli
# MAGIC 
# MAGIC 
# MAGIC 
# MAGIC 
# MAGIC The image below shows where Azure DevOps fits in the overall ML edge deployment pipeline:
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/ml-edge-deployment-flow.png?raw=true" width="40%">
# MAGIC 
# MAGIC 
# MAGIC At a high level, the components used, and the path that is followed to get the Databricks-trained model pushed into Azure Container Registry as a self-contained Docker image are:
# MAGIC 
# MAGIC 1. MLflow webhooks will be used to automatically trigger an Azure DevOps pipeline
# MAGIC 2. Azure DevOps will download the artifacts for the model that we previously built from MLflow Registry and creates a Docker image containing the ML model
# MAGIC 3. Azure DevOps pushes the Docker image to Azure Container Registry
# MAGIC 4. Azure IoT Edge’s Deployment Manifest gets updated to instruct the Edge server to download and deploy the Docker image containing the ML model

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create Databricks Token
# MAGIC 
# MAGIC Azure DevOps needs to be able to authenticate to Databricks to download the ML Model. A Databricks Access Token gives programmatic access to the Databricks and the managed MLFlow Registry. Follow [these steps](https://learn.microsoft.com/en-us/azure/databricks/dev-tools/auth#--azure-databricks-personal-access-tokens) to generate an Access Token using the Databricks UI.
# MAGIC 
# MAGIC Make note of that token and the Databricks Workspace URL before continuing to the next section below.

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ### Configure Azure DevOps Pipeline
# MAGIC 
# MAGIC #### Create Pipeline
# MAGIC The Azure DevOps Pipeline we are building will download the ML model artifacts from the MLflow registry and then create a Docker image that exposes the model to receive HTTP REST calls. Follow these steps to create an [Azure DevOps Pipeline](https://learn.microsoft.com/en-us/azure/devops/pipelines/create-first-pipeline?view=azure-devops&tabs=java%2Ctfs-2018-2%2Cbrowser) and then copy/paste the YAML file that is included in the [Github repository](https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/azure-pipelines.yml) for this Solution Accelerator. The pipeline should look something like this:
# MAGIC 
# MAGIC <img src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/ado_pipeline.png?raw=true" width="80%">
# MAGIC 
# MAGIC #### Update Pipeline
# MAGIC 
# MAGIC Make sure to update these values in the pipeline as follows:
# MAGIC 
# MAGIC - `MLFLOW_TRACKING_URI`: The value of this variable should be `databricks`
# MAGIC - `DATABRICKS_HOST`: Enter the Databricks Workspace URL that was captured earlier It should look something similar this: `https://adb-254883549138.18.azuredatabricks.net/`
# MAGIC - `DATABRICKS_TOKEN`: Enter the Databricks Token that was generated in the previous step
# MAGIC 
# MAGIC The Azure Container Registry (ACR) URL and Azure DevOps task that connects the Pipeline to that ACR needs to be updated as well:
# MAGIC 
# MAGIC 1. Find the `Create Docker Image` step in the YAML file and replace the URL `solacc.azurecr.io` with the URL of the Azure Container Registry that was previously deployed
# MAGIC 2. Delete whole task called `Push Docker Image to ACR` and create a new one that connects to the Azure Container Registry. More information on how to create that task can be found [here](https://learn.microsoft.com/en-us/azure/devops/pipelines/ecosystems/containers/acr-template?view=azure-devops)
# MAGIC 
# MAGIC #### Capture Pipeline Information
# MAGIC 
# MAGIC To trigger this Azure DevOps pipeline from Databricks, you will need to capture two values:
# MAGIC 
# MAGIC - **Azure DevOps Project Name:** Project Name was provided when you created the Azure DevOps organization and project in the previous step.
# MAGIC - **Azure DevOps Organization URL:** Go to "Pipeline's Edit" page and look at the browser's URL. The first part of the URL will contain the organization's URL and it would look something similar to `http://dev.azure.com/{organization}`
# MAGIC - **Pipeline ID:** The Pipeline ID can also be found in the browser's URL. In the "Pipeline's Edit" page, take a look at the URL and look for the number right after the `pipelineId` paramater. Make note of that number.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Create Databricks Job
# MAGIC 
# MAGIC Continue to the next notebook where you will create a Databricks Job that will trigger this Azure DevOps pipeline using the pipeline values that we just captured
