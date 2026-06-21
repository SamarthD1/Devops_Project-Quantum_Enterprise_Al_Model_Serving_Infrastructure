# Project Quantum - Enterprise AI Model Serving Infrastructure

Project Quantum is a production-grade, zero-trust, self-healing, and highly observable MLOps and DevOps ecosystem designed to serve machine learning models at scale. The platform serves three active ML models (Loan Approval, House Valuation, Customer Churn) in real time while demonstrating core DevOps lifecycle features: containerization, infrastructure automation, CI/CD pipelines, secret management, centralized logging, and interactive metrics monitoring with chaos simulations.

---

## 📂 Repository File Structure
```text
project-quantum/
├── docker-compose.yml         # Core app & services orchestration (frontend, backend, vault, prometheus, grafana)
├── docker-compose-elk.yml     # Centralized ELK stack orchestration (elasticsearch, logstash, kibana)
├── Jenkinsfile                # Declarative CI/CD pipeline automation (build, test, deploy, rollback)
├── backend/
│   ├── Dockerfile             # Hardened backend containerization config (non-root runner user)
│   ├── main.py                # FastAPI server (predictions, logging, metrics, chaos)
│   ├── model_loader.py        # Joblib loading class & toggle state manager
│   ├── requirements.txt       # Backend Python dependencies
│   ├── models/                # Serialized model pickle files (.pkl)
│   ├── logs/                  # Local runtime logs
│   ├── schemas/               # Pydantic input validation schemas
│   └── utils/
│       ├── logger.py          # Structured JSON logging formatter
│       └── train_models.py    # Offline ML model training script
├── frontend/
│   ├── Dockerfile             # Frontend Nginx serving container config
│   ├── index.html             # Main dashboard console and chaos controller
│   ├── style.css              # Custom responsive dark-theme stylesheet
│   ├── script.js              # Predictions form handler, latency logs, and status polling
│   └── pages/
│       └── registry.html      # Model registry metadata catalog
├── monitoring/
│   ├── Dockerfile             # Custom Prometheus container definition
│   ├── prometheus.yml         # Telemetry scraping config (every 5 seconds)
│   └── grafana-dashboard.json # Visual dashboards model template import
├── logging/
│   ├── logstash.conf          # ELK logs parsing pipeline
│   ├── elasticsearch.yml      # Elasticsearch cluster settings
│   └── kibana.yml             # Kibana console configurations
├── vault/
│   ├── vault-init.sh          # Secrets engine setup script
│   └── app-policy.hcl         # Vault access policy restriction rules
├── terraform/
│   ├── main.tf                # AWS VPC & EKS cluster provisioning IaC
│   ├── variables.tf           # Terraform input variables
│   └── outputs.tf             # Terraform output attributes
├── k8s/
│   ├── namespace.yaml         # Isolated 'quantum' cluster namespace
│   ├── backend-deployment.yaml# Backend app replica sets, services, and HPA configuration
│   ├── frontend-deployment.yaml# Frontend web console deployment and NodePort service
│   ├── ingress.yaml           # Ingress HTTP path routing rules
│   ├── prometheus-setup.yaml  # ClusterRole, ServiceAccount, and Prometheus deployment
│   └── grafana-setup.yaml     # Grafana metrics dashboard deployment manifest
├── ARCHITECTURE.md            # Visual architecture and deployment topology diagrams
└── DISASTER_RECOVERY.md       # DR metrics (RTO/RPO), backups, and restore operations
```

---

## 🛠️ Prerequisites
* **Python 3.10+** (for local backend development)
* **Docker Desktop** (v20.10+ with Compose support)
* **kubectl CLI** (configured locally)
* **minikube** (configured with the docker driver)
* **Terraform** (v1.5+ for AWS infrastructure automation)
* **pandoc** (optional, for compiling documentation reports)

---

## 🐍 Setup & Local Installation
1. **Initialize Virtual Environment**:
   Navigate to the project root and create a Python sandbox environment:
   ```bash
   cd project-quantum
   python3 -m venv venv
   source venv/bin/activate
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. **Train and Serialize ML Models**:
   Run the training script to generate `.pkl` files inside `backend/models/`:
   ```bash
   python3 backend/utils/train_models.py
   ```
4. **Start the Backend API**:
   ```bash
   cd backend
   python3 -m uvicorn main:app --reload --port 8000 --host 127.0.0.1
   ```
   * **Docs GUI**: `http://localhost:8000/docs`
   * **Health API**: `http://localhost:8000/health`
5. **Start the Frontend Static Server**:
   Open a new terminal window and run:
   ```bash
   cd project-quantum
   python3 -m http.server 3001 --directory frontend
   ```
   Access the dashboard console at `http://localhost:3001`.

---

## 🐳 Running with Docker
Ensure your local Docker Desktop daemon is running.

1. **Start the Core Application & Observability Stack**:
   Build the Dockerfiles and spin up the backend, frontend, Vault, Prometheus, and Grafana containers:
   ```bash
   docker compose up --build -d
   ```
2. **Start the Centralized Logging Stack (ELK)**:
   ```bash
   docker compose -f docker-compose-elk.yml up --build -d
   ```
