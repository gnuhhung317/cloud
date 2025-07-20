# Kubernetes Architecture và Orchestration Theory

## 1. Kubernetes Core Architecture

### 1.1 Cluster Architecture Overview

#### Control Plane Components
Kubernetes control plane bao gồm các component chịu trách nhiệm đưa ra quyết định cluster-wide và phát hiện/phản hồi cluster events.

```
┌─────────────────────────────────────────────────────────────┐
│                    Control Plane                            │
├──────────────┬──────────────┬──────────────┬───────────────┤
│ API Server   │    etcd      │  Scheduler   │   Controller  │
│              │              │              │   Manager     │
│ - REST API   │ - Key-Value  │ - Pod        │ - Node        │
│ - Auth       │ - Consistent │   Placement  │ - Replication │
│ - Admission  │ - Distributed│ - Resource   │ - Endpoint    │
│ - Validation │ - Watch API  │   Aware      │ - Service     │
└──────────────┴──────────────┴──────────────┴───────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
        ┌───────────▼──────────┐ ┌──────▼──────────┐
        │     Worker Node 1    │ │  Worker Node N  │
        │ ┌─────────────────┐  │ │ ┌─────────────┐ │
        │ │     kubelet     │  │ │ │   kubelet   │ │
        │ │   kube-proxy    │  │ │ │ kube-proxy  │ │
        │ │ Container Runtime│  │ │ │Runtime      │ │
        │ └─────────────────┘  │ │ └─────────────┘ │
        └──────────────────────┘ └─────────────────┘
```

#### API Server (kube-apiserver)
Central management entity và entry point cho tất cả REST operations:

**Core Responsibilities:**
```yaml
# API Server architecture
apiVersion: v1
kind: ConfigMap
metadata:
  name: kube-apiserver-config
data:
  # Authentication mechanisms
  authentication: |
    - X.509 certificates
    - Bearer tokens
    - Basic auth (deprecated)
    - OpenID Connect (OIDC)
    - Webhook token authentication
    
  # Authorization modes
  authorization: |
    - Node authorization
    - Attribute-based access control (ABAC)
    - Role-based access control (RBAC)
    - Webhook authorization
    
  # Admission controllers
  admission-controllers: |
    - NamespaceLifecycle
    - LimitRanger
    - ResourceQuota
    - ServiceAccount
    - SecurityContextDeny
    - PodSecurityPolicy
```

**Request Processing Flow:**
```bash
# API Request lifecycle
1. Authentication    # Xác thực user/service account
2. Authorization     # Kiểm tra permissions
3. Admission Control # Mutation & Validation webhooks
4. Schema Validation # OpenAPI schema validation
5. Storage          # Persist to etcd
6. Response         # Return response to client

# Example: Creating a Pod
kubectl apply -f pod.yaml
# -> Authentication (ServiceAccount token)
# -> Authorization (RBAC check)  
# -> Admission (PodSecurityPolicy)
# -> Validation (Resource limits)
# -> Storage (etcd)
# -> Response (201 Created)
```

#### etcd - Distributed Key-Value Store
Consistent và highly-available key value store:

**Data Model:**
```bash
# etcd key structure for Kubernetes
/registry/pods/namespace/pod-name
/registry/services/namespace/service-name
/registry/deployments/namespace/deployment-name
/registry/secrets/namespace/secret-name

# Example etcd query
etcdctl get /registry/pods/default/nginx-pod --print-value-only | jq .
{
  "kind": "Pod",
  "apiVersion": "v1",
  "metadata": {
    "name": "nginx-pod",
    "namespace": "default",
    "uid": "12345-67890-abcdef"
  }
}
```

**Consistency Model (Raft Consensus):**
```
Leader Election Process:
┌────────┐ ┌────────┐ ┌────────┐
│ Node 1 │ │ Node 2 │ │ Node 3 │
│Follower│ │ Leader │ │Follower│
└────────┘ └────────┘ └────────┘
     │         │         │
     └────────►│◄────────┘
              │
        Write Operations
     (Replicated to followers)

Failure Scenarios:
- Leader fails -> New election (majority needed)
- Network partition -> Majority partition continues
- Data corruption -> Automatic detection & repair
```

