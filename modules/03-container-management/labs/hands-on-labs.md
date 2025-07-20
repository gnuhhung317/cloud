# Container Management Hands-on Labs

## Lab 1: Docker Fundamentals và Security

### Lab 1.1: Container Security Implementation

#### Objective
Triển khai container với security best practices từ image build đến runtime.

#### Prerequisites
- Docker Engine 20.10+
- Basic understanding của Linux namespaces
- Access đến Docker registry

#### Exercise 1: Secure Multi-stage Build
```dockerfile
# Create Dockerfile.secure
FROM golang:1.19-alpine AS builder

# Security: Install ca-certificates và security tools
RUN apk add --no-cache \
    ca-certificates \
    git \
    tzdata

# Security: Create non-root user in builder stage
RUN adduser -D -s /bin/sh -u 1001 appuser

WORKDIR /app

# Copy dependency files first (better caching)
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# Copy source code
COPY . .

# Security: Build with hardening flags
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' \
    -a -installsuffix cgo \
    -o main .

# Security: Vulnerability scanning during build
RUN go list -json -m all | nancy sleuth || true

# Production stage - Minimal runtime
FROM scratch

# Security: Copy certificates and timezone data
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /etc/passwd /etc/passwd

# Security: Copy only the binary
COPY --from=builder /app/main /app

# Security: Run as non-root user
USER 1001

# Security: Use specific port
EXPOSE 8080

# Security: Use ENTRYPOINT instead of CMD
ENTRYPOINT ["/app"]
```

#### Exercise 2: Container Security Scanning
```bash
# Build the secure image
docker build -f Dockerfile.secure -t myapp:secure .

# Install and run Trivy security scanner
# On Ubuntu/Debian
sudo apt-get update
sudo apt-get install wget apt-transport-https gnupg lsb-release
wget -qO - https://aquasecurity.github.io/trivy-repo/deb/public.key | sudo apt-key add -
echo "deb https://aquasecurity.github.io/trivy-repo/deb $(lsb_release -sc) main" | sudo tee -a /etc/apt/sources.list.d/trivy.list
sudo apt-get update
sudo apt-get install trivy

# Comprehensive vulnerability scan
trivy image --severity HIGH,CRITICAL myapp:secure

# Filesystem scan
trivy fs --severity HIGH,CRITICAL .

# Configuration scan
trivy config .

# SBOM generation
trivy image --format spdx-json --output sbom.json myapp:secure

# Generate security report
trivy image --format json --output security-report.json myapp:secure
```

#### Exercise 3: Runtime Security Configuration
```bash
# Create secure container with security options
docker run -d \
  --name secure-app \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=1g \
  --cap-drop ALL \
  --cap-add NET_BIND_SERVICE \
  --security-opt no-new-privileges:true \
  --security-opt seccomp=seccomp-profile.json \
  --user 1001:1001 \
  --memory 512m \
  --cpus 0.5 \
  --pids-limit 100 \
  -p 8080:8080 \
  myapp:secure

# Verify security settings
docker inspect secure-app | jq '.[]|{
  ReadonlyRootfs: .HostConfig.ReadonlyRootfs,
  User: .Config.User,
  SecurityOpt: .HostConfig.SecurityOpt,
  CapDrop: .HostConfig.CapDrop,
  CapAdd: .HostConfig.CapAdd,
  Memory: .HostConfig.Memory,
  PidsLimit: .HostConfig.PidsLimit
}'

# Monitor container processes
docker exec secure-app ps aux

# Check container capabilities
docker exec secure-app grep Cap /proc/1/status
```

