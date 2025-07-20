# Module 3: Quản lý Container (Kubernetes, Docker, CI/CD)

## 🎯 Mục tiêu Module
Thành thạo công nghệ containerization và orchestration, từ Docker cơ bản đến Kubernetes nâng cao, kết hợp với CI/CD pipelines để triển khai ứng dụng hiện đại tại Viettel IDC.

## 📋 Nội dung Chính

### Docker (30% trọng số)
#### 1. Container Fundamentals
- **Docker architecture**: engine, daemon, client
- **Images & Containers**: lifecycle, management
- **Dockerfile**: best practices, multi-stage builds
- **Docker Compose**: multi-container applications

#### 2. Docker Operations
- **Registry management**: Docker Hub, private registries
- **Networking**: bridge, host, overlay networks
- **Storage**: volumes, bind mounts, tmpfs
- **Security**: image scanning, user namespaces

### Kubernetes (50% trọng số)
#### 1. Cluster Architecture
- **Control plane**: API server, etcd, scheduler, controller
- **Worker nodes**: kubelet, kube-proxy, container runtime
- **Networking**: CNI, services, ingress
- **Storage**: PV, PVC, storage classes

#### 2. Workload Management
- **Pods**: lifecycle, design patterns
- **Deployments**: rolling updates, rollbacks
- **Services**: ClusterIP, NodePort, LoadBalancer
- **ConfigMaps & Secrets**: configuration management

#### 3. Advanced Topics
- **StatefulSets**: stateful applications
- **DaemonSets**: node-level services
- **Jobs & CronJobs**: batch workloads
- **HPA/VPA**: auto-scaling

#### 4. Operations
- **kubectl**: command line mastery
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK stack, Fluentd
- **Troubleshooting**: debugging techniques

### CI/CD (20% trọng số)
#### 1. GitLab CI/CD
- **Pipeline configuration**: .gitlab-ci.yml
- **Runners**: shared vs dedicated
- **Environments**: staging, production
- **Security**: dependency scanning, SAST

#### 2. Jenkins
- **Pipeline as Code**: Jenkinsfile
- **Plugin ecosystem**: Docker, Kubernetes
- **Build agents**: master-slave setup
- **Integration**: webhooks, notifications

#### 3. ArgoCD (GitOps)
- **Application deployment**: declarative approach
- **Sync strategies**: manual vs automatic
- **Multi-cluster**: management patterns
- **Security**: RBAC, SSO integration

## 🛠️ Kỹ năng Thực hành

### Docker Labs
1. **Containerize Applications**
   ```dockerfile
   # Multi-stage Dockerfile example
   FROM node:16-alpine AS builder
   WORKDIR /app
   COPY package*.json ./
   RUN npm ci --only=production

   FROM node:16-alpine
   WORKDIR /app
   COPY --from=builder /app/node_modules ./node_modules
   COPY . .
   EXPOSE 3000
   CMD ["node", "app.js"]
   ```

2. **Docker Compose Stack**
   ```yaml
   # docker-compose.yml
   version: '3.8'
   services:
     web:
       build: .
       ports:
         - "3000:3000"
       depends_on:
         - db
     db:
       image: postgres:13
       environment:
         POSTGRES_DB: myapp
         POSTGRES_PASSWORD: secret
       volumes:
         - postgres_data:/var/lib/postgresql/data
   volumes:
     postgres_data:
   ```

### Kubernetes Labs
1. **Cluster Setup**
   ```bash
   # kubeadm cluster setup
   kubeadm init --pod-network-cidr=10.244.0.0/16
   kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml
   ```

2. **Application Deployment**
   ```yaml
   # deployment.yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: nginx-deployment
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: nginx
     template:
       metadata:
         labels:
           app: nginx
       spec:
         containers:
         - name: nginx
           image: nginx:1.20
           ports:
           - containerPort: 80
   ---
   apiVersion: v1
   kind: Service
   metadata:
     name: nginx-service
   spec:
     selector:
       app: nginx
     ports:
     - port: 80
       targetPort: 80
     type: LoadBalancer
   ```