#### Scheduler (kube-scheduler)
Watches for newly created Pods với no assigned node và selects a node for them to run on:

**Scheduling Algorithm:**
```yaml
# Scheduling phases
scheduling_phases:
  1_filtering:
    description: "Find nodes that can run the Pod"
    filters:
      - NodeResourcesFit        # CPU/Memory availability
      - NodeAffinity           # Node selector requirements
      - PodAffinity/AntiAffinity # Pod placement preferences
      - TaintToleration        # Taint/Toleration matching
      - VolumeBinding          # Storage requirements
      
  2_scoring:
    description: "Rank viable nodes"
    scoring_functions:
      - NodeResourcesFit       # Prefer nodes with more available resources
      - InterPodAffinity      # Prefer spreading pods
      - ImageLocality         # Prefer nodes with container images
      - NodeAffinity          # Weight node preferences
      
  3_binding:
    description: "Assign Pod to highest-scored node"
    process:
      - Reserve resources on target node
      - Update Pod spec with nodeName
      - Persist binding to etcd
```

**Custom Scheduler Example:**
```go
// Custom scheduler implementation
func (s *Scheduler) scheduleOne(ctx context.Context) {
    // 1. Get next pod from scheduling queue
    podInfo := s.NextPod()
    pod := podInfo.Pod
    
    // 2. Run filtering phase
    feasibleNodes, err := s.findNodesThatFitPod(ctx, pod)
    if err != nil {
        s.recordSchedulingFailure(pod, err)
        return
    }
    
    // 3. Run scoring phase
    priorityList, err := s.prioritizeNodes(ctx, pod, feasibleNodes)
    if err != nil {
        s.recordSchedulingFailure(pod, err)
        return
    }
    
    // 4. Select best node
    host := s.selectHost(priorityList)
    
    // 5. Bind pod to node
    err = s.bind(ctx, pod, host)
    if err != nil {
        s.recordSchedulingFailure(pod, err)
        return
    }
}
```

#### Controller Manager (kube-controller-manager)
Runs controller processes và monitors cluster state:

**Built-in Controllers:**
```yaml
controllers:
  replication_controller:
    purpose: "Maintains desired number of pod replicas"
    reconciliation_loop: |
      observed_replicas = count_running_pods()
      desired_replicas = spec.replicas
      if observed_replicas < desired_replicas:
          create_pods(desired_replicas - observed_replicas)
      elif observed_replicas > desired_replicas:
          delete_pods(observed_replicas - desired_replicas)
          
  node_controller:
    purpose: "Manages node lifecycle"
    responsibilities:
      - Monitor node health (heartbeats)
      - Evict pods from unhealthy nodes
      - Update node conditions
      - Manage node CIDR allocation
      
  service_controller:
    purpose: "Manages Service objects"
    responsibilities:
      - Create/delete LoadBalancer resources
      - Update Service endpoints
      - Manage service account tokens
      
  endpoint_controller:
    purpose: "Populates Endpoints objects"
    process: |
      for each Service:
          pods = select_pods_by_label_selector()
          endpoints = extract_pod_ips_and_ports(pods)
          update_endpoints_object(endpoints)
```

### 1.2 Worker Node Architecture

#### kubelet - Node Agent
Primary node agent chạy trên mỗi node:

**Core Functions:**
```yaml
kubelet_responsibilities:
  pod_lifecycle:
    - Pull container images
    - Start/stop containers
    - Monitor container health
    - Restart failed containers
    - Report pod status to API server
    
  resource_management:
    - Enforce resource limits (CPU/Memory)
    - Manage volumes and mounts
    - Perform garbage collection
    - Monitor disk usage
    
  node_management:
    - Register node with cluster
    - Report node status and capacity
    - Handle node-level operations
    - Implement container runtime interface (CRI)
```

**Pod Lifecycle Management:**
```bash
# Pod phases in kubelet
Pending -> Running -> Succeeded/Failed

# Detailed state transitions
1. Pod Assigned to Node (by Scheduler)
2. kubelet pulls images
3. kubelet creates containers
4. Container runtime starts containers
5. kubelet monitors container health
6. kubelet reports status to API server

# Container restart policies
restartPolicy: Always   # Always restart on failure
restartPolicy: OnFailure # Restart only on failure (exit code != 0)
restartPolicy: Never    # Never restart
```

