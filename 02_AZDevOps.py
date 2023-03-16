# Databricks notebook source
# MAGIC %md
# MAGIC ### Integratin with Azure DevOps and Azure Container Registry
# MAGIC 
# MAGIC This section of the Solution Accelerator is be done outside Databricks. We are using Azure DevOps as the CI/CD tool to download, test and push a Docker image containing the ML model to an Azure Container Registry. Although we are leveraging this Azure services to build the automation, the pattern we are presenting here does not depend on any of those services, and other CI/CD solutions and/or image repositories such as Jenkins and Docker registry are fully supported as well.
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
# MAGIC 
# MAGIC ### Create and Configure Azure DevOps Pipeline