3. **Verify running containers**:
   ```bash
   docker compose ps
   ```
   * **Frontend UI**: `http://localhost:3000`
   * **Backend API**: `http://localhost:8000`
   * **Prometheus Dashboard**: `http://localhost:9090`
   * **Grafana Panels**: `http://localhost:3002` (Login: `admin` / `admin`)
   * **Kibana logs discover**: `http://localhost:5601`
   * **Vault Secrets Console**: `http://localhost:8200`
4. **Stop the entire container stack**:
   ```bash
   docker compose down
   docker compose -f docker-compose-elk.yml down
   ```

---

## ☸️ Running on Kubernetes (Local with Minikube)

1. **Start the Local Cluster**:
   ```bash
   minikube start
   ```
2. **Expose Host Docker Registry**:
   Point your terminal environment shell to Minikube's internal Docker daemon:
   ```bash
   eval $(minikube docker-env)
   ```
3. **Build the Local Images directly in the Cluster Registry**:
   ```bash
   docker build -t project-quantum-backend:local ./backend
   docker build -t project-quantum-frontend:local ./frontend
   ```
4. **Deploy Manifests**:
   ```bash
   kubectl apply -f k8s/
   ```
5. **Access services via Port-Forwarding**:
   Route ports from your local host machine to the cluster namespace services:
   ```bash
   kubectl port-forward svc/quantum-frontend-service 3000:80 -n quantum &
   kubectl port-forward svc/quantum-backend-service 8000:8000 -n quantum &
   kubectl port-forward svc/prometheus-service 9090:9090 -n quantum &
   kubectl port-forward svc/grafana-service 3002:3000 -n quantum &
   ```
   Now access the frontend console at `http://localhost:3000`.

6. **Demonstrating Self-Healing & Autoscaling**:
   * **Self-Healing**: Delete an active backend pod:
     ```bash
     kubectl delete pod <pod-name> -n quantum
     ```
     Immediately query `kubectl get pods -n quantum`. Kubernetes automatically provisions a replacement container to restore target replicas to 100% capacity.
   * **Autoscaling (HPA)**: View active autoscaler policies:
     ```bash
     kubectl get hpa -n quantum
     ```
     Under load testing, the metrics-server triggers replication scaling (up to 10 replicas) to protect against resource exhaustion.

---

## 🏗️ Infrastructure as Code (Terraform)
Automates provisioning of target resources, transitioning from local clusters to cloud infrastructure.

1. **Initialize and Provision AWS VPC & EKS resources**:
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply -auto-approve
   ```
2. **Apply Local Kubeconfig Update**:
   ```bash
   aws eks update-kubeconfig --region us-east-1 --name quantum-eks-cluster
   ```
3. **Destroy AWS Infrastructure resources**:
   ```bash
   terraform destroy -auto-approve
   ```

---

## 🔁 CI/CD Pipeline (Jenkins)
Defined in a declarative `Jenkinsfile` automate the validation lifecycle on commits.

### Pipeline Stages
1. **Code Quality (Lint)**: Performs Python static code analysis using `flake8`.
2. **Unit Testing**: Executes test suites using `pytest` to verify model loader modules.
3. **Build Container Images**: Compiles version-tagged and `latest` backend and frontend images.
4. **Publish Images**: Skips/mocks pushing images to registries for local deployments.
5. **Orchestrate Deployments**: Applies declarative manifests (`kubectl apply -f k8s/`).
6. **Health Validation & Rollback**:
   * Inspects pod startup statuses via `kubectl rollout status --timeout=90s`.
   * Pings backend HTTP API `/health` endpoints.
   * If a timeout or non-200 HTTP code is detected, it triggers an automated rollback to the previous stable build revision:
     ```bash
     kubectl rollout undo deployment/quantum-backend -n quantum
     ```

### One-Time Local Setup Instructions
1. **Unlock Jenkins**:
   * Open `http://localhost:8080` in your web browser.
   * Input the initial administrator password (retrieved during local run setups).
   * Install the suggested plugins.
2. **Add Docker Hub Credentials**:
   * Navigate to `Manage Jenkins` → `Credentials` → `System` → `Global credentials`.
   * Add credentials with ID `docker-hub-credentials`, utilizing your Docker Hub username and Access Token.
3. **Configure SCM Polling**:
   * Setup a new Pipeline item in the Jenkins dashboard.
   * Under pipeline definitions, choose `Pipeline script from SCM` using git repository details.
   * Enable SCM polling with cron schedule `H/2 * * * *` to poll for commits every 2 minutes.

---

## ⚡ Chaos Engineering Simulations
Reviewers may trigger anomalies from the frontend dashboard control panel or utilize the following API requests:

1. **High Latency Simulation**:
   ```bash
   curl -X POST http://localhost:8000/simulate/high-latency
   ```
   * *Outcome*: Injects a 5-second sleep block in FastAPI threads. Latency timelines in Grafana immediately show a metric spike.
2. **HTTP 500 server Error Simulation**:
   ```bash
   curl -X POST http://localhost:8000/simulate/error
   ```
   * *Outcome*: Raises an unhandled exception. Logstash captures and indexes the stack trace, showing the error event inside Kibana search panels.
3. **Model Outage Simulation**:
   ```bash
   curl -X POST "http://localhost:8000/simulate/model-failure?model=loan&action=disable"
   ```
   * *Outcome*: Marks the loan model status as offline. Predictions return `HTTP 503 Service Unavailable` immediately. Re-enabling the model restores normal traffic.