#### kube-proxy - Network Proxy
Maintains network rules on nodes và implements Kubernetes Service concept:

**Service Implementation Modes:**

**1. iptables Mode (Default):**
```bash
# iptables rules for Service
Chain KUBE-SERVICES (1 references)
-A KUBE-SERVICES -d 10.96.0.1/32 -p tcp -m tcp --dport 443 -j KUBE-SVC-NPX46M4PTMTKRN6Y

Chain KUBE-SVC-NPX46M4PTMTKRN6Y (1 references)
-A KUBE-SVC-NPX46M4PTMTKRN6Y -m statistic --mode random --probability 0.33333333349 -j KUBE-SEP-ENDPOINT1
-A KUBE-SVC-NPX46M4PTMTKRN6Y -m statistic --mode random --probability 0.50000000000 -j KUBE-SEP-ENDPOINT2
-A KUBE-SVC-NPX46M4PTMTKRN6Y -j KUBE-SEP-ENDPOINT3

# DNAT rules for load balancing
Chain KUBE-SEP-ENDPOINT1 (1 references)
-A KUBE-SEP-ENDPOINT1 -p tcp -m tcp -j DNAT --to-destination 192.168.1.10:8080
```

**2. IPVS Mode (High Performance):**
```bash
# IPVS virtual server configuration
ipvsadm -A -t 10.96.0.1:443 -s rr  # Round-robin scheduling
ipvsadm -a -t 10.96.0.1:443 -r 192.168.1.10:8080 -m  # Real server 1
ipvsadm -a -t 10.96.0.1:443 -r 192.168.1.11:8080 -m  # Real server 2

# Load balancing algorithms
rr     # Round Robin
lc     # Least Connection
wrr    # Weighted Round Robin
wlc    # Weighted Least Connection
sh     # Source Hashing
```

#### Container Runtime Interface (CRI)
Standardized interface between kubelet và container runtime:

**Runtime Options:**
```yaml
container_runtimes:
  containerd:
    features:
      - OCI-compliant
      - Built-in image management
      - gRPC API
      - Snapshotter plugins
    configuration:
      config_path: /etc/containerd/config.toml
      
  cri-o:
    features:
      - Lightweight CRI implementation
      - OCI-compliant
      - Kubernetes-focused
      - Pod-level lifecycle management
    configuration:
      config_path: /etc/crio/crio.conf
      
  docker_engine:
    status: deprecated
    replacement: containerd
    features:
      - Legacy support through dockershim
```

## 2. Kubernetes Networking Model

### 2.1 Container Network Interface (CNI)

#### CNI Plugin Architecture
```bash
# CNI plugin execution flow
1. kubelet calls CNI plugin with ADD command
2. Plugin assigns IP address to pod
3. Plugin configures network namespace
4. Plugin sets up routing rules
5. Plugin returns result to kubelet

# CNI configuration example
cat /etc/cni/net.d/10-flannel.conflist
{
  "name": "cbr0",
  "cniVersion": "0.3.1",
  "plugins": [
    {
      "type": "flannel",
      "delegate": {
        "hairpinMode": true,
        "isDefaultGateway": true
      }
    },
    {
      "type": "portmap",
      "capabilities": {
        "portMappings": true
      }
    }
  ]
}
```

#### Popular CNI Implementations

**Flannel (Simple Overlay):**
```yaml
flannel_architecture:
  networking_mode: "Overlay"
  encapsulation: "VXLAN"
  ip_allocation: "Host-gw or VXLAN"
  scalability: "Medium (up to 1000 nodes)"
  
  configuration:
    subnet: "10.244.0.0/16"
    backend:
      type: "vxlan"
      port: 8472
```

**Calico (Policy-Aware):**
```yaml
calico_architecture:
  networking_mode: "Native routing + Overlay"
  ip_allocation: "IPAM using BGP"
  policy_engine: "Felix (iptables/eBPF)"
  scalability: "High (5000+ nodes)"
  
  components:
    felix: "Policy enforcement agent"
    bird: "BGP route distribution"
    calico_node: "Per-node daemon"
    cni_plugin: "Network interface setup"
```

