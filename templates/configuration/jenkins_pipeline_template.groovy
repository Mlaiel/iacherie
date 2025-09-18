# Jenkins Pipeline Configuration Template for Ainflue Platform
# Comprehensive CI/CD pipeline using Jenkins Declarative Pipeline

pipeline {
    agent {
        kubernetes {
            yaml """
                apiVersion: v1
                kind: Pod
                metadata:
                  labels:
                    jenkins: worker
                spec:
                  serviceAccountName: jenkins
                  containers:
                  - name: node
                    image: node:18-alpine
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - name: docker-sock
                      mountPath: /var/run/docker.sock
                  - name: docker
                    image: docker:24-dind
                    command:
                    - cat
                    tty: true
                    volumeMounts:
                    - name: docker-sock
                      mountPath: /var/run/docker.sock
                    securityContext:
                      privileged: true
                  - name: kubectl
                    image: bitnami/kubectl:latest
                    command:
                    - cat
                    tty: true
                  - name: python
                    image: python:3.11-slim
                    command:
                    - cat
                    tty: true
                  volumes:
                  - name: docker-sock
                    hostPath:
                      path: /var/run/docker.sock
            """
        }
    }

    environment {
        // Application configuration
        APP_NAME = 'ainflue'
        REGISTRY = credentials('docker-registry-url')
        DOCKER_REGISTRY_CREDS = credentials('docker-registry-credentials')
        
        // Version and build info
        BUILD_VERSION = "${env.BUILD_NUMBER}"
        GIT_COMMIT_SHORT = "${env.GIT_COMMIT.take(8)}"
        IMAGE_TAG = "${GIT_COMMIT_SHORT}-${BUILD_VERSION}"
        
        // Environment configuration
        STAGING_NAMESPACE = 'ainflue-staging'
        PRODUCTION_NAMESPACE = 'ainflue-production'
        
        // Kubernetes configuration
        KUBECONFIG = credentials('kubernetes-config')
        
        // Database credentials
        DB_STAGING_CREDS = credentials('db-staging-credentials')
        DB_PRODUCTION_CREDS = credentials('db-production-credentials')
        
        // API keys and tokens
        SLACK_WEBHOOK = credentials('slack-webhook-url')
        GITHUB_TOKEN = credentials('github-token')
        
        // Testing configuration
        COVERAGE_THRESHOLD = '80'
        PERFORMANCE_THRESHOLD = '2000'
        
        // Security scanning
        SECURITY_SCAN_ENABLED = 'true'
        SONARQUBE_TOKEN = credentials('sonarqube-token')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
        timeout(time: 60, unit: 'MINUTES')
        retry(2)
        skipStagesAfterUnstable()
        parallelsAlwaysFailFast()
    }

    triggers {
        githubPush()
        pollSCM('H/5 * * * *')
        cron('H 2 * * 0') // Weekly builds on Sunday at 2 AM
    }

    parameters {
        booleanParam(
            name: 'DEPLOY_TO_PRODUCTION',
            defaultValue: false,
            description: 'Deploy to production after successful staging deployment'
        )
        booleanParam(
            name: 'RUN_PERFORMANCE_TESTS',
            defaultValue: true,
            description: 'Run performance tests on staging environment'
        )
        choice(
            name: 'LOG_LEVEL',
            choices: ['INFO', 'DEBUG', 'WARN', 'ERROR'],
            description: 'Log level for deployment'
        )
    }

    stages {
        stage('Checkout & Setup') {
            steps {
                script {
                    // Checkout code
                    checkout scm
                    
                    // Set dynamic environment variables
                    env.BUILD_TIMESTAMP = new Date().format('yyyy-MM-dd-HHmm')
                    env.BRANCH_NAME_CLEAN = env.BRANCH_NAME.replaceAll(/[^a-zA-Z0-9]/, '-').toLowerCase()
                    
                    // Notify start
                    slackSend(
                        channel: '#deployments',
                        color: '#36a64f',
                        message: "🚀 Starting Ainflue pipeline - Branch: ${env.BRANCH_NAME}, Commit: ${GIT_COMMIT_SHORT}"
                    )
                }
            }
        }

        stage('Code Quality & Validation') {
            parallel {
                stage('Lint & Format Check') {
                    steps {
                        container('node') {
                            sh '''
                                npm ci
                                npm run lint
                                npm run format:check
                                npm run type-check
                            '''
                        }
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: true,
                                keepAll: true,
                                reportDir: 'lint-results',
                                reportFiles: 'index.html',
                                reportName: 'Lint Report'
                            ])
                        }
                    }
                }

                stage('Security Scan - Dependencies') {
                    steps {
                        container('node') {
                            sh '''
                                npm audit --audit-level high
                                npm run security:check
                            '''
                        }
                    }
                }

                stage('Infrastructure Validation') {
                    steps {
                        container('kubectl') {
                            sh '''
                                # Validate Kubernetes manifests
                                for file in kubernetes/*.yaml; do
                                    kubectl --dry-run=client apply -f $file
                                done
                                
                                # Validate Terraform if present
                                if [ -d "infrastructure" ]; then
                                    cd infrastructure
                                    terraform init -backend=false
                                    terraform validate
                                    terraform fmt -check
                                fi
                            '''
                        }
                    }
                }
            }
        }

        stage('Build & Test') {
            parallel {
                stage('Build API Service') {
                    steps {
                        container('node') {
                            sh '''
                                cd services/api
                                npm ci
                                npm run build
                                npm run test:unit -- --coverage --reporter=junit --outputFile=test-results.xml
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'services/api/test-results.xml'
                            publishCoverage adapters: [
                                coberturaAdapter('services/api/coverage/cobertura-coverage.xml')
                            ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                            
                            archiveArtifacts artifacts: 'services/api/dist/**', fingerprint: true
                        }
                    }
                }

                stage('Build Web Service') {
                    steps {
                        container('node') {
                            sh '''
                                cd services/web
                                npm ci
                                npm run build
                                npm run test:unit -- --coverage --reporter=junit --outputFile=test-results.xml
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'services/web/test-results.xml'
                            publishCoverage adapters: [
                                coberturaAdapter('services/web/coverage/cobertura-coverage.xml')
                            ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                            
                            archiveArtifacts artifacts: 'services/web/dist/**', fingerprint: true
                        }
                    }
                }

                stage('Build ML Service') {
                    steps {
                        container('python') {
                            sh '''
                                cd services/ml
                                pip install --upgrade pip
                                pip install -r requirements.txt
                                pip install -r requirements-dev.txt
                                
                                # Code quality checks
                                black --check src/
                                flake8 src/
                                isort --check-only src/
                                
                                # Run tests with coverage
                                pytest tests/ --cov=src --cov-report=xml --cov-report=html --junit-xml=test-results.xml
                                
                                # Type checking
                                mypy src/
                            '''
                        }
                    }
                    post {
                        always {
                            junit 'services/ml/test-results.xml'
                            publishCoverage adapters: [
                                coberturaAdapter('services/ml/coverage.xml')
                            ], sourceFileResolver: sourceFiles('STORE_LAST_BUILD')
                        }
                    }
                }
            }
        }

        stage('Integration Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                    changeRequest()
                }
            }
            steps {
                container('node') {
                    sh '''
                        # Start test services
                        docker-compose -f docker-compose.test.yml up -d
                        
                        # Wait for services to be ready
                        sleep 30
                        
                        # Run integration tests
                        npm run test:integration
                    '''
                }
            }
            post {
                always {
                    sh 'docker-compose -f docker-compose.test.yml down'
                    junit 'integration-test-results.xml'
                }
            }
        }

        stage('Security Scanning') {
            when {
                environment name: 'SECURITY_SCAN_ENABLED', value: 'true'
            }
            parallel {
                stage('SAST Scan') {
                    steps {
                        script {
                            def scannerHome = tool 'SonarQube Scanner'
                            withSonarQubeEnv('SonarQube') {
                                sh """
                                    ${scannerHome}/bin/sonar-scanner \
                                        -Dsonar.projectKey=ainflue \
                                        -Dsonar.projectName=Ainflue \
                                        -Dsonar.projectVersion=${BUILD_VERSION} \
                                        -Dsonar.sources=. \
                                        -Dsonar.exclusions=**/node_modules/**,**/dist/**,**/coverage/** \
                                        -Dsonar.javascript.lcov.reportPaths=*/coverage/lcov.info \
                                        -Dsonar.python.coverage.reportPaths=services/ml/coverage.xml
                                """
                            }
                        }
                    }
                }

                stage('Container Security Scan') {
                    steps {
                        container('docker') {
                            sh '''
                                # Install Trivy
                                curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
                                
                                # Scan project for vulnerabilities
                                trivy fs --security-checks vuln --format sarif --output security-report.sarif .
                            '''
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'security-report.sarif', fingerprint: true
                        }
                    }
                }

                stage('Secret Scanning') {
                    steps {
                        sh '''
                            # Install and run GitLeaks
                            wget -O gitleaks.tar.gz https://github.com/zricethezav/gitleaks/releases/download/v8.18.0/gitleaks_8.18.0_linux_x64.tar.gz
                            tar -xzf gitleaks.tar.gz
                            ./gitleaks detect --source . --report-format sarif --report-path gitleaks-report.sarif
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'gitleaks-report.sarif', fingerprint: true
                        }
                    }
                }
            }
        }

        stage('Build Docker Images') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            parallel {
                stage('Build API Image') {
                    steps {
                        container('docker') {
                            script {
                                def apiImage = docker.build("${REGISTRY}/ainflue-api:${IMAGE_TAG}", "services/api")
                                docker.withRegistry("https://${REGISTRY}", "${DOCKER_REGISTRY_CREDS}") {
                                    apiImage.push()
                                    apiImage.push("latest")
                                }
                            }
                        }
                    }
                }

                stage('Build Web Image') {
                    steps {
                        container('docker') {
                            script {
                                def webImage = docker.build("${REGISTRY}/ainflue-web:${IMAGE_TAG}", "services/web")
                                docker.withRegistry("https://${REGISTRY}", "${DOCKER_REGISTRY_CREDS}") {
                                    webImage.push()
                                    webImage.push("latest")
                                }
                            }
                        }
                    }
                }

                stage('Build ML Image') {
                    steps {
                        container('docker') {
                            script {
                                def mlImage = docker.build("${REGISTRY}/ainflue-ml:${IMAGE_TAG}", "services/ml")
                                docker.withRegistry("https://${REGISTRY}", "${DOCKER_REGISTRY_CREDS}") {
                                    mlImage.push()
                                    mlImage.push("latest")
                                }
                            }
                        }
                    }
                }
            }
        }

        stage('Deploy to Staging') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                container('kubectl') {
                    withCredentials([kubeconfigFile(credentialsId: 'kubernetes-config', variable: 'KUBECONFIG')]) {
                        sh '''
                            # Deploy to staging
                            kubectl set image deployment/ainflue-api \
                                ainflue-api=${REGISTRY}/ainflue-api:${IMAGE_TAG} \
                                --namespace=${STAGING_NAMESPACE}
                            
                            kubectl set image deployment/ainflue-web \
                                ainflue-web=${REGISTRY}/ainflue-web:${IMAGE_TAG} \
                                --namespace=${STAGING_NAMESPACE}
                            
                            kubectl set image deployment/ainflue-ml \
                                ainflue-ml=${REGISTRY}/ainflue-ml:${IMAGE_TAG} \
                                --namespace=${STAGING_NAMESPACE}
                            
                            # Wait for rollout to complete
                            kubectl rollout status deployment/ainflue-api --namespace=${STAGING_NAMESPACE} --timeout=300s
                            kubectl rollout status deployment/ainflue-web --namespace=${STAGING_NAMESPACE} --timeout=300s
                            kubectl rollout status deployment/ainflue-ml --namespace=${STAGING_NAMESPACE} --timeout=300s
                            
                            # Verify deployment
                            kubectl get pods --namespace=${STAGING_NAMESPACE}
                        '''
                    }
                }
            }
        }

        stage('Staging Tests') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            parallel {
                stage('Smoke Tests') {
                    steps {
                        container('node') {
                            sh '''
                                export API_BASE_URL="https://api.staging.ainflue.com"
                                export WEB_BASE_URL="https://staging.ainflue.com"
                                npm run test:smoke
                            '''
                        }
                    }
                }

                stage('E2E Tests') {
                    steps {
                        container('node') {
                            sh '''
                                export API_BASE_URL="https://api.staging.ainflue.com"
                                export WEB_BASE_URL="https://staging.ainflue.com"
                                npm run test:e2e:staging
                            '''
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'e2e-results/**', fingerprint: true
                        }
                    }
                }

                stage('Performance Tests') {
                    when {
                        environment name: 'RUN_PERFORMANCE_TESTS', value: 'true'
                    }
                    steps {
                        sh '''
                            # Install k6
                            curl -s https://github.com/grafana/k6/releases/download/v0.46.0/k6-v0.46.0-linux-amd64.tar.gz | tar -xz --strip-components=1
                            
                            # Run performance tests
                            ./k6 run --vus 50 --duration 5m performance/load-test.js
                            ./k6 run --vus 100 --duration 2m performance/stress-test.js
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'performance-results/**', fingerprint: true
                        }
                    }
                }
            }
        }

        stage('Deploy to Production') {
            when {
                allOf {
                    branch 'main'
                    anyOf {
                        environment name: 'DEPLOY_TO_PRODUCTION', value: 'true'
                        triggeredBy 'UserIdCause'
                    }
                }
            }
            steps {
                timeout(time: 5, unit: 'MINUTES') {
                    input message: 'Deploy to production?', ok: 'Deploy',
                          submitterParameter: 'DEPLOYER'
                }
                
                container('kubectl') {
                    withCredentials([kubeconfigFile(credentialsId: 'kubernetes-config', variable: 'KUBECONFIG')]) {
                        sh '''
                            # Deploy to production
                            kubectl set image deployment/ainflue-api \
                                ainflue-api=${REGISTRY}/ainflue-api:${IMAGE_TAG} \
                                --namespace=${PRODUCTION_NAMESPACE}
                            
                            kubectl set image deployment/ainflue-web \
                                ainflue-web=${REGISTRY}/ainflue-web:${IMAGE_TAG} \
                                --namespace=${PRODUCTION_NAMESPACE}
                            
                            kubectl set image deployment/ainflue-ml \
                                ainflue-ml=${REGISTRY}/ainflue-ml:${IMAGE_TAG} \
                                --namespace=${PRODUCTION_NAMESPACE}
                            
                            # Wait for rollout to complete
                            kubectl rollout status deployment/ainflue-api --namespace=${PRODUCTION_NAMESPACE} --timeout=600s
                            kubectl rollout status deployment/ainflue-web --namespace=${PRODUCTION_NAMESPACE} --timeout=600s
                            kubectl rollout status deployment/ainflue-ml --namespace=${PRODUCTION_NAMESPACE} --timeout=600s
                            
                            # Verify deployment
                            kubectl get pods --namespace=${PRODUCTION_NAMESPACE}
                        '''
                    }
                }
            }
        }

        stage('Production Smoke Tests') {
            when {
                branch 'main'
            }
            steps {
                container('node') {
                    sh '''
                        export API_BASE_URL="https://api.ainflue.com"
                        export WEB_BASE_URL="https://app.ainflue.com"
                        npm run test:smoke:production
                    '''
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }
        
        success {
            slackSend(
                channel: '#deployments',
                color: 'good',
                message: "✅ Ainflue pipeline completed successfully! Branch: ${env.BRANCH_NAME}, Commit: ${GIT_COMMIT_SHORT}, Build: ${BUILD_NUMBER}"
            )
        }
        
        failure {
            slackSend(
                channel: '#deployments',
                color: 'danger',
                message: "❌ Ainflue pipeline failed! Branch: ${env.BRANCH_NAME}, Commit: ${GIT_COMMIT_SHORT}, Build: ${BUILD_NUMBER}, Check: ${BUILD_URL}"
            )
        }
        
        unstable {
            slackSend(
                channel: '#deployments',
                color: 'warning',
                message: "⚠️ Ainflue pipeline is unstable! Branch: ${env.BRANCH_NAME}, Commit: ${GIT_COMMIT_SHORT}, Build: ${BUILD_NUMBER}"
            )
        }
    }
}