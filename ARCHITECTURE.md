# System Architecture Diagram & Technical Report - Project Quantum

This document provides a comprehensive overview of the design, communication flows, and infrastructure layout for **Project Quantum - Enterprise AI Model Serving Infrastructure**.

---

## 1. System Architecture & Data Flow

The following Mermaid diagram illustrates the request routing path, metrics scrapings, logging collection pipeline, and secret integration paths.

```mermaid
graph TD
    %% Users and Entry Points
    User[Client Web Browser] -->|HTTP Port 3000| FE[Nginx Frontend Container]
    User -->|Inference Queries Port 8000| BE[FastAPI Backend Container]
    
    %% Application Layer
    subgraph K8s_Quantum_Namespace ["Kubernetes Cluster namespace: 'quantum'"]
        FE
        BE
        
        %% Model Loader
        BE -->|Dynamic Load| ML_Loader[Model Loader Service]
        ML_Loader -->|Read Pickles| Serialized_Models[(Models: Loan, House, Churn)]
        
        %% Monitoring Stack
        BE -->|Metrics Endpoint /metrics| Prom[Prometheus Pod]
        Prom -->|Scraped Telemetry| Grafana[Grafana Dashboard Pod]
        
        %% Logging Stack
        BE -->|JSON Logs File /app/logs/application.log| FB[Filebeat Agent DaemonSet]
    end

    %% External & Centralized Services
    subgraph Central_Services ["Observability & Security Systems"]
        FB -->|Ship Logs| LS[Logstash Pipeline]
        LS -->|Filter & Index| ES[(Elasticsearch Cluster)]
        Kibana[Kibana Interface] -->|Query Indices| ES
        
        %% Secret Management
        BE -->|Kubernetes Token Login| Vault[HashiCorp Vault Server]
        Vault -->|Inject API & DB keys| BE
    end

    classDef k8s fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#F8FAFC;
    classDef external fill:#0F172A,stroke:#A78BFA,stroke-width:2px,color:#F8FAFC;
    class FE,BE,Prom,Grafana,FB,ML_Loader,Serialized_Models k8s;
    class LS,ES,Kibana,Vault external;
```

---

## 2. Infrastructure Deployment Topology (AWS & Kubernetes)

The platform is designed to be provisioned via Terraform and orchestrated using AWS EKS across multiple availability zones.

```mermaid
graph TD
    subgraph AWS_Cloud ["AWS Cloud Region: us-east-1"]
        subgraph VPC ["Virtual Private Cloud - 10.0.0.0/16"]
            IGW[Internet Gateway]
            
            subgraph Availability_Zone_A ["Availability Zone A"]
                Subnet_Public_A[Public Subnet 10.0.0.0/24]
                EKS_Node_1[EKS EC2 Worker Node]
            end
            
            subgraph Availability_Zone_B ["Availability Zone B"]
                Subnet_Public_B[Public Subnet 10.0.1.0/24]
                EKS_Node_2[EKS EC2 Worker Node]
            end
        end
    end
    
    %% Connections
    IGW --> RouteTable[Public Route Table]
    RouteTable --> Subnet_Public_A
    RouteTable --> Subnet_Public_B
    
    EKS_Node_1 -->|NodePort: 30080| FE_Pod[Frontend Pod]
    EKS_Node_1 -->|ClusterIP: 8000| BE_Pod_1[Backend Pod 1]
    
    EKS_Node_2 -->|ClusterIP: 8000| BE_Pod_2[Backend Pod 2]

    classDef vpc fill:#0F172A,stroke:#10B981,stroke-width:2px,color:#FFF;
    classDef node fill:#1E293B,stroke:#F59E0B,stroke-width:2px,color:#FFF;
    class VPC vpc;
    class EKS_Node_1,EKS_Node_2 node;
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
