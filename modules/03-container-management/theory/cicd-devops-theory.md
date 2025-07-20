# CI/CD Pipeline Theory và DevOps Practices

## 1. Continuous Integration/Continuous Deployment Fundamentals

### 1.1 CI/CD Concepts và Philosophy

#### Continuous Integration (CI)
CI là practice của việc integrate code changes vào shared repository thường xuyên, thường là nhiều lần trong ngày.

**Core Principles:**
```yaml
ci_principles:
  frequent_integration:
    description: "Developers integrate code changes frequently"
    frequency: "Multiple times per day"
    benefits:
      - Early detection of integration issues
      - Reduced merge conflicts
      - Faster feedback cycles
      
  automated_builds:
    description: "Every integration triggers automated build"
    components:
      - Source code compilation
      - Dependency resolution
      - Unit test execution
      - Static code analysis
      
  fast_feedback:
    description: "Quick notification of build status"
    targets:
      - Build completion within 10 minutes
      - Immediate notification on failure
      - Clear error reporting
```

**CI Pipeline Stages:**
```bash
# Typical CI pipeline flow
1. Source Code Management (SCM) Trigger
   ├── Git webhook on push/merge
   ├── Branch protection rules
   └── Commit message validation

2. Build Stage
   ├── Environment provisioning
   ├── Dependency installation
   ├── Code compilation
   └── Artifact generation

3. Test Stage
   ├── Unit tests
   ├── Integration tests
   ├── Code coverage analysis
   └── Security scanning

4. Quality Gates
   ├── Code quality metrics
   ├── Test coverage thresholds
   ├── Security vulnerability checks
   └── Performance benchmarks

5. Artifact Management
   ├── Binary storage
   ├── Image building and pushing
   ├── Metadata tagging
   └── Artifact promotion
```

#### Continuous Deployment (CD)
CD extends CI by automatically deploying successful builds to production.

**Deployment Strategies:**
```yaml
deployment_strategies:
  blue_green:
    description: "Two identical production environments"
    process:
      1. Deploy to inactive environment (green)
      2. Test green environment thoroughly
      3. Switch traffic from blue to green
      4. Keep blue as rollback option
    advantages:
      - Zero downtime deployment
      - Easy rollback
      - Full testing before switch
    disadvantages:
      - Resource duplication
      - Complex data synchronization
      
  canary_deployment:
    description: "Gradual rollout to subset of users"
    process:
      1. Deploy new version to small subset (5%)
      2. Monitor metrics and user feedback
      3. Gradually increase traffic to new version
      4. Complete rollout or rollback based on metrics
    advantages:
      - Risk mitigation
      - Real user testing
      - Gradual validation
    disadvantages:
      - Complex routing logic
      - Longer deployment time
      
  rolling_deployment:
    description: "Sequential replacement of instances"
    process:
      1. Deploy new version to one instance
      2. Verify health and functionality
      3. Repeat for remaining instances
      4. Monitor overall system health
    advantages:
      - Resource efficient
      - Built-in rollback capability
      - Gradual migration
    disadvantages:
      - Temporary capacity reduction
      - Version inconsistency during deployment
```

### 1.2 DevOps Culture và Practices

#### DevOps Principles
```yaml
devops_culture:
  collaboration:
    traditional_model: "Dev throws code over wall to Ops"
    devops_model: "Shared responsibility for entire lifecycle"
    practices:
      - Cross-functional teams
      - Shared metrics and goals
      - Joint incident response
      
  automation:
    philosophy: "Automate repetitive, error-prone tasks"
    areas:
      - Infrastructure provisioning
      - Application deployment
      - Testing and validation
      - Monitoring and alerting
      
  measurement:
    key_metrics:
      - Deployment frequency
      - Lead time for changes
      - Time to restore service
      - Change failure rate
      
  sharing:
    knowledge_transfer:
      - Documentation as code
      - Post-mortem culture
      - Internal tech talks
      - Cross-training initiatives
```

#### Infrastructure as Code (IaC)
```yaml
iac_principles:
  declarative_configuration:
    approach: "Describe desired state, not steps"
    benefits:
      - Predictable outcomes
      - Easier reasoning about infrastructure
      - Better version control
      
  version_control:
    requirements:
      - All infrastructure code in SCM
      - Branching strategy for environments
      - Code review process
      - Change tracking and rollback
      
  testing:
    levels:
      - Syntax validation
      - Unit tests for modules
      - Integration tests
      - Policy compliance checks
      
  environments:
    consistency:
      - Same code for all environments
      - Environment-specific variables
      - Promotion pipeline dev->staging->prod
```

## 2. GitLab CI/CD Deep Dive