#### Exercise 4: Seccomp Profile Creation
```json
# Create seccomp-profile.json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64"
  ],
  "syscalls": [
    {
      "names": [
        "accept4",
        "access",
        "arch_prctl",
        "bind",
        "brk",
        "clone",
        "close",
        "connect",
        "dup2",
        "execve",
        "exit_group",
        "fstat",
        "futex",
        "getpid",
        "getuid",
        "listen",
        "mmap",
        "mprotect",
        "munmap",
        "nanosleep",
        "open",
        "openat",
        "read",
        "rt_sigaction",
        "rt_sigprocmask",
        "rt_sigreturn",
        "setsockopt",
        "socket",
        "stat",
        "write"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

#### Validation Tasks
1. Verify image has no HIGH/CRITICAL vulnerabilities
2. Confirm container runs as non-root user
3. Test that container cannot access host filesystem
4. Validate resource limits are enforced
5. Check that unnecessary capabilities are dropped

---

## Lab 2: Kubernetes Security và RBAC

### Lab 2.1: Pod Security Standards Implementation

#### Objective
Implement Pod Security Standards và RBAC trong Kubernetes cluster.

#### Exercise 1: Namespace Security Configuration
```yaml
# Create namespace with Pod Security Standards
apiVersion: v1
kind: Namespace
metadata:
  name: secure-production
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
    environment: production
---
# Network policy - default deny all
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: secure-production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
---
# Resource quota
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: secure-production
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    pods: "10"
    persistentvolumeclaims: "4"
```

#### Exercise 2: Secure Pod Deployment
```yaml
# Secure application deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: secure-web-app
  namespace: secure-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: secure-web-app
  template:
    metadata:
      labels:
        app: secure-web-app
      annotations:
        container.apparmor.security.beta.kubernetes.io/web: runtime/default
    spec:
      serviceAccountName: web-app-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 2001
        fsGroup: 2001
        seccompProfile:
          type: RuntimeDefault
      containers:
      - name: web
        image: nginx:1.23-alpine
        ports:
        - containerPort: 8080
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          runAsNonRoot: true
          runAsUser: 1001
          capabilities:
            drop:
            - ALL
            add:
            - NET_BIND_SERVICE
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: var-cache
          mountPath: /var/cache/nginx
        - name: var-run
          mountPath: /var/run
      volumes:
      - name: tmp
        emptyDir: {}
      - name: var-cache
        emptyDir: {}
      - name: var-run
        emptyDir: {}
```

#### Exercise 3: RBAC Configuration
```yaml
# Service Account
apiVersion: v1
kind: ServiceAccount
metadata:
  name: web-app-sa
  namespace: secure-production
automountServiceAccountToken: false
---
# Role with minimal permissions
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: secure-production
  name: web-app-role
rules:
- apiGroups: [""]
  resources: ["configmaps"]
  resourceNames: ["app-config"]
  verbs: ["get"]
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["app-secrets"]
  verbs: ["get"]
---
# Role binding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: web-app-binding
  namespace: secure-production
subjects:
- kind: ServiceAccount
  name: web-app-sa
  namespace: secure-production
roleRef:
  kind: Role
  name: web-app-role
  apiGroup: rbac.authorization.k8s.io
---
# Network policy for application
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-app-netpol
  namespace: secure-production
spec:
  podSelector:
    matchLabels:
      app: secure-web-app
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-system
    ports:
    - protocol: TCP
      port: 8080
  egress:
  # Allow DNS
  - to: []
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  # Allow HTTPS outbound
  - to: []
    ports:
    - protocol: TCP
      port: 443
```

#### Exercise 4: Security Validation
```bash
# Deploy the secure application
kubectl apply -f secure-namespace.yaml
kubectl apply -f secure-deployment.yaml
kubectl apply -f rbac-config.yaml

# Validate Pod Security Standards
kubectl get pods -n secure-production
kubectl describe pod <pod-name> -n secure-production

# Check security context
kubectl get pod <pod-name> -n secure-production -o jsonpath='{.spec.securityContext}'
kubectl get pod <pod-name> -n secure-production -o jsonpath='{.spec.containers[0].securityContext}'

# Verify RBAC permissions
kubectl auth can-i get secrets --as=system:serviceaccount:secure-production:web-app-sa -n secure-production
kubectl auth can-i delete pods --as=system:serviceaccount:secure-production:web-app-sa -n secure-production

# Test network policy
kubectl run test-pod --image=alpine --rm -it --restart=Never -- sh
# Try to access the application pod

# Validate resource constraints
kubectl top pods -n secure-production
kubectl describe resourcequota -n secure-production
```

---

## Lab 3: Kubernetes Advanced Networking

### Lab 3.1: Service Mesh Implementation với Istio

#### Objective
Deploy và configure Istio service mesh với security policies.

#### Exercise 1: Istio Installation
```bash
# Download Istio
curl -L https://istio.io/downloadIstio | sh -
cd istio-*
export PATH=$PWD/bin:$PATH

# Install Istio with security profile
istioctl install --set values.defaultRevision=default

# Enable automatic sidecar injection
kubectl label namespace secure-production istio-injection=enabled

# Verify installation
kubectl get pods -n istio-system
istioctl proxy-status
```

#### Exercise 2: Application Deployment với Istio
```yaml
# Application with Istio annotations
apiVersion: apps/v1
kind: Deployment
metadata:
  name: productcatalog
  namespace: secure-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: productcatalog
  template:
    metadata:
      labels:
        app: productcatalog
        version: v1
      annotations:
        sidecar.istio.io/inject: "true"
    spec:
      containers:
      - name: server
        image: gcr.io/google-samples/microservices-demo/productcatalogservice:v0.3.6
        ports:
        - containerPort: 3550
        env:
        - name: PORT
          value: "3550"
        resources:
          requests:
            cpu: 100m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: productcatalog
  namespace: secure-production
spec:
  selector:
    app: productcatalog
  ports:
  - port: 3550
    targetPort: 3550
---
# Frontend service
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: secure-production
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
        version: v1
    spec:
      containers:
      - name: server
        image: gcr.io/google-samples/microservices-demo/frontend:v0.3.6
        ports:
        - containerPort: 8080
        env:
        - name: PORT
          value: "8080"
        - name: PRODUCT_CATALOG_SERVICE_ADDR
          value: "productcatalog:3550"
        resources:
          requests:
            cpu: 100m
            memory: 64Mi
          limits:
            cpu: 200m
            memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: frontend
  namespace: secure-production
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 8080
  type: ClusterIP
```

#### Exercise 3: Security Policies Configuration
```yaml
# Enable mTLS for the namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: secure-production
spec:
  mtls:
    mode: STRICT
---
# Authorization policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: productcatalog-authz
  namespace: secure-production
spec:
  selector:
    matchLabels:
      app: productcatalog
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/secure-production/sa/default"]
    - source:
        principals: ["cluster.local/ns/secure-production/sa/frontend"]
    to:
    - operation:
        methods: ["GET", "POST"]
        ports: ["3550"]
---
# Traffic policy
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: productcatalog-destination
  namespace: secure-production
spec:
  host: productcatalog
  trafficPolicy:
    tls:
      mode: ISTIO_MUTUAL
    connectionPool:
      tcp:
        maxConnections: 10
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 2
    outlierDetection:
      consecutiveErrors: 3
      interval: 30s
      baseEjectionTime: 30s
---
# Virtual service for traffic management
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: productcatalog-vs
  namespace: secure-production
spec:
  hosts:
  - productcatalog
  http:
  - match:
    - headers:
        user-type:
          exact: premium
    route:
    - destination:
        host: productcatalog
        subset: v1
      weight: 100
    timeout: 5s
    retries:
      attempts: 3
      perTryTimeout: 2s
  - route:
    - destination:
        host: productcatalog
        subset: v1
    timeout: 10s
```

#### Exercise 4: Gateway và Ingress Configuration
```yaml
# Istio Gateway
apiVersion: networking.istio.io/v1beta1
kind: Gateway
metadata:
  name: frontend-gateway
  namespace: secure-production
spec:
  selector:
    istio: ingressgateway
  servers:
  - port:
      number: 443
      name: https
      protocol: HTTPS
    tls:
      mode: SIMPLE
      credentialName: frontend-tls-secret
    hosts:
    - app.company.com
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - app.company.com
    tls:
      httpsRedirect: true
---
# Virtual service for gateway
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: frontend-vs
  namespace: secure-production
spec:
  hosts:
  - app.company.com
  gateways:
  - frontend-gateway
  http:
  - match:
    - uri:
        prefix: /
    route:
    - destination:
        host: frontend
        port:
          number: 80
    headers:
      request:
        add:
          x-forwarded-proto: https
      response:
        add:
          x-content-type-options: nosniff
          x-frame-options: DENY
          x-xss-protection: "1; mode=block"
---
# TLS Certificate
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: frontend-tls
  namespace: istio-system
spec:
  secretName: frontend-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - app.company.com
```

#### Validation Tasks
```bash
# Deploy applications
kubectl apply -f istio-apps.yaml
kubectl apply -f security-policies.yaml
kubectl apply -f gateway-config.yaml

# Verify mTLS is working
istioctl authn tls-check productcatalog.secure-production.svc.cluster.local

# Check proxy configuration
istioctl proxy-config cluster <pod-name>.secure-production

# Monitor traffic
kubectl logs -f deployment/frontend -c istio-proxy -n secure-production

# Test authorization policies
kubectl exec -n secure-production deployment/frontend -c server -- curl productcatalog:3550

# View service mesh topology
istioctl dashboard kiali
```

---

## Lab 4: CI/CD Pipeline với GitLab và ArgoCD

### Lab 4.1: Complete CI/CD Pipeline Implementation

#### Objective
Implement end-to-end CI/CD pipeline với security scanning và GitOps deployment.

#### Exercise 1: GitLab CI/CD Pipeline
```yaml
# .gitlab-ci.yml
stages:
  - validate
  - build
  - security-scan
  - deploy-staging
  - integration-test
  - deploy-production

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  REGISTRY: $CI_REGISTRY_IMAGE
  KUBECONFIG_FILE: $KUBE_CONFIG

.docker_template: &docker_template
  image: docker:20.10.16
  services:
    - docker:20.10.16-dind
  before_script:
    - echo $CI_REGISTRY_PASSWORD | docker login -u $CI_REGISTRY_USER --password-stdin $CI_REGISTRY

# Code quality và security validation
validate:lint:
  stage: validate
  image: golangci/golangci-lint:latest
  script:
    - golangci-lint run --timeout 5m
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == "main"

validate:unit-tests:
  stage: validate
  image: golang:1.19-alpine
  script:
    - go mod download
    - go test -v -race -coverprofile=coverage.out ./...
    - go tool cover -html=coverage.out -o coverage.html
  coverage: '/coverage: \d+.\d+% of statements/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
    paths:
      - coverage.html
    expire_in: 1 week

# Secure build
build:application:
  <<: *docker_template
  stage: build
  script:
    - |
      # Multi-platform build
      docker buildx create --use --name multiplatform
      docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --push \
        --tag $REGISTRY:$CI_COMMIT_SHA \
        --tag $REGISTRY:latest \
        --file Dockerfile.secure \
        .
  artifacts:
    reports:
      dotenv: build.env
  rules:
    - if: $CI_COMMIT_BRANCH == "main"
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"

# Security scanning
security:trivy-scan:
  stage: security-scan
  image: aquasec/trivy:latest
  script:
    - trivy image --exit-code 1 --severity HIGH,CRITICAL $REGISTRY:$CI_COMMIT_SHA
    - trivy image --format json --output trivy-report.json $REGISTRY:$CI_COMMIT_SHA
  artifacts:
    reports:
      dependency_scanning: trivy-report.json
    paths:
      - trivy-report.json
    expire_in: 1 week
  allow_failure: false

security:sast:
  stage: security-scan
  include:
    - template: Security/SAST.gitlab-ci.yml
  variables:
    SAST_EXCLUDED_ANALYZERS: "eslint"

security:secret-detection:
  stage: security-scan
  include:
    - template: Security/Secret-Detection.gitlab-ci.yml

# Staging deployment
deploy:staging:
  stage: deploy-staging
  image: bitnami/kubectl:latest
  environment:
    name: staging
    url: https://staging.company.com
  script:
    - echo $KUBE_CONFIG | base64 -d > kubeconfig
    - export KUBECONFIG=kubeconfig
    - |
      # Update deployment with new image
      kubectl set image deployment/web-app \
        web=$REGISTRY:$CI_COMMIT_SHA \
        -n staging
      kubectl rollout status deployment/web-app -n staging --timeout=300s
      
      # Verify deployment
      kubectl get pods -n staging
      kubectl get services -n staging
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Integration tests
test:integration:
  stage: integration-test
  image: postman/newman:latest
  script:
    - newman run postman/integration-tests.json \
        --environment postman/staging-env.json \
        --reporters cli,json \
        --reporter-json-export newman-report.json
  artifacts:
    reports:
      junit: newman-report.xml
    paths:
      - newman-report.json
    expire_in: 1 week
  rules:
    - if: $CI_COMMIT_BRANCH == "main"

# Production deployment (manual)
deploy:production:
  stage: deploy-production
  image: bitnami/kubectl:latest
  environment:
    name: production
    url: https://app.company.com
  script:
    - echo "Triggering ArgoCD sync for production deployment"
    - |
      # Update GitOps repository
      git clone https://gitlab-ci-token:${CI_JOB_TOKEN}@gitlab.com/company/k8s-manifests.git
      cd k8s-manifests
      sed -i "s|image:.*|image: $REGISTRY:$CI_COMMIT_SHA|g" production/web-app/deployment.yaml
      git add .
      git commit -m "Update production image to $CI_COMMIT_SHA"
      git push origin main
  when: manual
  only:
    - main
```

#### Exercise 2: ArgoCD Application Setup
```yaml
# ArgoCD application for staging
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: web-app-staging
  namespace: argocd
  labels:
    environment: staging
spec:
  project: default
  source:
    repoURL: https://gitlab.com/company/k8s-manifests.git
    targetRevision: HEAD
    path: staging/web-app
  destination:
    server: https://kubernetes.default.svc
    namespace: staging
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  revisionHistoryLimit: 10
---
# ArgoCD application for production
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: web-app-production
  namespace: argocd
  labels:
    environment: production
spec:
  project: default
  source:
    repoURL: https://gitlab.com/company/k8s-manifests.git
    targetRevision: HEAD
    path: production/web-app
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    syncOptions:
      - CreateNamespace=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
  revisionHistoryLimit: 10
```

#### Exercise 3: Kubernetes Manifests Structure
```bash
# k8s-manifests repository structure
k8s-manifests/
├── staging/
│   └── web-app/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       └── kustomization.yaml
├── production/
│   └── web-app/
│       ├── deployment.yaml
│       ├── service.yaml
│       ├── configmap.yaml
│       ├── hpa.yaml
│       ├── pdb.yaml
│       └── kustomization.yaml
└── base/
    └── web-app/
        ├── deployment.yaml
        ├── service.yaml
        └── kustomization.yaml
```

```yaml
# production/web-app/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
  namespace: production
  labels:
    app: web-app
    environment: production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9090"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: web-app-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        fsGroup: 2001
      containers:
      - name: web
        image: registry.company.com/web-app:latest  # This will be updated by CI/CD
        ports:
        - containerPort: 8080
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "info"
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        volumeMounts:
        - name: tmp
          mountPath: /tmp
      volumes:
      - name: tmp
        emptyDir: {}
```

#### Validation Tasks
```bash
# Set up GitLab CI/CD
# 1. Add .gitlab-ci.yml to your repository
# 2. Configure CI/CD variables in GitLab:
#    - CI_REGISTRY_IMAGE
#    - KUBE_CONFIG (base64 encoded kubeconfig)

# Deploy ArgoCD applications
kubectl apply -f argocd-applications.yaml

# Monitor pipeline execution
# Check GitLab pipeline status
# Monitor ArgoCD sync status

# Verify deployments
kubectl get applications -n argocd
argocd app list
argocd app sync web-app-staging
argocd app get web-app-production

# Test the complete flow
# 1. Make a code change
# 2. Push to main branch
# 3. Monitor pipeline execution
# 4. Verify staging deployment
# 5. Run integration tests
# 6. Trigger production deployment
# 7. Verify production deployment

# Security validation
trivy image registry.company.com/web-app:latest
kubectl get pods -n production -o jsonpath='{.items[*].spec.securityContext}'
```

---

## Lab 5: Monitoring và Observability

### Lab 5.1: Comprehensive Monitoring Stack

#### Objective
Deploy complete monitoring stack với Prometheus, Grafana, và AlertManager.

#### Exercise 1: Prometheus Setup
```yaml
# prometheus-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093
    
    scrape_configs:
      - job_name: 'kubernetes-apiservers'
        kubernetes_sd_configs:
          - role: endpoints
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
            action: keep
            regex: default;kubernetes;https
      
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
        scheme: https
        tls_config:
          ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
        bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
        relabel_configs:
          - action: labelmap
            regex: __meta_kubernetes_node_label_(.+)
          - target_label: __address__
            replacement: kubernetes.default.svc:443
          - source_labels: [__meta_kubernetes_node_name]
            regex: (.+)
            target_label: __metrics_path__
            replacement: /api/v1/nodes/${1}/proxy/metrics
      
      - job_name: 'kubernetes-pods'
        kubernetes_sd_configs:
          - role: pod
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: $1:$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name
      
      - job_name: 'istio-mesh'
        kubernetes_sd_configs:
          - role: endpoints
            namespaces:
              names:
                - istio-system
        relabel_configs:
          - source_labels: [__meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
            action: keep
            regex: istio-telemetry;prometheus
---
# Alerting rules
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: monitoring
data:
  kubernetes.yml: |
    groups:
    - name: kubernetes
      rules:
      - alert: KubernetesPodCrashLooping
        expr: rate(kube_pod_container_status_restarts_total[5m]) * 60 * 5 > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: Kubernetes pod crash looping
          description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is crash looping"
      
      - alert: KubernetesNodeNotReady
        expr: kube_node_status_condition{condition="Ready",status="true"} == 0
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: Kubernetes node not ready
          description: "Node {{ $labels.node }} is not ready"
      
      - alert: KubernetesPodNotReady
        expr: kube_pod_status_ready{condition="true"} == 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: Kubernetes pod not ready
          description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is not ready"
    
    - name: application
      rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High error rate detected
          description: "Error rate is {{ $value }} for {{ $labels.job }}"
      
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High latency detected
          description: "95th percentile latency is {{ $value }}s for {{ $labels.job }}"
```

#### Exercise 2: Grafana Dashboard Configuration
```yaml
# grafana-dashboard-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubernetes-dashboard
  namespace: monitoring
  labels:
    grafana_dashboard: "1"
data:
  kubernetes-dashboard.json: |
    {
      "dashboard": {
        "id": null,
        "title": "Kubernetes Cluster Monitoring",
        "tags": ["kubernetes"],
        "timezone": "browser",
        "panels": [
          {
            "id": 1,
            "title": "Cluster CPU Usage",
            "type": "stat",
            "targets": [
              {
                "expr": "100 - (avg(irate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
                "legendFormat": "CPU Usage %"
              }
            ],
            "fieldConfig": {
              "defaults": {
                "unit": "percent",
                "thresholds": {
                  "steps": [
                    {"color": "green", "value": null},
                    {"color": "yellow", "value": 70},
                    {"color": "red", "value": 90}
                  ]
                }
              }
            },
            "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
          },
          {
            "id": 2,
            "title": "Cluster Memory Usage",
            "type": "stat",
            "targets": [
              {
                "expr": "100 * (1 - ((avg_over_time(node_memory_MemFree_bytes[10m]) + avg_over_time(node_memory_Cached_bytes[10m]) + avg_over_time(node_memory_Buffers_bytes[10m])) / avg_over_time(node_memory_MemTotal_bytes[10m])))",
                "legendFormat": "Memory Usage %"
              }
            ],
            "fieldConfig": {
              "defaults": {
                "unit": "percent",
                "thresholds": {
                  "steps": [
                    {"color": "green", "value": null},
                    {"color": "yellow", "value": 70},
                    {"color": "red", "value": 90}
                  ]
                }
              }
            },
            "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
          },
          {
            "id": 3,
            "title": "Pod Status",
            "type": "table",
            "targets": [
              {
                "expr": "kube_pod_info",
                "legendFormat": "",
                "format": "table",
                "instant": true
              }
            ],
            "transformations": [
              {
                "id": "organize",
                "options": {
                  "excludeByName": {"Time": true, "__name__": true},
                  "indexByName": {},
                  "renameByName": {
                    "namespace": "Namespace",
                    "pod": "Pod",
                    "node": "Node"
                  }
                }
              }
            ],
            "gridPos": {"h": 12, "w": 24, "x": 0, "y": 8}
          }
        ],
        "time": {"from": "now-1h", "to": "now"},
        "refresh": "30s"
      }
    }
```

#### Exercise 3: AlertManager Configuration
```yaml
# alertmanager-config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      smtp_smarthost: 'smtp.company.com:587'
      smtp_from: 'alerts@company.com'
      slack_api_url: 'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK'
    
    route:
      group_by: ['alertname', 'cluster', 'service']
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 12h
      receiver: 'default'
      routes:
        - match:
            severity: critical
          receiver: 'critical-alerts'
          group_wait: 10s
          repeat_interval: 1h
        - match:
            severity: warning
          receiver: 'warning-alerts'
          group_wait: 30s
          repeat_interval: 4h
    
    receivers:
      - name: 'default'
        slack_configs:
          - channel: '#general-alerts'
            title: 'Kubernetes Alert'
            text: |
              {{ range .Alerts }}
              *Alert:* {{ .Annotations.summary }}
              *Description:* {{ .Annotations.description }}
              *Severity:* {{ .Labels.severity }}
              {{ end }}
      
      - name: 'critical-alerts'
        email_configs:
          - to: 'oncall@company.com'
            subject: 'CRITICAL: {{ .GroupLabels.alertname }}'
            body: |
              {{ range .Alerts }}
              Alert: {{ .Annotations.summary }}
              Description: {{ .Annotations.description }}
              Severity: {{ .Labels.severity }}
              {{ end }}
        slack_configs:
          - channel: '#critical-alerts'
            title: 'CRITICAL Alert'
            text: |
              <!channel>
              {{ range .Alerts }}
              *Alert:* {{ .Annotations.summary }}
              *Description:* {{ .Annotations.description }}
              {{ end }}
      
      - name: 'warning-alerts'
        slack_configs:
          - channel: '#warning-alerts'
            title: 'Warning Alert'
            text: |
              {{ range .Alerts }}
              *Alert:* {{ .Annotations.summary }}
              *Description:* {{ .Annotations.description }}
              {{ end }}
    
    inhibit_rules:
      - source_match:
          severity: 'critical'
        target_match:
          severity: 'warning'
        equal: ['alertname', 'cluster', 'service']
```

#### Validation Tasks
```bash
# Deploy monitoring stack
kubectl create namespace monitoring
kubectl apply -f prometheus-config.yaml
kubectl apply -f grafana-dashboard-configmap.yaml
kubectl apply -f alertmanager-config.yaml

# Deploy Prometheus using Helm
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set prometheus.prometheusSpec.additionalScrapeConfigs="prometheus-config" \
  --set alertmanager.config="alertmanager-config"

# Access Grafana dashboard
kubectl port-forward service/prometheus-grafana 3000:80 -n monitoring
# Login: admin/prom-operator

# Verify metrics collection
kubectl port-forward service/prometheus-kube-prometheus-prometheus 9090:9090 -n monitoring
# Check targets: http://localhost:9090/targets
# Check rules: http://localhost:9090/rules

# Test alerting
# Create a pod that will crash
kubectl run test-crash --image=busybox --restart=Never -- sh -c "exit 1"
# Monitor alerts in AlertManager UI

# Create custom application metrics
# Add to your application:
# /metrics endpoint with Prometheus format
# Example Go application with metrics:
```

```go
package main

import (
    "net/http"
    "time"
    
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
)

var (
    httpRequests = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total number of HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )
    
    httpDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "Duration of HTTP requests",
        },
        []string{"method", "endpoint"},
    )
)

func init() {
    prometheus.MustRegister(httpRequests)
    prometheus.MustRegister(httpDuration)
}

func metricsMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        
        next.ServeHTTP(w, r)
        
        duration := time.Since(start)
        httpDuration.WithLabelValues(r.Method, r.URL.Path).Observe(duration.Seconds())
        httpRequests.WithLabelValues(r.Method, r.URL.Path, "200").Inc()
    })
}

func main() {
    http.Handle("/metrics", promhttp.Handler())
    http.Handle("/", metricsMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        w.Write([]byte("Hello World"))
    })))
    
    http.ListenAndServe(":8080", nil)
}
```

Các labs này cung cấp hands-on experience toàn diện về container management, từ Docker security đến Kubernetes orchestration, CI/CD pipelines, và monitoring. Mỗi lab được thiết kế để mirror real-world scenarios tại Viettel IDC với focus trên security và best practices.
