#!/bin/sh
# vault-init.sh
# Automated CLI script to configure the Vault developer container.

set -e

echo "=== A. Checking Vault Server Status ==="
vault status

echo "=== B. Enabling Key-Value Secrets Engine (KV-v2) ==="
# Enable kv-v2 engine under the secret/ path if not already enabled
vault secrets enable -path=secret kv-v2 || echo "KV engine already enabled"

echo "=== C. Writing Application Secrets into Key-Value Store ==="
vault kv put secret/quantum/api-keys \
  loan_approval_api_key="sk-loan-923847293" \
  monitoring_alert_webhook="https://hooks.slack.com/services/T00/B00/X00"

vault kv put secret/quantum/db-credentials \
  db_user="quantum_admin" \
  db_password="SuperSecureDBPassword2026!"

echo "=== D. Applying Security Access Policies ==="
# Load the Policy file
vault policy write quantum-app-policy /vault/policies/app-policy.hcl

echo "=== E. Configuring Kubernetes ServiceAccount Token-Review Auth ==="
# Enable Kubernetes authentication path
vault auth enable kubernetes || echo "Kubernetes Auth already enabled"

vault write auth/kubernetes/config \
    kubernetes_host="https://kubernetes.default.svc:443" \
    disable_local_ca_jwt=true

# Create a role binding a ServiceAccount (in the 'quantum' namespace) to the policy
vault write auth/kubernetes/role/quantum-app-role \
    bound_service_account_names=quantum-backend-sa \
    bound_service_account_namespaces=quantum \
    policies=quantum-app-policy \
    ttl=24h

echo "Vault Setup Completed Successfully!"