### 2.1 Pipeline Architecture

#### .gitlab-ci.yml Structure
```yaml
# Complete GitLab CI/CD pipeline example
stages:
  - validate
  - build
  - test
  - security
  - deploy
  - post-deploy

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  REGISTRY: $CI_REGISTRY_IMAGE
  TAG: $CI_COMMIT_SHORT_SHA

# Templates for reusability
.docker_template: &docker_template
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY

.kubernetes_template: &kubernetes_template
  image: bitnami/kubectl:latest
  before_script:
    - kubectl config use-context $KUBE_CONTEXT
    - kubectl config set-cluster k8s --server="$KUBE_URL" --certificate-authority="$KUBE_CA_PEM_FILE"
    - kubectl config set-credentials gitlab --token="$KUBE_TOKEN"

# Validation stage
validate:syntax:
  stage: validate
  image: node:16-alpine
  script:
    - npm install --only=dev
    - npm run lint
    - npm run type-check
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

validate:dockerfile:
  stage: validate
  image: hadolint/hadolint:latest-debian
  script:
    - hadolint Dockerfile
  rules:
    - changes:
        - Dockerfile

# Build stage
build:application:
  <<: *docker_template
  stage: build
  script:
    - docker build --pull -t $REGISTRY:$TAG .
    - docker push $REGISTRY:$TAG
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# Test stage
test:unit:
  stage: test
  image: node:16-alpine
  services:
    - redis:6-alpine
    - postgres:13-alpine
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_pass
    REDIS_URL: redis://redis:6379
  script:
    - npm ci
    - npm run test:unit
    - npm run test:integration
  coverage: '/Coverage: \d+\.\d+%/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
      junit: junit.xml
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

test:e2e:
  stage: test
  image: cypress/included:10.8.0
  services:
    - name: $REGISTRY:$TAG
      alias: app
  variables:
    CYPRESS_baseUrl: http://app:3000
  script:
    - cypress run --record --key $CYPRESS_RECORD_KEY
  artifacts:
    when: always
    paths:
      - cypress/screenshots
      - cypress/videos
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Security stage
security:sast:
  stage: security
  include:
    - template: Security/SAST.gitlab-ci.yml
  variables:
    SAST_EXCLUDED_PATHS: "spec,test,tests,tmp"
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

security:dependency_scanning:
  stage: security
  include:
    - template: Security/Dependency-Scanning.gitlab-ci.yml
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

security:container_scanning:
  stage: security
  include:
    - template: Security/Container-Scanning.gitlab-ci.yml
  variables:
    CS_IMAGE: $REGISTRY:$TAG
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Deploy stages
deploy:staging:
  <<: *kubernetes_template
  stage: deploy
  environment:
    name: staging
    url: https://staging.example.com
    deployment_tier: staging
  script:
    - envsubst < k8s/deployment.yml | kubectl apply -f -
    - kubectl rollout status deployment/app -n staging
    - kubectl get services -n staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

deploy:production:
  <<: *kubernetes_template
  stage: deploy
  environment:
    name: production
    url: https://production.example.com
    deployment_tier: production
  script:
    - envsubst < k8s/deployment.yml | kubectl apply -f -
    - kubectl rollout status deployment/app -n production
  when: manual
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Post-deploy validation
post-deploy:health-check:
  stage: post-deploy
  image: curlimages/curl:latest
  script:
    - curl -f $CI_ENVIRONMENT_URL/health || exit 1
    - curl -f $CI_ENVIRONMENT_URL/metrics || exit 1
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: always

post-deploy:performance:
  stage: post-deploy
  image: grafana/k6:latest
  script:
    - k6 run --out influxdb=http://influxdb:8086/k6 performance/load-test.js
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
      when: always
```

#### Advanced Pipeline Features

**Dynamic Child Pipelines:**
```yaml
# Parent pipeline
generate:child-pipeline:
  stage: generate
  script:
    - python scripts/generate-pipeline.py > child-pipeline.yml
  artifacts:
    paths:
      - child-pipeline.yml

trigger:child-pipeline:
  stage: deploy
  trigger:
    include:
      - artifact: child-pipeline.yml
        job: generate:child-pipeline
    strategy: depend

# Generated child pipeline (dynamic content)
# child-pipeline.yml
stages:
  - deploy-microservices

deploy:service-a:
  stage: deploy-microservices
  script:
    - kubectl apply -f k8s/service-a/
    
deploy:service-b:
  stage: deploy-microservices
  script:
    - kubectl apply -f k8s/service-b/
```