**Cilium (eBPF-based):**
```yaml
cilium_architecture:
  networking_mode: "eBPF datapath"
  policy_engine: "eBPF programs"
  observability: "Built-in Hubble"
  scalability: "Very High"
  
  features:
    l7_policy: "HTTP/gRPC/Kafka filtering"
    load_balancing: "eBPF-based"
    encryption: "Transparent encryption"
    service_mesh: "Sidecar-free"
```

### 2.2 Service Networking

#### Service Types và Implementation

**ClusterIP Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend-service
spec:
  type: ClusterIP
  selector:
    app: backend
  ports:
  - port: 80
    targetPort: 8080
    protocol: TCP

# Implementation details
implementation:
  virtual_ip: "Assigned from service CIDR"
  discovery: "DNS A record: backend-service.namespace.svc.cluster.local"
  load_balancing: "Round-robin via kube-proxy"
  scope: "Cluster-internal only"
```

**NodePort Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-nodeport
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080  # Range: 30000-32767

# Traffic flow
external_client -> node_ip:30080 -> cluster_ip:80 -> pod_ip:8080
```

**LoadBalancer Service:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-lb
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 8080

# Cloud provider integration
cloud_controller_manager:
  aws: "Creates ALB/NLB"
  gcp: "Creates TCP/UDP Load Balancer"
  azure: "Creates Azure Load Balancer"
```

#### Ingress Controllers

**Ingress Resource:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: api.example.com
    http:
      paths:
      - path: /v1
        pathType: Prefix
        backend:
          service:
            name: api-v1
            port:
              number: 80
      - path: /v2
        pathType: Prefix
        backend:
          service:
            name: api-v2
            port:
              number: 80
```

**NGINX Ingress Controller Architecture:**
```bash
# Controller components
nginx-ingress-controller
├── Watch Ingress resources
├── Generate nginx.conf
├── Reload nginx configuration
├── Handle SSL termination
└── Provide metrics/logging

# Configuration generation
ingress_resource -> nginx_configuration
{
  "server": {
    "server_name": "api.example.com",
    "location /v1": {
      "proxy_pass": "http://api-v1-upstream"
    },
    "location /v2": {
      "proxy_pass": "http://api-v2-upstream"
    }
  }
}
```

## 3. Storage Architecture

### 3.1 Volume Management

#### Persistent Volume (PV) Lifecycle
```yaml
# PV states
pv_lifecycle:
  available: "PV is available for claim"
  bound: "PV is bound to a PVC"
  released: "PVC is deleted but PV not yet reclaimed"
  failed: "Automatic reclamation failed"

# Reclaim policies
reclaim_policies:
  retain: "Manual reclamation required"
  delete: "PV and backing storage deleted"
  recycle: "Basic scrub (deprecated)"
```

#### Storage Classes và Dynamic Provisioning
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: ssd-storage
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp3
  iops: "3000"
  throughput: "125"
  encrypted: "true"
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
reclaimPolicy: Delete

# Dynamic provisioning flow
1. PVC created with storageClassName: ssd-storage
2. Storage controller watches for PVC
3. Controller calls provisioner (AWS EBS)
4. EBS volume created with specified parameters
5. PV object created and bound to PVC
6. Pod can mount the volume
```

#### Container Storage Interface (CSI)

**CSI Driver Architecture:**
```yaml
csi_components:
  controller_plugin:
    functions:
      - CreateVolume/DeleteVolume
      - ControllerPublishVolume/ControllerUnpublishVolume
      - ValidateVolumeCapabilities
      - ListVolumes/GetCapacity
    deployment: "StatefulSet or Deployment"
    
  node_plugin:
    functions:
      - NodeStageVolume/NodeUnstageVolume
      - NodePublishVolume/NodeUnpublishVolume
      - NodeGetInfo/NodeGetCapabilities
    deployment: "DaemonSet on every node"
    
  csi_driver_registration:
    purpose: "Register driver with kubelet"
    implementation: "Init container in node plugin"
```

**Volume Operations Flow:**
```bash
# Attach flow (for block storage)
1. Controller Plugin: CreateVolume() -> Volume created in storage backend
2. Controller Plugin: ControllerPublishVolume() -> Volume attached to node
3. Node Plugin: NodeStageVolume() -> Volume staged on node (format, etc.)
4. Node Plugin: NodePublishVolume() -> Volume bind-mounted into pod

# Detach flow
1. Node Plugin: NodeUnpublishVolume() -> Unmount from pod
2. Node Plugin: NodeUnstageVolume() -> Unstage from node
3. Controller Plugin: ControllerUnpublishVolume() -> Detach from node
4. Controller Plugin: DeleteVolume() -> Delete from storage backend
```

### 3.2 StatefulSet Storage Management

#### Stable Storage Guarantees
```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: database
spec:
  serviceName: "database"
  replicas: 3
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
      - name: postgres
        image: postgres:13
        volumeMounts:
        - name: data
          mountPath: /var/lib/postgresql/data
  volumeClaimTemplates:
  - metadata:
      name: data
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: "ssd-storage"
      resources:
        requests:
          storage: 100Gi

# StatefulSet guarantees
guarantees:
  stable_network_identity: "database-0.database, database-1.database, ..."
  stable_storage: "Each pod gets dedicated PVC"
  ordered_deployment: "Pods created sequentially (0, 1, 2, ...)"
  ordered_termination: "Pods deleted in reverse order (..., 2, 1, 0)"
```

## 4. Security Architecture

### 4.1 Authentication và Authorization

#### Authentication Methods
```yaml
authentication_methods:
  x509_certificates:
    usage: "User authentication"
    example:
      subject: "CN=john,O=developers,C=US"
      certificate_authority: "/etc/kubernetes/pki/ca.crt"
      
  service_accounts:
    usage: "Pod authentication"
    token_location: "/var/run/secrets/kubernetes.io/serviceaccount/token"
    automatic_mounting: true
    
  oidc_tokens:
    usage: "External identity provider"
    configuration:
      issuer_url: "https://accounts.google.com"
      client_id: "kubernetes"
      username_claim: "email"
      groups_claim: "groups"
      
  webhook_authentication:
    usage: "Custom authentication logic"
    webhook_url: "https://auth.example.com/authenticate"
```

#### Role-Based Access Control (RBAC)
```yaml
# Role definition
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]

---
# RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: production
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io

# Permission evaluation
rbac_evaluation:
  process:
    1. Extract user/group from authentication
    2. Find all RoleBindings for user/group
    3. Aggregate permissions from bound Roles
    4. Check if requested action is allowed
  result: "Allow if any rule matches, Deny otherwise"
```

#### Pod Security Standards
```yaml
# Pod Security Standards levels
pod_security_standards:
  privileged:
    description: "Unrestricted policy"
    restrictions: "None"
    
  baseline:
    description: "Minimally restrictive"
    restrictions:
      - No privileged containers
      - No host namespaces
      - No host ports
      - Limited volume types
      
  restricted:
    description: "Heavily restricted"
    restrictions:
      - All baseline restrictions
      - Must run as non-root
      - No privilege escalation
      - Seccomp profile required
      - Dropped capabilities

# Implementation via Pod Security Admission
apiVersion: v1
kind: Namespace
metadata:
  name: secure-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### 4.2 Network Security

#### Network Policies
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: production
spec:
  podSelector: {}  # Apply to all pods in namespace
  policyTypes:
  - Ingress
  # No ingress rules = deny all ingress

---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-frontend-to-backend
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8080

# Network policy enforcement
enforcement_modes:
  calico: "iptables rules per node"
  cilium: "eBPF programs"
  antrea: "Open vSwitch flows"
```

## 5. Workload Management Patterns

### 5.1 Deployment Strategies

#### Rolling Update Strategy
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 10
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 2      # Max pods that can be unavailable
      maxSurge: 2           # Max pods above desired replica count
  template:
    spec:
      containers:
      - name: web
        image: nginx:1.20
        readinessProbe:
          httpGet:
            path: /health
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5

# Rolling update process
rolling_update_flow:
  1. Create new ReplicaSet with updated template
  2. Scale up new ReplicaSet (respecting maxSurge)
  3. Wait for new pods to become ready
  4. Scale down old ReplicaSet (respecting maxUnavailable)
  5. Repeat until all pods are updated
  6. Delete old ReplicaSet (keep for rollback)
```

#### Blue-Green Deployment
```yaml
# Blue deployment (current)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-blue
  labels:
    version: blue
spec:
  replicas: 5
  selector:
    matchLabels:
      app: myapp
      version: blue

---
# Green deployment (new)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-green
  labels:
    version: green
spec:
  replicas: 5
  selector:
    matchLabels:
      app: myapp
      version: green

---
# Service switch
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp
    version: blue  # Switch to 'green' for deployment
  ports:
  - port: 80
    targetPort: 8080
```

#### Canary Deployment
```yaml
# Primary deployment (90% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-stable
spec:
  replicas: 9
  selector:
    matchLabels:
      app: myapp
      track: stable

---
# Canary deployment (10% traffic)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app-canary
spec:
  replicas: 1
  selector:
    matchLabels:
      app: myapp
      track: canary

---
# Service selects both
apiVersion: v1
kind: Service
metadata:
  name: app-service
spec:
  selector:
    app: myapp  # Both stable and canary pods
  ports:
  - port: 80
    targetPort: 8080
```

### 5.2 Auto-scaling

#### Horizontal Pod Autoscaler (HPA)
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: web-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  minReplicas: 3
  maxReplicas: 50
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  - type: Pods
    pods:
      metric:
        name: requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60

# HPA algorithm
hpa_calculation:
  desired_replicas = ceil(current_replicas * (current_metric / target_metric))
  
  example:
    current_replicas: 10
    current_cpu_utilization: 90%
    target_cpu_utilization: 70%
    desired_replicas = ceil(10 * (90/70)) = ceil(12.86) = 13
```

#### Vertical Pod Autoscaler (VPA)
```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: web-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: web-app
  updatePolicy:
    updateMode: "Auto"  # Auto, Initial, Off
  resourcePolicy:
    containerPolicies:
    - containerName: web
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2
        memory: 4Gi
      controlledResources: ["cpu", "memory"]

# VPA components
vpa_components:
  recommender:
    function: "Analyzes resource usage and provides recommendations"
    algorithm: "Histogram-based with exponential decay"
    
  updater:
    function: "Evicts pods when recommendations differ significantly"
    trigger: "Resource recommendation changes by >10%"
    
  admission_plugin:
    function: "Sets resource requests on new pods"
    mechanism: "Mutating admission webhook"
```

#### Cluster Autoscaler
```yaml
# Cluster Autoscaler configuration
cluster_autoscaler:
  scale_up_triggers:
    - Pods in Pending state due to insufficient resources
    - Node utilization below threshold with pending pods
    
  scale_down_triggers:
    - Node utilization below threshold (default 50%)
    - All pods can be moved to other nodes
    - No scale-down-disabled annotation
    
  node_group_scaling:
    min_size: 1
    max_size: 100
    desired_capacity: 3
    
  algorithms:
    expander: "random"  # random, most-pods, least-waste, priority
    scale_down_delay_after_add: "10m"
    scale_down_unneeded_time: "10m"
    max_node_provision_time: "15m"
```

## 6. Advanced Scheduling

### 6.1 Node Affinity và Pod Affinity

#### Node Affinity
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: with-node-affinity
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: zone
            operator: In
            values:
            - zone-1
            - zone-2
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        preference:
          matchExpressions:
          - key: instance-type
            operator: In
            values:
            - c5.large
            - c5.xlarge
  containers:
  - name: app
    image: nginx

# Affinity evaluation
node_affinity_evaluation:
  required_terms: "Must match (hard constraint)"
  preferred_terms: "Weighted preferences (soft constraint)"
  
  operator_types:
    In: "Label value in specified list"
    NotIn: "Label value not in specified list"
    Exists: "Label key exists"
    DoesNotExist: "Label key does not exist"
    Gt: "Label value greater than"
    Lt: "Label value less than"
```

#### Pod Affinity và Anti-Affinity
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-cache
spec:
  replicas: 3
  selector:
    matchLabels:
      app: redis-cache
  template:
    metadata:
      labels:
        app: redis-cache
    spec:
      affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - redis-cache
            topologyKey: kubernetes.io/hostname
        podAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - web-frontend
              topologyKey: zone

# Topology spreading
pod_topology_spread:
  purpose: "Even distribution across topology domains"
  example:
    topologySpreadConstraints:
    - maxSkew: 1
      topologyKey: zone
      whenUnsatisfiable: DoNotSchedule
      labelSelector:
        matchLabels:
          app: web-frontend
```

### 6.2 Taints và Tolerations

#### Taint Effects
```bash
# Taint a node
kubectl taint nodes node1 key1=value1:NoSchedule
kubectl taint nodes node1 key1=value1:PreferNoSchedule
kubectl taint nodes node1 key1=value1:NoExecute

# Taint effects
taint_effects:
  NoSchedule: "Pods won't be scheduled unless they tolerate the taint"
  PreferNoSchedule: "Scheduler tries to avoid placing pods"
  NoExecute: "Existing pods will be evicted unless they tolerate"
```

#### Tolerations
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: tolerant-pod
spec:
  tolerations:
  - key: "key1"
    operator: "Equal"
    value: "value1"
    effect: "NoSchedule"
  - key: "key2"
    operator: "Exists"
    effect: "NoExecute"
    tolerationSeconds: 300  # Pod will be evicted after 5 minutes
  containers:
  - name: app
    image: nginx

# Built-in tolerations
default_tolerations:
  node_not_ready:
    key: "node.kubernetes.io/not-ready"
    effect: "NoExecute"
    tolerationSeconds: 300
    
  node_unreachable:
    key: "node.kubernetes.io/unreachable"
    effect: "NoExecute"
    tolerationSeconds: 300
```

## 7. Observability và Monitoring

### 7.1 Metrics Architecture

#### Metrics Server
```yaml
# Metrics Server provides resource metrics API
metrics_server:
  purpose: "Provides container CPU and memory usage metrics"
  api_endpoint: "/apis/metrics.k8s.io/v1beta1"
  data_source: "kubelet cAdvisor"
  retention: "In-memory only (no historical data)"
  
  usage:
    kubectl_top: "kubectl top nodes/pods"
    hpa: "Horizontal Pod Autoscaler"
    vpa: "Vertical Pod Autoscaler"
```

#### Prometheus Integration
```yaml
# ServiceMonitor for automatic discovery
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: web-app-metrics
spec:
  selector:
    matchLabels:
      app: web-app
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics

# Custom metrics for HPA
apiVersion: v1
kind: Service
metadata:
  name: custom-metrics-api
  labels:
    app: custom-metrics-api
spec:
  ports:
  - port: 443
    targetPort: 8443
  selector:
    app: custom-metrics-api

# Prometheus adapter configuration
prometheus_adapter:
  custom_metrics:
    - seriesQuery: 'http_requests_per_second{namespace!="",pod!=""}'
      resources:
        overrides:
          namespace: {resource: "namespace"}
          pod: {resource: "pod"}
      name:
        matches: "^(.*)_per_second"
        as: "${1}_rate"
      metricsQuery: 'avg(<<.Series>>{<<.LabelMatchers>>}) by (<<.GroupBy>>)'
```

### 7.2 Logging Architecture

#### Cluster-level Logging Patterns

**Node-level Logging Agent (DaemonSet):**
```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd-logger
spec:
  selector:
    matchLabels:
      name: fluentd-logger
  template:
    metadata:
      labels:
        name: fluentd-logger
    spec:
      containers:
      - name: fluentd
        image: fluentd:v1.14
        volumeMounts:
        - name: varlibdockercontainers
          mountPath: /var/lib/docker/containers
          readOnly: true
        - name: varlog
          mountPath: /var/log
          readOnly: true
      volumes:
      - name: varlibdockercontainers
        hostPath:
          path: /var/lib/docker/containers
      - name: varlog
        hostPath:
          path: /var/log

# Log aggregation flow
log_flow:
  1_generation: "Applications write to stdout/stderr"
  2_collection: "Container runtime captures logs"
  3_storage: "Logs stored in /var/log/containers/"
  4_forwarding: "DaemonSet agents forward to aggregator"
  5_processing: "Central processing (parsing, filtering)"
  6_storage: "Long-term storage (Elasticsearch, S3)"
  7_visualization: "Kibana, Grafana for analysis"
```

**Sidecar Pattern:**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-with-sidecar-logging
spec:
  containers:
  - name: app
    image: myapp:latest
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app
  - name: log-forwarder
    image: fluentd:v1.14
    volumeMounts:
    - name: shared-logs
      mountPath: /var/log/app
      readOnly: true
    env:
    - name: FLUENTD_CONF
      value: "forwarder.conf"
  volumes:
  - name: shared-logs
    emptyDir: {}
```

## 8. Troubleshooting Framework

### 8.1 Diagnostic Commands

#### Cluster-level Diagnostics
```bash
# Cluster health overview
kubectl cluster-info
kubectl get componentstatuses
kubectl get nodes -o wide

# Resource usage
kubectl top nodes
kubectl top pods --all-namespaces
kubectl describe node NODE_NAME

# Event analysis
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get events --field-selector involvedObject.name=POD_NAME

# etcd health (if accessible)
ETCDCTL_API=3 etcdctl --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key \
  endpoint health
```

#### Pod-level Diagnostics
```bash
# Pod lifecycle analysis
kubectl get pod POD_NAME -o yaml
kubectl describe pod POD_NAME
kubectl logs POD_NAME --previous  # Previous container instance

# Resource constraints
kubectl top pod POD_NAME --containers
kubectl exec POD_NAME -- cat /proc/meminfo
kubectl exec POD_NAME -- df -h

# Network connectivity
kubectl exec POD_NAME -- nslookup kubernetes.default.svc.cluster.local
kubectl exec POD_NAME -- wget -qO- http://SERVICE_NAME:PORT/health
kubectl exec POD_NAME -- netstat -tuln
```

### 8.2 Common Issues và Resolution

#### Scheduling Issues
```yaml
scheduling_problems:
  insufficient_resources:
    symptoms:
      - Pod stuck in Pending state
      - Event: "Insufficient cpu/memory"
    diagnosis:
      kubectl describe pod POD_NAME
      kubectl top nodes
    resolution:
      - Add more nodes
      - Reduce resource requests
      - Use priority classes
      
  taints_tolerations:
    symptoms:
      - Pod pending with FailedScheduling
      - Event: "Taint not tolerated"
    diagnosis:
      kubectl describe nodes
      kubectl get pod POD_NAME -o yaml | grep -A5 tolerations
    resolution:
      - Add tolerations to pod
      - Remove taints from nodes
      - Use node selectors
```

#### Network Issues
```yaml
network_problems:
  dns_resolution:
    symptoms:
      - Service discovery failures
      - nslookup timeouts
    diagnosis:
      kubectl exec POD_NAME -- nslookup kubernetes.default.svc.cluster.local
      kubectl get pods -n kube-system -l k8s-app=kube-dns
    resolution:
      - Check CoreDNS pods health
      - Verify DNS policy in pod spec
      - Check network policies
      
  service_connectivity:
    symptoms:
      - Connection refused errors
      - Timeout connecting to services
    diagnosis:
      kubectl get endpoints SERVICE_NAME
      kubectl exec POD_NAME -- telnet SERVICE_IP SERVICE_PORT
    resolution:
      - Verify service selector matches pod labels
      - Check target port configuration
      - Validate network policies
```

#### Storage Issues
```yaml
storage_problems:
  pvc_pending:
    symptoms:
      - PVC stuck in Pending state
      - Pod unable to start
    diagnosis:
      kubectl describe pvc PVC_NAME
      kubectl get storageclass
    resolution:
      - Check storage class provisioner
      - Verify storage capacity
      - Review volume binding mode
      
  mount_failures:
    symptoms:
      - Pod stuck in ContainerCreating
      - Mount errors in events
    diagnosis:
      kubectl describe pod POD_NAME
      kubectl get pv PV_NAME -o yaml
    resolution:
      - Check node storage driver
      - Verify volume access modes
      - Review security contexts
```

Lý thuyết này cung cấp hiểu biết sâu sắc về Kubernetes architecture và operations, từ core components đến advanced patterns, giúp engineers tại Viettel IDC thành thạo container orchestration trong môi trường enterprise.
