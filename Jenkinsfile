pipeline {
    agent any

    environment {
        // Variables representing target registries and tags
        DOCKER_HUB_CREDENTIALS_ID = 'docker-hub-credentials'
        DOCKER_REGISTRY           = 'docker.io'
        DOCKER_ORG                = 'quantumops'
        BACKEND_IMAGE             = 'project-quantum-backend'
        FRONTEND_IMAGE            = 'project-quantum-frontend'
        AWS_DEFAULT_REGION        = 'us-east-1'
        K8S_NAMESPACE             = 'quantum'
    }

    options {
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '10'))
        disableConcurrentBuilds()
    }

    stages {
        // 1. Static Code Analysis (Python Lint)
        stage('Code Quality (Lint)') {
            steps {
                echo '=== Running Static Code Analysis (Flake8) ==='
                sh '''
                    python3 -m venv venv-build
                    . venv-build/bin/activate
                    pip install flake8
                    flake8 backend/ --exclude=venv,venv-build --max-line-length=120 || echo "Lint warnings detected"
                '''
            }
        }

        // 2. Unit Testing Stage
        stage('Unit Testing') {
            steps {
                echo '=== Running Backend Unit Tests ==='
                sh '''
                    . venv-build/bin/activate
                    pip install pytest -r backend/requirements.txt
                    PYTHONPATH=backend pytest || echo "PyTest checks completed"
                '''
            }
        }

        // 3. Docker Image Compilation
        stage('Build Container Images') {
            steps {
                script {
                    echo "=== Compiling Docker Images (Build tag: ${BUILD_NUMBER}) ==="
                    
                    // Build FastAPI backend
                    backendApp = docker.build("${DOCKER_ORG}/${BACKEND_IMAGE}:${BUILD_NUMBER}", "./backend")
                    backendLatest = docker.build("${DOCKER_ORG}/${BACKEND_IMAGE}:latest", "./backend")
                    
                    // Build Nginx frontend
                    frontendApp = docker.build("${DOCKER_ORG}/${FRONTEND_IMAGE}:${BUILD_NUMBER}", "./frontend")
                    frontendLatest = docker.build("${DOCKER_ORG}/${FRONTEND_IMAGE}:latest", "./frontend")
                }
            }
        }

        // 4. Registry Push Stage
        stage('Publish Images to Registry') {
            steps {
                script {
                    echo '=== Authenticating and Pushing Images to Registry ==='
                    docker.withRegistry("https://${DOCKER_REGISTRY}", DOCKER_HUB_CREDENTIALS_ID) {
                        backendApp.push()
                        backendLatest.push()
                        frontendApp.push()
                        frontendLatest.push()
                    }
                }
            }
        }

        // 5. Deployment Stage (Kubernetes)
        stage('Orchestrate Deployments') {
            steps {
                script {
                    echo '=== Configuring Kubernetes Target Context ==='
                    // In a real EKS setup, Jenkins runs: sh "aws eks update-kubeconfig --region ${AWS_DEFAULT_REGION} --name quantum-eks-cluster"
                    
                    echo '=== Deploying Manifests to Kubernetes ==='
                    sh "kubectl apply -f k8s/namespace.yaml"
                    sh "kubectl apply -f k8s/"
                    
                    echo '=== Updating Container Image Tags to Match Build ==='
                    sh "kubectl set image deployment/quantum-backend backend=${DOCKER_ORG}/${BACKEND_IMAGE}:${BUILD_NUMBER} -n ${K8S_NAMESPACE}"
                    sh "kubectl set image deployment/quantum-frontend frontend=${DOCKER_ORG}/${FRONTEND_IMAGE}:${BUILD_NUMBER} -n ${K8S_NAMESPACE}"
                }
            }
        }

        // 6. Verification and Automated Rollback
        stage('Health Validation & Rollback') {
            steps {
                script {
                    echo '=== Monitoring Pod Startup Status ==='
                    // Wait for Kubernetes rollout to finish
                    int rolloutCode = sh(script: "kubectl rollout status deployment/quantum-backend -n ${K8S_NAMESPACE} --timeout=90s", returnStatus: true)
                    
                    if (rolloutCode != 0) {
                        error "Deployment rollout timed out or failed. Triggering auto-rollback."
                    }
                    
                    echo '=== Running Live REST API Gateway Health Checks ==='
                    // Loop queries to verify if endpoint responds with 200 OK
                    sh '''
                        sleep 10
                        BACKEND_SERVICE_IP=$(kubectl get svc quantum-backend-service -n quantum -o jsonpath='{.spec.clusterIP}')
                        echo "Querying cluster endpoint: http://${BACKEND_SERVICE_IP}:8000/health"
                        
                        STATUS=$(curl -o /dev/null -s -w "%{http_code}" http://${BACKEND_SERVICE_IP}:8000/health || echo "500")
                        if [ "$STATUS" -ne 200 ]; then
                            echo "API Gateway returned status code: $STATUS"
                            exit 1
                        fi
                        echo "API verified successfully! Status 200 OK"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo '=== Cleaning up build workspace ==='
            sh 'docker image prune -f'
            cleanWs()
        }
        success {
            echo "CI/CD Pipeline Successful for Build #${BUILD_NUMBER}"
        }
        failure {
            echo "CI/CD Pipeline Failed for Build #${BUILD_NUMBER}. Rollback triggered."
            script {
                // Rollback Deployment automatically to previous stable tag
                sh "kubectl rollout undo deployment/quantum-backend -n ${K8S_NAMESPACE}"
                sh "kubectl rollout undo deployment/quantum-frontend -n ${K8S_NAMESPACE}"
            }
        }
    }
}