**Multi-project Pipelines:**
```yaml
# Trigger downstream projects
trigger:integration-tests:
  stage: integration
  trigger:
    project: group/integration-test-suite
    branch: main
    strategy: depend
  variables:
    UPSTREAM_PROJECT_NAME: $CI_PROJECT_NAME
    UPSTREAM_COMMIT_SHA: $CI_COMMIT_SHA

# Cross-project dependencies
deploy:microservice:
  stage: deploy
  needs:
    - project: group/shared-library
      job: build:library
      ref: main
      artifacts: true
```

### 2.2 GitLab Runner Architecture

#### Runner Types và Configuration
```yaml
runner_types:
  shared_runners:
    description: "Available to all projects in GitLab instance"
    use_cases:
      - Standard CI/CD workflows
      - Open source projects
      - Cost-effective for small teams
    limitations:
      - Limited customization
      - Shared resource pool
      - Security considerations
      
  group_runners:
    description: "Available to all projects in a group"
    use_cases:
      - Organization-wide standards
      - Shared infrastructure
      - Group-level compliance
    benefits:
      - Better resource control
      - Group-specific configurations
      - Consistent environments
      
  project_runners:
    description: "Dedicated to specific project"
    use_cases:
      - High-security environments
      - Custom hardware requirements
      - Performance-critical workloads
    benefits:
      - Complete control
      - Custom configurations
      - Isolated execution

# Runner configuration
# /etc/gitlab-runner/config.toml
concurrent = 4
check_interval = 0

[session_server]
  session_timeout = 1800

[[runners]]
  name = "docker-runner"
  url = "https://gitlab.example.com/"
  token = "RUNNER_TOKEN"
  executor = "docker"
  [runners.custom_build_dir]
  [runners.cache]
    [runners.cache.s3]
      ServerAddress = "s3.amazonaws.com"
      BucketName = "gitlab-runner-cache"
      BucketLocation = "us-west-2"
  [runners.docker]
    tls_verify = false
    image = "alpine:latest"
    privileged = false
    disable_entrypoint_overwrite = false
    oom_kill_disable = false
    disable_cache = false
    volumes = ["/cache", "/var/run/docker.sock:/var/run/docker.sock:rw"]
    shm_size = 0
```

#### Executor Types
```yaml
executors:
  docker:
    description: "Run jobs in Docker containers"
    advantages:
      - Isolated environments
      - Consistent dependencies
      - Easy cleanup
      - Scalable
    configuration:
      image: "node:16-alpine"
      services: ["redis:6", "postgres:13"]
      volumes: ["/cache"]
      
  kubernetes:
    description: "Run jobs in Kubernetes pods"
    advantages:
      - Auto-scaling
      - Resource management
      - Cloud-native integration
      - High availability
    configuration:
      namespace: "gitlab-runner"
      image: "ubuntu:20.04"
      cpu_limit: "1"
      memory_limit: "2Gi"
      
  shell:
    description: "Run jobs directly on runner machine"
    advantages:
      - Direct system access
      - No containerization overhead
      - Full hardware access
    disadvantages:
      - Security risks
      - Environment pollution
      - Dependency conflicts
      
  ssh:
    description: "Run jobs on remote machines via SSH"
    use_cases:
      - Legacy system deployment
      - Physical hardware testing
      - Remote development environments
```

## 3. Jenkins Pipeline Architecture

### 3.1 Pipeline as Code

