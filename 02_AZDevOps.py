# Databricks notebook source
# MAGIC %md
# MAGIC ### Configure Azure DevOps
# MAGIC 
# MAGIC This section of the Solution Accelerator will be done outside Databricks. We are using Azure DevOps as the CI/CD tool to download, test and push a Docker image containing the ML model to an Azure Container Registry. Although we are leveraging this Azure services to build the automation, the pattern we are presenting here does not depend on any of those services, and other CI/CD solutions and/or image repositories such as Jenkins and Docker registry are fully supported as well.
# MAGIC 
# MAGIC The image below shows where Azure DevOps fits in the overall ML edge deployment pipeline:
