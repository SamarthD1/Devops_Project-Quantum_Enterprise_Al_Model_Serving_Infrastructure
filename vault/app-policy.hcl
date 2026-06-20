# Permit read-only access to Project Quantum application secrets
path "secret/data/quantum/api-keys" {
  capabilities = ["read"]
}

# Permit read-only access to dynamic database credentials
path "secret/data/quantum/db-credentials" {
  capabilities = ["read"]
}