#### Declarative Pipeline
```groovy
// Jenkinsfile - Declarative Pipeline
pipeline {
    agent {
        kubernetes {
            yaml """
                apiVersion: v1
                kind: Pod
                spec:
                  containers:
                  - name: docker
                    image: docker:20.10.16-dind
                    securityContext:
                      privileged: true
                  - name: kubectl
                    image: bitnami/kubectl:latest
                    command:
                    - cat
                    tty: true
                  - name: node
                    image: node:16-alpine
                    command:
                    - cat
                    tty: true
            """
        }
    }
    
    environment {
        REGISTRY = credentials('docker-registry')
        KUBECONFIG = credentials('kubeconfig')
        SONAR_TOKEN = credentials('sonar-token')
    }
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 1, unit: 'HOURS')
        retry(3)
        skipStagesAfterUnstable()
    }
    
    triggers {
        pollSCM('H/5 * * * *')  // Poll every 5 minutes
        cron('H 2 * * *')       // Daily build at 2 AM
        upstream(upstreamProjects: 'shared-library', threshold: hudson.model.Result.SUCCESS)
    }
    
    parameters {
        choice(
            name: 'ENVIRONMENT',
            choices: ['dev', 'staging', 'production'],
            description: 'Target environment'
        )
        booleanParam(
            name: 'SKIP_TESTS',
            defaultValue: false,
            description: 'Skip test execution'
        )
        string(
            name: 'IMAGE_TAG',
            defaultValue: 'latest',
            description: 'Docker image tag'
        )
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
                script {
                    env.GIT_COMMIT_SHORT = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()
                }
            }
        }
        
        stage('Build') {
            parallel {
                stage('Compile') {
                    steps {
                        container('node') {
                            sh 'npm ci'
                            sh 'npm run build'
                            archiveArtifacts artifacts: 'dist/**', allowEmptyArchive: false
                        }
                    }
                }
                stage('Docker Build') {
                    steps {
                        container('docker') {
                            script {
                                def image = docker.build("${env.REGISTRY}/${env.JOB_NAME}:${env.GIT_COMMIT_SHORT}")
                                docker.withRegistry('https://registry.example.com', 'docker-registry') {
                                    image.push()
                                    image.push('latest')
                                }
                            }
                        }
                    }
                }
            }
        }
        
        stage('Test') {
            when {
                not { params.SKIP_TESTS }
            }
            parallel {
                stage('Unit Tests') {
                    steps {
                        container('node') {
                            sh 'npm run test:unit'
                            publishTestResults testResultsPattern: 'test-results.xml'
                            publishCoverage adapters: [
                                cobertura(path: 'coverage/cobertura-coverage.xml')
                            ]
                        }
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: 'coverage/**', allowEmptyArchive: true
                        }
                    }
                }
                stage('Integration Tests') {
                    steps {
                        container('node') {
                            sh 'npm run test:integration'
                        }
                    }
                }
                stage('Security Scan') {
                    steps {
                        container('docker') {
                            sh """
                                docker run --rm -v \$(pwd):/app -w /app \
                                    sonarqube/sonar-scanner-cli \
                                    sonar-scanner \
                                    -Dsonar.projectKey=${env.JOB_NAME} \
                                    -Dsonar.sources=. \
                                    -Dsonar.host.url=https://sonar.example.com \
                                    -Dsonar.login=${env.SONAR_TOKEN}
                            """
                        }
                    }
                }
            }
        }
        
        stage('Deploy') {
            when {
                anyOf {
                    branch 'main'
                    branch 'develop'
                }
            }
            steps {
                container('kubectl') {
                    script {
                        def namespace = params.ENVIRONMENT
                        def imageTag = env.GIT_COMMIT_SHORT
                        
                        sh """
                            helm upgrade --install ${env.JOB_NAME} ./helm-chart \
                                --namespace ${namespace} \
                                --set image.tag=${imageTag} \
                                --set environment=${namespace} \
                                --wait --timeout=600s
                        """
                        
                        // Verify deployment
                        sh """
                            kubectl rollout status deployment/${env.JOB_NAME} -n ${namespace}
                            kubectl get pods -n ${namespace} -l app=${env.JOB_NAME}
                        """
                    }
                }
            }
        }
        
        stage('Post-Deploy Tests') {
            when {
                branch 'main'
            }
            steps {
                container('node') {
                    script {
                        def appUrl = "https://${params.ENVIRONMENT}.example.com"
                        sh """
                            export APP_URL=${appUrl}
                            npm run test:e2e
                        """
                    }
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
                message: "✅ ${env.JOB_NAME} #${env.BUILD_NUMBER} deployed successfully to ${params.ENVIRONMENT}"
            )
        }
        failure {
            slackSend(
                channel: '#alerts',
                color: 'danger',
                message: "❌ ${env.JOB_NAME} #${env.BUILD_NUMBER} failed. Check: ${env.BUILD_URL}"
            )
            emailext(
                to: '${DEFAULT_RECIPIENTS}',
                subject: "Build Failed: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                body: "Build failed. Check console output at ${env.BUILD_URL}console"
            )
        }
        unstable {
            slackSend(
                channel: '#ci-cd',
                color: 'warning',
                message: "⚠️ ${env.JOB_NAME} #${env.BUILD_NUMBER} is unstable"
            )
        }
    }
}
```

#### Scripted Pipeline (Advanced Use Cases)
```groovy
// Jenkinsfile - Scripted Pipeline for complex logic
node('kubernetes') {
    def dockerImage
    def kubeConfig
    def deploymentStrategy = 'rolling'
    
    try {
        stage('Preparation') {
            checkout scm
            
            // Dynamic environment selection
            def branchName = env.BRANCH_NAME
            if (branchName == 'main') {
                env.TARGET_ENV = 'production'
                deploymentStrategy = 'blue-green'
            } else if (branchName == 'develop') {
                env.TARGET_ENV = 'staging'
            } else {
                env.TARGET_ENV = 'dev'
            }
            
            // Load external configuration
            def config = readYaml file: 'ci/config.yml'
            env.APP_VERSION = config.version
            env.BUILD_ARGS = config.buildArgs.join(' ')
        }
        
        stage('Build Matrix') {
            def buildJobs = [:]
            def platforms = ['linux/amd64', 'linux/arm64']
            
            for (platform in platforms) {
                def p = platform // Variable capture for closure
                buildJobs[p] = {
                    node('docker') {
                        stage("Build ${p}") {
                            sh """
                                docker buildx build \
                                    --platform ${p} \
                                    --tag ${env.REGISTRY}/${env.JOB_NAME}:${env.BUILD_NUMBER}-${p.replace('/', '-')} \
                                    --push \
                                    ${env.BUILD_ARGS} \
                                    .
                            """
                        }
                    }
                }
            }
            
            parallel buildJobs
        }
        
        stage('Create Manifest') {
            sh """
                docker manifest create ${env.REGISTRY}/${env.JOB_NAME}:${env.BUILD_NUMBER} \
                    ${env.REGISTRY}/${env.JOB_NAME}:${env.BUILD_NUMBER}-linux-amd64 \
                    ${env.REGISTRY}/${env.JOB_NAME}:${env.BUILD_NUMBER}-linux-arm64
                docker manifest push ${env.REGISTRY}/${env.JOB_NAME}:${env.BUILD_NUMBER}
            """
        }
        
        stage('Test Deployment') {
            if (env.TARGET_ENV != 'production') {
                sh """
                    helm install ${env.JOB_NAME}-test ./helm-chart \
                        --namespace ${env.TARGET_ENV}-test \
                        --set image.tag=${env.BUILD_NUMBER} \
                        --set replicaCount=1 \
                        --wait
                """
                
                // Run health checks
                timeout(time: 5, unit: 'MINUTES') {
                    waitUntil {
                        script {
                            def result = sh(
                                script: "kubectl get pods -n ${env.TARGET_ENV}-test -l app=${env.JOB_NAME}-test -o jsonpath='{.items[0].status.phase}'",
                                returnStdout: true
                            ).trim()
                            return result == 'Running'
                        }
                    }
                }
                
                // Cleanup test deployment
                sh "helm uninstall ${env.JOB_NAME}-test -n ${env.TARGET_ENV}-test"
            }
        }
        
        stage('Deploy') {
            if (deploymentStrategy == 'blue-green') {
                blueGreenDeploy()
            } else {
                rollingDeploy()
            }
        }
        
    } catch (Exception e) {
        currentBuild.result = 'FAILURE'
        throw e
    } finally {
        // Cleanup
        sh 'docker system prune -f'
    }
}

def blueGreenDeploy() {
    script {
        def currentColor = sh(
            script: "kubectl get service ${env.JOB_NAME} -n ${env.TARGET_ENV} -o jsonpath='{.spec.selector.color}' || echo 'blue'",
            returnStdout: true
        ).trim()
        
        def newColor = currentColor == 'blue' ? 'green' : 'blue'
        
        echo "Current deployment: ${currentColor}, New deployment: ${newColor}"
        
        // Deploy to new color
        sh """
            helm upgrade --install ${env.JOB_NAME}-${newColor} ./helm-chart \
                --namespace ${env.TARGET_ENV} \
                --set image.tag=${env.BUILD_NUMBER} \
                --set color=${newColor} \
                --set service.enabled=false \
                --wait
        """
        
        // Run smoke tests
        def appUrl = "http://${env.JOB_NAME}-${newColor}.${env.TARGET_ENV}.svc.cluster.local"
        sh "curl -f ${appUrl}/health || exit 1"
        
        // Switch traffic
        sh """
            kubectl patch service ${env.JOB_NAME} -n ${env.TARGET_ENV} \
                -p '{"spec":{"selector":{"color":"${newColor}"}}}'
        """
        
        // Wait and cleanup old deployment
        sleep 300 // 5 minutes
        sh "helm uninstall ${env.JOB_NAME}-${currentColor} -n ${env.TARGET_ENV} || true"
    }
}

def rollingDeploy() {
    sh """
        helm upgrade --install ${env.JOB_NAME} ./helm-chart \
            --namespace ${env.TARGET_ENV} \
            --set image.tag=${env.BUILD_NUMBER} \
            --wait
    """
}
```

### 3.2 Jenkins Plugin Ecosystem

#### Essential Plugins
```yaml
jenkins_plugins:
  pipeline_plugins:
    - pipeline-stage-view
    - workflow-aggregator
    - pipeline-utility-steps
    - pipeline-graph-analysis
    
  scm_plugins:
    - git
    - github
    - gitlab-plugin
    - bitbucket
    
  build_tools:
    - maven-plugin
    - gradle
    - nodejs
    - docker-workflow
    
  testing_plugins:
    - junit
    - coverage
    - sonar
    - selenium
    
  deployment_plugins:
    - kubernetes
    - helm
    - ansible
    - aws-cli
    
  notification_plugins:
    - slack
    - email-ext
    - jenkins-webhooks
    - prometheus-metrics

# Plugin configuration examples
kubernetes_plugin_config:
  clouds:
    - name: "kubernetes"
      serverUrl: "https://kubernetes.default.svc.cluster.local"
      namespace: "jenkins-agents"
      credentialsId: "kubernetes-token"
      templates:
        - name: "docker-agent"
          label: "docker"
          containers:
            - name: "docker"
              image: "docker:20.10.16-dind"
              privileged: true
              resourceRequestMemory: "512Mi"
              resourceLimitMemory: "2Gi"
```

## 4. ArgoCD và GitOps

### 4.1 GitOps Principles

#### GitOps Workflow
```yaml
gitops_principles:
  declarative:
    description: "System described declaratively"
    implementation:
      - Kubernetes YAML manifests
      - Helm charts
      - Kustomize overlays
      - Infrastructure as Code
      
  versioned:
    description: "Desired state versioned in Git"
    benefits:
      - Audit trail
      - Rollback capability
      - Branching strategies
      - Change approval process
      
  automated:
    description: "Automatic deployment and drift correction"
    mechanisms:
      - Git webhook triggers
      - Continuous reconciliation
      - Self-healing systems
      - Automatic rollbacks
      
  observable:
    description: "System state is observable"
    requirements:
      - Real-time status monitoring
      - Deployment tracking
      - Drift detection
      - Alert notifications
```

#### Repository Patterns
```bash
# App of Apps pattern
apps/
├── argocd/
│   ├── applications/
│   │   ├── app1.yaml
│   │   ├── app2.yaml
│   │   └── app3.yaml
│   └── app-of-apps.yaml
├── environments/
│   ├── dev/
│   │   ├── app1/
│   │   ├── app2/
│   │   └── kustomization.yaml
│   ├── staging/
│   │   ├── app1/
│   │   ├── app2/
│   │   └── kustomization.yaml
│   └── production/
│       ├── app1/
│       ├── app2/
│       └── kustomization.yaml
└── base/
    ├── app1/
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── kustomization.yaml
    └── app2/
        ├── deployment.yaml
        ├── service.yaml
        └── kustomization.yaml
```

### 4.2 ArgoCD Architecture

#### Core Components
```yaml
argocd_components:
  api_server:
    purpose: "REST API and Web UI"
    responsibilities:
      - Application management
      - User authentication
      - Repository credentials
      - RBAC enforcement
    
  repository_server:
    purpose: "Git repository interaction"
    responsibilities:
      - Git clone and fetch
      - Manifest generation
      - Helm template rendering
      - Kustomize build
    
  application_controller:
    purpose: "Kubernetes controller"
    responsibilities:
      - Monitor application state
      - Compare desired vs actual state
      - Sync applications
      - Health assessment
    
  dex_server:
    purpose: "OIDC identity provider"
    responsibilities:
      - SSO integration
      - User authentication
      - Token management
      - Group mapping
```

#### Application Configuration
```yaml
# ArgoCD Application
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: web-application
  namespace: argocd
  labels:
    environment: production
    team: platform
  annotations:
    notifications.argoproj.io/subscribe.on-sync-succeeded.slack: deployment-notifications
    notifications.argoproj.io/subscribe.on-health-degraded.slack: alerts
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/company/k8s-configs
    targetRevision: HEAD
    path: apps/web-application/overlays/production
    
  destination:
    server: https://kubernetes.default.svc
    namespace: web-production
    
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
      allowEmpty: false
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
        
  revisionHistoryLimit: 10
  
  ignoreDifferences:
    - group: apps
      kind: Deployment
      jsonPointers:
        - /spec/replicas
    - group: ""
      kind: Service
      managedFieldsManagers:
        - kube-controller-manager

# Project configuration
---
apiVersion: argoproj.io/v1alpha1
kind: AppProject
metadata:
  name: web-applications
  namespace: argocd
spec:
  description: "Web application projects"
  
  sourceRepos:
    - 'https://github.com/company/*'
    - 'https://charts.bitnami.com/bitnami'
    
  destinations:
    - namespace: 'web-*'
      server: https://kubernetes.default.svc
    - namespace: 'staging-*'
      server: https://staging-cluster
      
  clusterResourceWhitelist:
    - group: ''
      kind: Namespace
    - group: rbac.authorization.k8s.io
      kind: ClusterRole
      
  namespaceResourceWhitelist:
    - group: ''
      kind: Service
    - group: apps
      kind: Deployment
    - group: networking.k8s.io
      kind: Ingress
      
  roles:
    - name: developers
      description: "Developer access"
      policies:
        - p, proj:web-applications:developers, applications, get, web-applications/*, allow
        - p, proj:web-applications:developers, applications, sync, web-applications/*, allow
      groups:
        - company:developers
        
    - name: admins
      description: "Admin access"
      policies:
        - p, proj:web-applications:admins, applications, *, web-applications/*, allow
        - p, proj:web-applications:admins, repositories, *, *, allow
      groups:
        - company:platform-team
```

#### Multi-cluster Management
```yaml
# Cluster registration
argocd_clusters:
  production_cluster:
    name: "production"
    server: "https://prod-k8s.example.com"
    config:
      tlsClientConfig:
        caData: "LS0tLS1CRUdJTi..."
        certData: "LS0tLS1CRUdJTi..."
        keyData: "LS0tLS1CRUdJTi..."
    labels:
      environment: "production"
      region: "us-west-2"
      
  staging_cluster:
    name: "staging"
    server: "https://staging-k8s.example.com"
    config:
      bearerToken: "eyJhbGciOiJSUzI1NiIs..."
    labels:
      environment: "staging"
      region: "us-east-1"

# Cluster generators for ApplicationSet
cluster_generator:
  generators:
    - clusters:
        selector:
          matchLabels:
            environment: production
        values:
          revision: stable
          replicaCount: '5'
    - clusters:
        selector:
          matchLabels:
            environment: staging
        values:
          revision: main
          replicaCount: '2'
```

### 4.3 ApplicationSet Controller

#### Git Generator
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: microservices
  namespace: argocd
spec:
  generators:
  - git:
      repoURL: https://github.com/company/microservices
      revision: HEAD
      directories:
      - path: services/*
      - path: infrastructure/*
        exclude: infrastructure/argocd
  template:
    metadata:
      name: '{{path.basename}}'
      labels:
        app.kubernetes.io/name: '{{path.basename}}'
    spec:
      project: microservices
      source:
        repoURL: https://github.com/company/microservices
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

#### Matrix Generator
```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: multi-env-apps
spec:
  generators:
  - matrix:
      generators:
      - git:
          repoURL: https://github.com/company/apps
          revision: HEAD
          directories:
          - path: apps/*
      - clusters:
          selector:
            matchLabels:
              argocd.argoproj.io/secret-type: cluster
  template:
    metadata:
      name: '{{path.basename}}-{{name}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/company/apps
        targetRevision: HEAD
        path: '{{path}}/overlays/{{metadata.labels.environment}}'
      destination:
        server: '{{server}}'
        namespace: '{{path.basename}}-{{metadata.labels.environment}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
```

## 5. Advanced CI/CD Patterns

### 5.1 Progressive Delivery

#### Feature Flags Integration
```yaml
# Deployment with feature flags
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  template:
    spec:
      containers:
      - name: app
        image: web-app:v2.0.0
        env:
        - name: FEATURE_NEW_CHECKOUT
          value: "true"
        - name: FEATURE_ROLLOUT_PERCENTAGE
          value: "10"
        - name: UNLEASH_API_URL
          value: "https://unleash.example.com/api"
        - name: UNLEASH_API_TOKEN
          valueFrom:
            secretKeyRef:
              name: unleash-token
              key: token

# Application code integration
feature_flag_service:
  implementation: |
    from unleash import UnleashClient
    
    client = UnleashClient(
        url=os.getenv('UNLEASH_API_URL'),
        app_name='web-app',
        custom_headers={'Authorization': f'Bearer {os.getenv("UNLEASH_API_TOKEN")}'}
    )
    
    def is_feature_enabled(feature_name, user_id):
        context = {'userId': user_id}
        return client.is_enabled(feature_name, context)
    
    # Usage in application
    if is_feature_enabled('new_checkout', user.id):
        return new_checkout_flow()
    else:
        return legacy_checkout_flow()
```

#### Flagger Integration (Canary Deployments)
```yaml
apiVersion: flagger.app/v1beta1
kind: Canary
metadata:
  name: web-app
  namespace: production
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  progressDeadlineSeconds: 60
  service:
    port: 80
    targetPort: 8080
    gateways:
    - istio-system/gateway
    hosts:
    - app.example.com
  analysis:
    interval: 1m
    threshold: 5
    maxWeight: 50
    stepWeight: 10
    metrics:
    - name: request-success-rate
      thresholdRange:
        min: 99
      interval: 1m
    - name: request-duration
      thresholdRange:
        max: 500
      interval: 1m
    webhooks:
    - name: load-test
      url: http://flagger-loadtester.test/
      timeout: 5s
      metadata:
        cmd: "hey -z 1m -q 10 -c 2 http://app.example.com/"
    - name: integration-test
      url: http://integration-test-runner.test/
      timeout: 30s
      metadata:
        test_suite: "canary"
```

### 5.2 Security Integration

#### Security Scanning Pipeline
```yaml
# Comprehensive security scanning
security_pipeline:
  sast_scanning:
    tools:
      - sonarqube
      - semgrep
      - codeql
    configuration: |
      sonar-scanner \
        -Dsonar.projectKey=web-app \
        -Dsonar.sources=src \
        -Dsonar.exclusions=**/*_test.go,**/vendor/** \
        -Dsonar.tests=src \
        -Dsonar.test.inclusions=**/*_test.go \
        -Dsonar.go.coverage.reportPaths=coverage.out
        
  dependency_scanning:
    tools:
      - snyk
      - safety
      - npm_audit
    configuration: |
      # Snyk vulnerability scan
      snyk test --severity-threshold=high
      snyk monitor --project-name=web-app
      
      # Python dependencies
      safety check --json --output safety-report.json
      
      # Node.js dependencies
      npm audit --audit-level=high
      
  container_scanning:
    tools:
      - trivy
      - clair
      - twistlock
    configuration: |
      # Trivy comprehensive scan
      trivy image --exit-code 1 --severity HIGH,CRITICAL web-app:latest
      trivy fs --exit-code 1 --severity HIGH,CRITICAL .
      trivy config --exit-code 1 .
      
  secret_scanning:
    tools:
      - truffleHog
      - gitleaks
      - detect-secrets
    configuration: |
      # TruffleHog scan
      truffleHog --regex --entropy=False .
      
      # Gitleaks scan
      gitleaks detect --source . --verbose
