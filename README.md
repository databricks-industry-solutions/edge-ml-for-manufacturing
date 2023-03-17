![image](https://user-images.githubusercontent.com/86326159/206014015-a70e3581-e15c-4a10-95ef-36fd5a560717.png)

[![CLOUD](https://img.shields.io/badge/CLOUD-ALL-blue?logo=googlecloud&style=for-the-badge)](https://cloud.google.com/databricks)
[![POC](https://img.shields.io/badge/POC-10_days-green?style=for-the-badge)](https://databricks.com/try-databricks)

## Deploying and Maintaining Machine Learning Models on the "Edge" in Manufacturing

Edge computing is a computing paradigm that refers to devices that store, process data and make decisions very close to where that data is being generated. Edge computing has existed for a long time but the “Edge” has become more relevant over the last few years as more companies move their storage and compute capacity to the cloud but still have the need to keep some compute processing running on-premise to meet certain business or technical requirements. In manufacturing, it is very common to see local servers deployed at manufacturing sites that are used to collect and store data from various machines/sensors in a manufacturing plant and apply AI/ML models to incoming data to analyze patterns and anomalies in the data.

There are many different reasons why manufacturers may decide to deploy machine learning (ML) models and other analytics solutions directly to the Edge:
- **Unreliable connectivity to the cloud:** Depending on the manufacturing plant's location and/or conditions, connectivity issues may result in unstable communication with the cloud, impacting the effectiveness of any critical predictive maintenance model that attempts to prevent catastrophic failures.
- **Latency requirements:** Some use cases require low-latency responses. For example, a computer vision use case that looks for common product defects as they are being manufactured will need to quickly make decisions to remove faulty parts from the manufacturing line for further inspection. 
- **Security:** Due to compliance and security requirements (Purdue model, ISA95, etc), some of the shop floor systems are not permitted to connect directly to the internet. In those scenarios, there is a need to perform inference on-premise without having to send data over the internet. 

In this solution accelerator, we discuss how manufacturers are taking advantage of the cloud and delivering analytics and AI solutions to Edge devices using standard patterns. There are different ways to push models to the edge but in this solution acceleator, we will leverage Docker to deliver ML models built on Databricks down to the Edge.

The main advantages of using Docker are its portability and consistency - Docker containers are platform-agnostic and they make it very easy to package and deploy the ML model along with all its dependencies and configuration from Databricks to an on-premise server. Docker is a great option for deploying ML models to on-premise servers with sufficient CPU, memory, and storage capacity. However, Docker is not the answer to every Edge use case and there are other technologies/frameworks available such as TensorFlow Lite or PyTorch Mobile that were specifically designed to deploy ML models to microcontrollers and other embedded edge devices with storage, memory and CPU constraints.



___
<andres.urrutia@databricks.com>

___

<img alt="add_repo" src="https://github.com/databricks-industry-solutions/edge-ml-for-manufacturing/blob/main/images/edge-deployment-ref-diagram.png?raw=true" width=75%/>

___

&copy; 2022 Databricks, Inc. All rights reserved. The source in this notebook is provided subject to the Databricks License [https://databricks.com/db-license-source].  All included or referenced third party libraries are subject to the licenses set forth below.

| library                                | description             | license    | source                                              |
|----------------------------------------|-------------------------|------------|-----------------------------------------------------|
| PyYAML                                 | Reading Yaml files      | MIT        | https://github.com/yaml/pyyaml                      |

## Getting started

Although specific solutions can be downloaded as .dbc archives from our websites, we recommend cloning these repositories onto your databricks environment. Not only will you get access to latest code, but you will be part of a community of experts driving industry best practices and re-usable solutions, influencing our respective industries. 

<img width="500" alt="add_repo" src="https://user-images.githubusercontent.com/4445837/177207338-65135b10-8ccc-4d17-be21-09416c861a76.png">

To start using a solution accelerator in Databricks simply follow these steps: 

1. Clone solution accelerator repository in Databricks using [Databricks Repos](https://www.databricks.com/product/repos)
2. Attach the `RUNME` notebook to any cluster and execute the notebook via Run-All. A multi-step-job describing the accelerator pipeline will be created, and the link will be provided. The job configuration is written in the RUNME notebook in json format. 
3. Execute the multi-step-job to see how the pipeline runs. 
4. You might want to modify the samples in the solution accelerator to your need, collaborate with other users and run the code samples against your own data. To do so start by changing the Git remote of your repository  to your organization’s repository vs using our samples repository (learn more). You can now commit and push code, collaborate with other user’s via Git and follow your organization’s processes for code development.

The cost associated with running the accelerator is the user's responsibility.


## Project support 

Please note the code in this project is provided for your exploration only, and are not formally supported by Databricks with Service Level Agreements (SLAs). They are provided AS-IS and we do not make any guarantees of any kind. Please do not submit a support ticket relating to any issues arising from the use of these projects. The source in this project is provided subject to the Databricks [License](./LICENSE). All included or referenced third party libraries are subject to the licenses set forth below.

Any issues discovered through the use of this project should be filed as GitHub Issues on the Repo. They will be reviewed as time permits, but there are no formal SLAs for support. 