3. **StatefulSet Example**
   ```yaml
   # statefulset.yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: web
   spec:
     serviceName: "nginx"
     replicas: 3
     selector:
       matchLabels:
         app: nginx
     template:
       metadata:
         labels:
           app: nginx
       spec:
         containers:
         - name: nginx
           image: nginx:1.20
           ports:
           - containerPort: 80
           volumeMounts:
           - name: www
             mountPath: /usr/share/nginx/html
     volumeClaimTemplates:
     - metadata:
         name: www
       spec:
         accessModes: [ "ReadWriteOnce" ]
         resources:
           requests:
             storage: 1Gi
   ```

### CI/CD Labs
1. **GitLab CI Pipeline**
   ```yaml
   # .gitlab-ci.yml
   stages:
     - build
     - test
     - deploy

   variables:
     DOCKER_DRIVER: overlay2
     DOCKER_TLS_CERTDIR: "/certs"

   build:
     stage: build
     image: docker:20.10.16
     services:
       - docker:20.10.16-dind
     script:
       - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
       - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA

   deploy:
     stage: deploy
     image: bitnami/kubectl:latest
     script:
       - kubectl set image deployment/myapp myapp=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
       - kubectl rollout status deployment/myapp
   ```

2. **ArgoCD Application**
   ```yaml
   # application.yaml
   apiVersion: argoproj.io/v1alpha1
   kind: Application
   metadata:
     name: myapp
     namespace: argocd
   spec:
     project: default
     source:
       repoURL: https://github.com/user/myapp-config
       targetRevision: HEAD
       path: k8s
     destination:
       server: https://kubernetes.default.svc
       namespace: production
     syncPolicy:
       automated:
         prune: true
         selfHeal: true
   ```

## 📚 Lý Thuyết Chi Tiết

### Theory Files
- **[Container Fundamentals Theory](./theory/container-fundamentals-theory.md)** - Kiến thức nền tảng về containerization, Docker architecture, và security
- **[Kubernetes Architecture Theory](./theory/kubernetes-architecture-theory.md)** - Kiến trúc Kubernetes, networking, storage, và advanced patterns
- **[CI/CD và DevOps Theory](./theory/cicd-devops-theory.md)** - Pipeline architecture, GitOps, và DevOps practices
- **[Container Security Theory](./theory/container-security-theory.md)** - Security model, best practices, và compliance

### Hands-on Labs
- **[Practical Labs](./labs/hands-on-labs.md)** - Comprehensive hands-on exercises cho tất cả topics
- **[Module Summary](./module-summary.md)** - Learning roadmap, assessment criteria, và career guidance

## 📚 Tài liệu Tham khảo

### Docker
- Docker Official Documentation
- Docker Deep Dive by Nigel Poulton
- Docker in Action by Jeff Nickoloff

### Kubernetes
- Kubernetes Official Documentation
- Kubernetes in Action by Marko Lukša
- Kubernetes Up & Running by Kelsey Hightower

### CI/CD
- GitLab CI/CD Documentation
- Jenkins User Handbook
- ArgoCD Documentation

## 🎓 Chứng chỉ Liên quan
- **Docker**: Docker Certified Associate (DCA)
- **Kubernetes**: CKA (Certified Kubernetes Administrator), CKAD (Certified Kubernetes Application Developer)
- **GitLab**: GitLab Certified CI/CD Specialist

## ⏱️ Thời gian Học: 3-4 tuần
- Tuần 1: Docker fundamentals + containerization
- Tuần 2: Kubernetes basics + cluster setup
- Tuần 3: Kubernetes advanced + workload management
- Tuần 4: CI/CD integration + GitOps practices

## 🔗 Chuyển sang Module tiếp theo
Với kiến thức container và orchestration, bạn sẵn sàng cho **Module 4: Database Management**.
