# Project Quantum - Enterprise AI Model Serving Platform

Project Quantum is a production-grade MLOps and DevOps ecosystem designed to serve machine learning models at scale. The platform serves three active ML models (Loan Approval, House Valuation, Customer Churn) in real time while demonstrating core DevOps lifecycle features: containerization, cloud infrastructure provisioning, CI/CD pipelines, secret management, centralized logging, and interactive metrics monitoring with chaos simulations.

---

## 📂 Repository File Structure
```text
project-quantum/
├── docker-compose.yml       # Docker Compose stack orchestration
├── Jenkinsfile              # Declarative CI/CD pipeline automation
├── backend/
│   ├── Dockerfile           # Backend containerization config (non-root runner)
│   ├── main.py              # FastAPI server (predictions, logging, metrics, chaos)
│   ├── model_loader.py      # Joblib loading class & toggle state manager
│   ├── requirements.txt         # Backend Python dependencies
│   ├── models/              # Serialized pickle files (.pkl)
│   ├── logs/                # Local runtime logs
│   ├── schemas/             # Pydantic input schemas
│   └── utils/
│       ├── logger.py        # Structured JSON formatter
│       └── train_models.py  # Offline model training script
├── frontend/
│   ├── Dockerfile           # Frontend Nginx serving container config
│   ├── index.html           # Main dashboard console and chaos controller
│   ├── style.css            # Custom responsive dark-theme stylesheet
│   ├── script.js            # Form updates, HTTP requests, history, and status polling
│   └── pages/
│       └── registry.html    # Model registry metadata catalog
├── monitoring/
│   ├── Dockerfile           # Custom Prometheus container definition
│   ├── prometheus.yml       # Telemetry scraping config (every 5 seconds)
│   └── grafana-dashboard.json # Visual dashboards model template import
├── logging/
│   ├── logstash.conf        # ELK logs parsing pipeline
│   ├── elasticsearch.yml    # Elasticsearch cluster settings
│   └── kibana.yml           # Kibana console configurations
├── vault/
│   ├── vault-init.sh        # Secrets database setup script
│   └── app-policy.hcl       # Policy restriction rules
├── ARCHITECTURE.md          # Visual architecture Mermaid diagrams
└── DISASTER_RECOVERY.md     # DR metrics, backups, and restore operations
```

---

## 🚀 Setup & Execution Guide (Phase by Phase)

### 🐍 Phase 1: Local Backend Setup

#### 1. Setup Virtual Environment
Open a terminal and navigate to the project directory:
```bash
cd project-quantum
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

#### 2. Train and Serialize Models
Train the Loan, House, and Churn models using synthetic data:
```bash
python3 backend/utils/train_models.py
```
*(This outputs `.pkl` files to `backend/models/`)*

#### 3. Run FastAPI Server
```bash
cd backend
python3 -m uvicorn main:app --reload --port 8000 --host 127.0.0.1
```
* **Docs GUI**: `http://localhost:8000/docs`
* **Health API**: `http://localhost:8000/health`
* **Metrics API**: `http://localhost:8000/metrics`

---

### 🌐 Phase 2: Local Frontend Setup
Keep the backend running. Open a new terminal session and start a static web server:
```bash
cd project-quantum
python3 -m http.server 3001 --directory frontend
```
Now, open your browser to **[http://localhost:3001](http://localhost:3001)**. You can input features, execute predictions, and click the chaos buttons.

---

### 🐳 Phase 3: Containerized Deployment (Docker Compose)
Close the local python backend and frontend servers before launching containers to prevent port address collisions.

#### 1. Launch the Stack
Make sure your Docker Desktop application is running, and run this command:
```bash
docker-compose up --build -d
```

#### 2. Verify Services
Check if the 5 containers are running:
```bash
docker-compose ps
```
* **Frontend UI**: `http://localhost:3000`
* **Backend API**: `http://localhost:8000`
* **Prometheus**: `http://localhost:9090`
* **Grafana**: `http://localhost:3002`
* **Vault**: `http://localhost:8200`

#### 3. Stop the Containers
```bash
docker-compose down
```

---

### 📊 Phase 4: Telemetry & Monitoring Setup (Grafana)
1. Navigate to **[http://localhost:3002](http://localhost:3002)** (Log in with `admin` / `admin`).
2. Add a new **Prometheus** data source, set the connection URL to `http://prometheus:9090`, and click **Save & Test**.
3. Import the [grafana-dashboard.json](monitoring/grafana-dashboard.json) file to populate your dashboard charts.

---

### ☁️ Phase 5: Cloud Deployment & CI/CD Operations

#### 1. Cloud Infrastructure (Terraform)
To provision the AWS VPC and EKS cluster automatically:
```bash
cd terraform
terraform init
terraform plan
terraform apply -auto-approve
```
Update your local `kubectl` configuration to point to the new cluster:
```bash
aws eks update-kubeconfig --region us-east-1 --name quantum-eks-cluster
```

#### 2. Kubernetes Deployments
Deploy the namespace, deployment controllers, and NodePort services to the cluster:
```bash
cd k8s
kubectl apply -f namespace.yaml
kubectl apply -f .
```

#### 3. Secret Engine Configuration (Vault)
Setup keys and Kubernetes permissions:
```bash
cd vault
./vault-init.sh
```

---

## ⚡ Chaos Engineering Demo Manual (Screenshots Guide)

Reviewers may simulate traffic anomalies or code updates. Run the following actions on your frontend dashboard to capture verification screenshots:

### 1. High Latency Scenario
* **Action**: Click the **Trigger Latency Loop** button on the panel.
* **Backend Log Result**: Generates a warning block: `"Simulation initiated: Injecting 5 seconds of latency..."`.
* **Telemetry Result**: The Grafana Dashboard *Gateway Latency* statistic card and *95th Percentile Latency* timeline graph will spike.

### 2. HTTP 500 Node Crash Scenario
* **Action**: Click the **Crash API Node** button.
* **Backend Log Result**: Generates a JSON error stacktrace.
* **Telemetry Result**: The Grafana *Failed Requests Rate* gauge and *HTTP Status Codes Traffic* chart will register a red 500 anomaly spike.

### 3. Model Outage & Recovery Scenario
* **Action**: Toggle off the **Loan Approval Endpoint** switch.
* **Inference Result**: Attempting to submit a loan prediction request will instantly fail, displaying a red **HTTP 503 Outage Box**.
* **Telemetry Result**: The *Model Status Outages* metric card increments to `1`, and the *Model Status Telemetry* gauge changes from green (`ACTIVE/ONLINE`) to red (`CRITICAL/OFFLINE`).
* **Recovery Action**: Toggle the switch back on. The status indicators will immediately reset back to online green, and predictions will succeed.