```

#### Policy as Code
```yaml
# Open Policy Agent (OPA) Gatekeeper
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredsecuritycontext
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredSecurityContext
      validation:
        properties:
          runAsNonRoot:
            type: boolean
          runAsUser:
            type: integer
          fsGroup:
            type: integer
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredsecuritycontext
        
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not container.securityContext.runAsNonRoot
          msg := "Container must run as non-root user"
        }
        
        violation[{"msg": msg}] {
          not input.review.object.spec.securityContext.fsGroup
          msg := "Pod must specify fsGroup"
        }

---
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredSecurityContext
metadata:
  name: must-run-as-nonroot
spec:
  match:
    kinds:
      - apiGroups: ["apps"]
        kinds: ["Deployment"]
    namespaces: ["production", "staging"]
  parameters:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
```

### 5.3 Observability Integration

#### Metrics Collection
```yaml
# Prometheus monitoring integration
prometheus_config:
  scrape_configs:
    - job_name: 'gitlab-ci-pipelines'
      static_configs:
        - targets: ['gitlab-runner-metrics:9252']
      metrics_path: /metrics
      scrape_interval: 30s
      
    - job_name: 'jenkins-metrics'
      static_configs:
        - targets: ['jenkins:8080']
      metrics_path: /prometheus
      scrape_interval: 30s
      
    - job_name: 'argocd-metrics'
      kubernetes_sd_configs:
        - role: pod
          namespaces:
            names: ['argocd']
      relabel_configs:
        - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
          action: keep
          regex: argocd-metrics

# Custom metrics for CI/CD
custom_metrics:
  deployment_frequency:
    query: 'rate(deployments_total[24h])'
    description: "Number of deployments per day"
    
  lead_time:
    query: 'histogram_quantile(0.95, rate(commit_to_deploy_duration_seconds_bucket[24h]))'
    description: "95th percentile lead time"
    
  change_failure_rate:
    query: 'rate(deployment_failures_total[24h]) / rate(deployments_total[24h])'
    description: "Percentage of deployments that fail"
    
  mean_time_to_recovery:
    query: 'histogram_quantile(0.50, rate(incident_resolution_duration_seconds_bucket[24h]))'
    description: "Median time to resolve incidents"
```

Lý thuyết này cung cấp nền tảng sâu sắc về CI/CD và DevOps practices, từ pipeline fundamentals đến advanced patterns như GitOps và progressive delivery, giúp engineers tại Viettel IDC xây dựng và vận hành CI/CD systems hiệu quả trong môi trường enterprise.
