# System Architecture Diagram & Technical Report - Project Quantum

This document provides a comprehensive overview of the design, communication flows, and infrastructure layout for **Project Quantum - Enterprise AI Model Serving Infrastructure**.

---

## 1. System Architecture & Data Flow

The following flowchart illustrates the request routing path, metrics scrapings, logging collection pipeline, and secret integration paths:

```text
                  +-----------------------+
                  |  Client Web Browser   |
                  +-----------+-----------+
                              |
              +---------------+---------------+
              | (HTTP 3000)                   | (HTTP 8000)
              v                               v
  +-----------------------+       +-------------------------------+
  |    Nginx Frontend     |       |        FastAPI Backend        |
  |      Container        |       |           Container           |
  +-----------------------+       +---------------+---------------+
                                                  |
                  +-------------------------------+---------------+-------------------------------+
                  |                               |                               |               |
                  v                               v                               v               v
       +--------------------+          +--------------------+          +---------------------+ +-----+
       |   Model Loader     |          |  Prometheus Pod    |          |  Filebeat DaemonSet | |     |
       |     Service        |          | (Scrapes /metrics) |          | (Reads app.log file)| |  V  |
       +----------+---------+          +----------+---------+          +----------+----------+ |  A  |
                  |                               |                               |            |  U  |
                  v                               v                               v            |  L  |
       +--------------------+          +--------------------+          +---------------------+ |  T  |
       | Serialized Models  |          | Grafana Dashboard  |          | Logstash Pipeline   | |     |
       | (Loan, House,      |          |        Pod         |          | (Filters & Indexes) | +--+--+
       |   Churn PKLs)      |          +--------------------+          +----------+----------+    |
       +--------------------+                                                     |               |
                                                                                  v               |
                                                                       +---------------------+    |
                                                                       |    Elasticsearch    | <--+
                                                                       |       Cluster       | (Token Auth)
                                                                       +----------+----------+
                                                                                  ^
                                                                                  | (Queries)
                                                                       +----------+----------+
                                                                       |  Kibana Interface   |
                                                                       +---------------------+
```

---

## 2. Infrastructure Deployment Topology (AWS & Kubernetes)

The platform is designed to be provisioned via Terraform and orchestrated using AWS EKS across multiple availability zones:

```text
+----------------------------------------------------------------------------------------------------+
| AWS Cloud Region: us-east-1                                                                        |
|  +-----------------------------------------------------------------------------------------------+ |
|  | Virtual Private Cloud (VPC) - 10.0.0.0/16                                                     | |
|  |                                                                                               | |
|  |             +-------------------------+                                                       | |
|  |             |    Internet Gateway     |                                                       | |
|  |             +------------+------------+                                                       | |
|  |                          |                                                                    | |
|  |                          v                                                                    | |
|  |             +-------------------------+                                                       | |
|  |             |   Public Route Table    |                                                       | |
|  |             +------+------------+-----+                                                       | |
|  |                    |            |                                                             | |
|  |         +----------+            +----------+                                                  | |
|  |         |                                  |                                                  | |
|  |         v                                  v                                                  | |
|  |  +------------------------------+   +------------------------------+                          | |
|  |  | Availability Zone A          |   | Availability Zone B          |                          | |
|  |  |  +------------------------+  |   |  +------------------------+  |                          | |
|  |  |  | Public Subnet          |  |   |  | Public Subnet          |  |                          | |
|  |  |  | 10.0.0.0/24            |  |   |  | 10.0.1.0/24            |  |                          | |
|  |  |  +-----------+------------+  |   |  +-----------+------------+  |                          | |
|  |  |              |               |   |              |               |                          | |
|  |  |              v               |   |              v               |                          | |
|  |  |  +------------------------+  |   |  +------------------------+  |                          | |
|  |  |  | EKS EC2 Worker Node 1  |  |   |  | EKS EC2 Worker Node 2  |  |                          | |
|  |  |  |  +------------------+  |  |   |  |  +------------------+  |  |                          | |
|  |  |  |  | Frontend Pod     |  |  |   |  |  | Backend Pod 2    |  |  |                          | |
|  |  |  |  | (NodePort 30080) |  |  |   |  |  | (ClusterIP 8000) |  |  |                          | |
|  |  |  |  +------------------+  |  |   |  |  +------------------+  |  |                          | |
|  |  |  |  +------------------+  |  |   |  +------------------------+  |                          | |
|  |  |  |  | Backend Pod 1    |  |  |   +------------------------------+                          | |
|  |  |  |  | (ClusterIP 8000) |  |  |                                                             | |
|  |  |  |  +------------------+  |  |                                                             | |
|  |  |  +------------------------+  |  |                                                             | |
|  |  +------------------------------+                                                             | |
|  +-----------------------------------------------------------------------------------------------+ |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Technology Integrations Overview

* **Inference Gateway**: Built with **FastAPI** for high concurrency and native support for async tasks.
* **Auto-Scaling (HPA)**: Scales inference pods dynamically based on CPU/Memory loads to guarantee throughput.
* **Gateway Observability**:
  * **Prometheus**: Polls `/metrics` every 10 seconds.
  * **Grafana**: Visualizes response times, HTTP statuses, and model toggling states.
* **Structured Auditing**: The application generates structured JSON logs directly to standard output and `application.log`. **Logstash** ingests, parses the JSON structure, and indexes it into **Elasticsearch** for search and dashboards in **Kibana**.
* **Zero-Trust Security**: **HashiCorp Vault** manages sensitive API tokens and database keys. Pods authenticate dynamically using Kubernetes Service Account Tokens.
