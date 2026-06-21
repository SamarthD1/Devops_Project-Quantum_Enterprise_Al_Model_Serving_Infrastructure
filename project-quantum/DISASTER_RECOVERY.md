# Disaster Recovery (DR) Plan - Project Quantum

This document outlines the backup protocols, failover strategies, and recovery procedures designed to ensure high availability and data integrity for the **Project Quantum** AI Model Serving Infrastructure.

---

## 1. Objectives & Metrics
* **RTO (Recovery Time Objective)**: `< 15 minutes` (target time to restore services after a major incident).
* **RPO (Recovery Point Objective)**: `< 1 hour` (maximum data loss window in the event of a total system failure).

---

## 2. High Availability (HA) Architecture
* **Multi-AZ EKS Deployment**: Managed Node Groups scale across three availability zones.
* **Database & PV Replication**: AWS EBS Volumes are replicated synchronously across AZs.
* **Vault Multi-Node Raft Cluster**: Vault utilizes integrated Raft storage with nodes distributed across subnets.
* **Auto-Scaling (HPA)**: Kubernetes HPAs scale application pods up to 10 replicas in traffic surges to prevent OOM outages.

---

## 3. Automated Backup Procedures

### A. Kubernetes Cluster State Backup (ETCD)
Etcd backups capture the state of all deployments, services, policies, and secrets.
```bash
# Capture a snapshot of the active etcd database state
ETCDCTL_API=3 etcdctl \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  snapshot save /backups/etcd-snapshot-$(date +%F-%H%M).db
```
* **Frequency**: Automated cron job runs every 4 hours.
* **Retention**: Backups are copied to a secure AWS S3 bucket with a 30-day lifecycle expiration policy.

### B. Vault Storage Engine Backup
Raft integrated storage is backed up directly using Vault Operator commands:
```bash
# Export Raft storage snapshot
export VAULT_TOKEN="my-root-token"
export VAULT_ADDR="http://127.0.0.1:8200"
vault operator raft snapshot save /backups/vault-raft-$(date +%F-%H%M).snap
```
* **Frequency**: Automated daily cron task.

### C. Application Logs & Metrics
* Logs are pushed continuously to the centralized **ELK Stack** indices.
* Prometheus metrics are stored on persistent volumes (EBS) with snapshot policies.

---

## 4. Disaster Recovery & Restoration Procedures

### Scenario A: Accidental Application Code Deployment Failure
If a corrupted model version or code update causes pods to crash or health checks to fail:
```bash
# 1. Rollback the backend deployment instantly to the last stable state
kubectl rollout undo deployment/quantum-backend -n quantum

# 2. Monitor recovery status
kubectl rollout status deployment/quantum-backend -n quantum
```

### Scenario B: Total Cluster Outage (Re-creation from Infrastructure-as-Code)
If the EKS cluster is destroyed or compromised:
1. **Re-provision AWS Infrastructure**:
   ```bash
   cd terraform
   terraform init
   terraform apply -auto-approve
   ```
2. **Configure Connection Context**:
   ```bash
   aws eks update-kubeconfig --region us-east-1 --name quantum-eks-cluster
   ```
3. **Restore Kubernetes Manifests**:
   ```bash
   cd ../k8s
   kubectl apply -f namespace.yaml
   kubectl apply -f .
   ```
4. **Restore Vault Raft Storage**:
   * Deploy Vault in the new cluster.
   * Restore configuration state:
     ```bash
     vault operator raft snapshot restore /backups/vault-raft-latest.snap
     ```
   * Input the required unseal keys to activate Vault.

---

## 5. Simulation & Testing Schedule
* **DR Drill Frequency**: Semi-annually.
* **Testing Scope**: Simulated EKS node deletion, Vault state restorations, and deployment rollbacks.
