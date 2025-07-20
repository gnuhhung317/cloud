# Container Security và Best Practices Theory

## 1. Container Security Fundamentals

### 1.1 Container Security Model

#### Security Boundaries và Attack Surface
Container security model dựa trên nhiều layers của isolation và protection:

```yaml
security_layers:
  application_layer:
    vulnerabilities:
      - Code injection attacks
      - Business logic flaws
      - Authentication bypasses
      - Data exposure
    mitigation:
      - Secure coding practices
      - Input validation
      - Output encoding
      - Authentication/authorization
      
  container_runtime_layer:
    vulnerabilities:
      - Container escape
      - Privilege escalation
      - Resource exhaustion
      - Image vulnerabilities
    mitigation:
      - Runtime security policies
      - Resource limits
      - Read-only filesystems
      - Image scanning
      
  kernel_layer:
    vulnerabilities:
      - Kernel exploits
      - Namespace breakouts
      - cgroup bypasses
      - Syscall abuse
    mitigation:
      - Kernel hardening
      - Seccomp profiles
      - AppArmor/SELinux
      - Capability dropping
      
  infrastructure_layer:
    vulnerabilities:
      - Network attacks
      - Storage access
      - Node compromise
      - Cluster misconfigurations
    mitigation:
      - Network segmentation
      - Encryption at rest/transit
      - Node hardening
      - RBAC policies
```

#### Shared Kernel Risks
Containers chia sẻ kernel với host, tạo ra unique security challenges:

```bash
# Kernel namespace isolation
# Process namespace - processes visible only within container
ps aux  # Inside container shows only container processes
ps aux  # On host shows all processes including containers

# Network namespace - separate network stack
ip netns list  # List network namespaces
ip netns exec container_ns ip addr show  # Container network config

# Mount namespace - separate filesystem view
mount  # Inside container shows container mounts only
mount  # On host shows all mounts including container volumes

# User namespace - UID/GID mapping
# Container root (UID 0) maps to unprivileged user on host
id  # Inside container: uid=0(root)
ps -eo pid,uid,cmd | grep container_process  # Host: shows mapped UID

# Potential escape vectors
kernel_exploits:
  dirty_cow: "CVE-2016-5195 - Memory corruption leading to privilege escalation"
  container_escape: "CVE-2019-5736 - runc container escape via /proc/self/exe"
  mount_namespace_bypass: "Improper mount handling leading to host access"
```

### 1.2 Image Security

#### Base Image Selection
```dockerfile
# Security-focused base image selection

# BAD: Using latest tag (unpredictable)
FROM ubuntu:latest

# BAD: Full OS with unnecessary packages
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y \
    vim curl wget git build-essential

# GOOD: Minimal base image with specific version
FROM alpine:3.16.2
# Alpine Linux advantages:
# - Minimal attack surface (5MB base)
# - Security-focused distribution
# - Package signing and verification
# - Regular security updates

# BETTER: Distroless images (Google)
FROM gcr.io/distroless/java:11
# Distroless advantages:
# - No shell, package manager, or unnecessary binaries
# - Minimal attack surface
# - Reduced CVE exposure
# - Smaller image size

# BEST: Scratch for static binaries
FROM scratch
COPY ca-certificates.crt /etc/ssl/certs/
COPY myapp /
ENTRYPOINT ["/myapp"]
```

#### Multi-stage Build Security
```dockerfile
# Security-optimized multi-stage build
# Build stage - Contains build tools and source code
FROM golang:1.19-alpine AS builder
WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git ca-certificates tzdata

# Copy dependency files first (better caching)
COPY go.mod go.sum ./
RUN go mod download && go mod verify

# Copy source code
COPY . .

# Build with security flags
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' \
    -a -installsuffix cgo \
    -o main .

# Security scanning during build
RUN go mod tidy
RUN go list -json -m all | nancy sleuth

# Runtime stage - Minimal runtime environment
FROM scratch
LABEL maintainer="security-team@company.com"
LABEL version="1.0.0"
LABEL description="Production web application"

# Copy only necessary files from builder
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=builder /app/main /app

# Create non-root user (scratch doesn't have useradd)
# We handle this in the builder stage
FROM builder AS user-creator
RUN adduser -D -s /bin/sh -u 1001 appuser

FROM scratch
COPY --from=user-creator /etc/passwd /etc/passwd
COPY --from=user-creator /etc/group /etc/group
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=builder /app/main /app

# Security configurations
USER 1001
EXPOSE 8080
ENTRYPOINT ["/app"]

# Image metadata for security scanning
LABEL security.scan.enabled="true"
LABEL security.scan.vendor="trivy"
LABEL security.compliance.policy="enterprise-strict"
```

#### Image Vulnerability Management
```yaml
vulnerability_management:
  scanning_stages:
    build_time:
      tools:
        - trivy
        - clair
        - snyk
        - aqua_microscanner
      integration:
        - CI/CD pipeline gates
        - Registry webhooks
        - IDE plugins
        - Pre-commit hooks
        
    runtime:
      tools:
        - falco
        - sysdig
        - aqua_runtime
        - twistlock
      monitoring:
        - Runtime behavior analysis
        - Anomaly detection
        - Process monitoring
        - Network analysis
        
  vulnerability_database:
    sources:
      - National Vulnerability Database (NVD)
      - CVE (Common Vulnerabilities and Exposures)
      - Vendor-specific databases
      - Security research feeds
    update_frequency: "Hourly"
    
  remediation_workflow:
    critical_severity:
      action: "Block deployment"
      timeline: "Immediate fix required"
      escalation: "Security team notification"
      
    high_severity:
      action: "Warning with approval gate"
      timeline: "Fix within 24 hours"
      escalation: "Development team lead"
      
    medium_severity:
      action: "Log and track"
      timeline: "Fix within 1 week"
      escalation: "Sprint planning inclusion"
```

### 1.3 Runtime Security

#### Security Contexts
```yaml
# Pod-level security context
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  securityContext:
    # Run as non-root user
    runAsNonRoot: true
    runAsUser: 1001
    runAsGroup: 2001
    
    # Filesystem permissions
    fsGroup: 2001
    fsGroupChangePolicy: "OnRootMismatch"
    
    # SELinux context
    seLinuxOptions:
      level: "s0:c123,c456"
      role: "container_r"
      type: "container_t"
      user: "container_u"
    
    # Seccomp profile
    seccompProfile:
      type: RuntimeDefault  # Use runtime's default seccomp profile
      # type: Localhost
      # localhostProfile: "profiles/audit.json"
    
    # Windows-specific (if applicable)
    windowsOptions:
      gmsaCredentialSpecName: "my-gmsa-credential"
      runAsUserName: "ContainerUser"
    
    # System controls (sysctls)
    sysctls:
    - name: net.core.somaxconn
      value: "1024"
  
  containers:
  - name: app
    image: myapp:secure
    securityContext:
      # Container-level overrides
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      
      # Capabilities
      capabilities:
        drop:
        - ALL  # Drop all capabilities
        add:
        - NET_BIND_SERVICE  # Only add necessary capabilities
      
      # Run as specific user (overrides pod-level)
      runAsUser: 1002
      runAsGroup: 2002
    
    # Resource limits (security through constraints)
    resources:
      limits:
        cpu: "500m"
        memory: "512Mi"
        ephemeral-storage: "1Gi"
      requests:
        cpu: "100m"
        memory: "128Mi"
        ephemeral-storage: "100Mi"
    
    # Volume mounts with security options
    volumeMounts:
    - name: app-data
      mountPath: /data
      readOnly: false
    - name: config
      mountPath: /etc/config
      readOnly: true
    - name: tmp
      mountPath: /tmp
      
  volumes:
  - name: app-data
    persistentVolumeClaim:
      claimName: app-data-pvc
  - name: config
    configMap:
      name: app-config
      defaultMode: 0444  # Read-only for owner, group, others
  - name: tmp
    emptyDir:
      sizeLimit: "100Mi"
```

#### Linux Capabilities Management
```bash
# Understanding Linux capabilities
# Traditional model: root vs non-root (all or nothing)
# Capabilities model: Granular privileges

# View capabilities of a process
grep Cap /proc/self/status
CapInh: 0000000000000000  # Inheritable
CapPrm: 0000000000000000  # Permitted  
CapEff: 0000000000000000  # Effective
CapBnd: 0000003fffffffff  # Bounding set

# Common capabilities and their purposes
capabilities_reference:
  CAP_NET_BIND_SERVICE: "Bind to ports below 1024"
  CAP_NET_ADMIN: "Network administration (iptables, routing)"
  CAP_SYS_ADMIN: "System administration (mount, swapon, etc.)"
  CAP_SYS_TIME: "Set system clock"
  CAP_KILL: "Send signals to processes"
  CAP_SETUID: "Change UID"
  CAP_SETGID: "Change GID"
  CAP_DAC_OVERRIDE: "Bypass file permission checks"
  CAP_CHOWN: "Change file ownership"

# Container capability management
docker run --cap-drop ALL --cap-add NET_BIND_SERVICE nginx
# Kubernetes equivalent in SecurityContext shown above

# Viewing container capabilities
kubectl exec pod-name -- cat /proc/1/status | grep Cap
kubectl exec pod-name -- capsh --print
```

#### Seccomp Profiles
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": [
    "SCMP_ARCH_X86_64",
    "SCMP_ARCH_X86",
    "SCMP_ARCH_X32"
  ],
  "syscalls": [
    {
      "names": [
        "accept",
        "accept4",
        "access",
        "adjtimex",
        "alarm",
        "bind",
        "brk",
        "capget",
        "capset",
        "chdir",
        "chmod",
        "chown",
        "chown32",
        "clock_getres",
        "clock_gettime",
        "clock_nanosleep",
        "close",
        "connect",
        "copy_file_range",
        "creat",
        "dup",
        "dup2",
        "dup3",
        "epoll_create",
        "epoll_create1",
        "epoll_ctl",
        "epoll_pwait",
        "epoll_wait",
        "eventfd",
        "eventfd2",
        "execve",
        "execveat",
        "exit",
        "exit_group",
        "faccessat",
        "fadvise64",
        "fadvise64_64",
        "fallocate",
        "fanotify_mark",
        "fchdir",
        "fchmod",
        "fchmodat",
        "fchown",
        "fchown32",
        "fchownat",
        "fcntl",
        "fcntl64",
        "fdatasync",
        "fgetxattr",
        "flistxattr",
        "flock",
        "fork",
        "fremovexattr",
        "fsetxattr",
        "fstat",
        "fstat64",
        "fstatat64",
        "fstatfs",
        "fstatfs64",
        "fsync",
        "ftruncate",
        "ftruncate64",
        "futex",
        "getcwd",
        "getdents",
        "getdents64",
        "getegid",
        "getegid32",
        "geteuid",
        "geteuid32",
        "getgid",
        "getgid32",
        "getgroups",
        "getgroups32",
        "getitimer",
        "getpgid",
        "getpgrp",
        "getpid",
        "getppid",
        "getpriority",
        "getrandom",
        "getresgid",
        "getresgid32",
        "getresuid",
        "getresuid32",
        "getrlimit",
        "get_robust_list",
        "getrusage",
        "getsid",
        "getsockname",
        "getsockopt",
        "get_thread_area",
        "gettid",
        "gettimeofday",
        "getuid",
        "getuid32",
        "getxattr",
        "inotify_add_watch",
        "inotify_init",
        "inotify_init1",
        "inotify_rm_watch",
        "io_cancel",
        "ioctl",
        "io_destroy",
        "io_getevents",
        "ioprio_get",
        "ioprio_set",
        "io_setup",
        "io_submit",
        "ipc",
        "kill",
        "lchown",
        "lchown32",
        "lgetxattr",
        "link",
        "linkat",
        "listen",
        "listxattr",
        "llistxattr",
        "lremovexattr",
        "lseek",
        "lsetxattr",
        "lstat",
        "lstat64",
        "madvise",
        "memfd_create",
        "mincore",
        "mkdir",
        "mkdirat",
        "mknod",
        "mknodat",
        "mlock",
        "mlock2",
        "mlockall",
        "mmap",
        "mmap2",
        "mprotect",
        "mq_getsetattr",
        "mq_notify",
        "mq_open",
        "mq_timedreceive",
        "mq_timedsend",
        "mq_unlink",
        "mremap",
        "msgctl",
        "msgget",
        "msgrcv",
        "msgsnd",
        "msync",
        "munlock",
        "munlockall",
        "munmap",
        "nanosleep",
        "newfstatat",
        "_newselect",
        "open",
        "openat",
        "pause",
        "pipe",
        "pipe2",
        "poll",
        "ppoll",
        "prctl",
        "pread64",
        "preadv",
        "prlimit64",
        "pselect6",
        "ptrace",
        "pwrite64",
        "pwritev",
        "read",
        "readahead",
        "readlink",
        "readlinkat",
        "readv",
        "recv",
        "recvfrom",
        "recvmmsg",
        "recvmsg",
        "remap_file_pages",
        "removexattr",
        "rename",
        "renameat",
        "renameat2",
        "restart_syscall",
        "rmdir",
        "rt_sigaction",
        "rt_sigpending",
        "rt_sigprocmask",
        "rt_sigqueueinfo",
        "rt_sigreturn",
        "rt_sigsuspend",
        "rt_sigtimedwait",
        "rt_tgsigqueueinfo",
        "sched_getaffinity",
        "sched_getattr",
        "sched_getparam",
        "sched_get_priority_max",
        "sched_get_priority_min",
        "sched_getscheduler",
        "sched_rr_get_interval",
        "sched_setaffinity",
        "sched_setattr",
        "sched_setparam",
        "sched_setscheduler",
        "sched_yield",
        "seccomp",
        "select",
        "semctl",
        "semget",
        "semop",
        "semtimedop",
        "send",
        "sendfile",
        "sendfile64",
        "sendmmsg",
        "sendmsg",
        "sendto",
        "setfsgid",
        "setfsgid32",
        "setfsuid",
        "setfsuid32",
        "setgid",
        "setgid32",
        "setgroups",
        "setgroups32",
        "setitimer",
        "setpgid",
        "setpriority",
        "setregid",
        "setregid32",
        "setresgid",
        "setresgid32",
        "setresuid",
        "setresuid32",
        "setreuid",
        "setreuid32",
        "setrlimit",
        "set_robust_list",
        "setsid",
        "setsockopt",
        "set_thread_area",
        "set_tid_address",
        "setuid",
        "setuid32",
        "setxattr",
        "shmat",
        "shmctl",
        "shmdt",
        "shmget",
        "shutdown",
        "sigaltstack",
        "signalfd",
        "signalfd4",
        "sigreturn",
        "socket",
        "socketcall",
        "socketpair",
        "splice",
        "stat",
        "stat64",
        "statfs",
        "statfs64",
        "statx",
        "symlink",
        "symlinkat",
        "sync",
        "sync_file_range",
        "syncfs",
        "sysinfo",
        "tee",
        "tgkill",
        "time",
        "timer_create",
        "timer_delete",
        "timerfd_create",
        "timerfd_gettime",
        "timerfd_settime",
        "timer_getoverrun",
        "timer_gettime",
        "timer_settime",
        "times",
        "tkill",
        "truncate",
        "truncate64",
        "ugetrlimit",
        "umask",
        "uname",
        "unlink",
        "unlinkat",
        "utime",
        "utimensat",
        "utimes",
        "vfork",
        "vmsplice",
        "wait4",
        "waitid",
        "waitpid",
        "write",
        "writev"
      ],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}

# Seccomp profile application
seccomp_usage:
  docker: |
    docker run --security-opt seccomp=./custom-profile.json nginx
    
  kubernetes: |
    apiVersion: v1
    kind: Pod
    spec:
      securityContext:
        seccompProfile:
          type: Localhost
          localhostProfile: profiles/custom-profile.json
          
  runtime_default: |
    # Most secure option - use runtime's default profile
    seccompProfile:
      type: RuntimeDefault
```

## 2. Network Security

### 2.1 Network Segmentation

#### Kubernetes Network Policies
```yaml
# Default deny all ingress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-ingress
  namespace: production
spec:
  podSelector: {}  # Applies to all pods in namespace
  policyTypes:
  - Ingress

---
# Default deny all egress traffic
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-egress
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Egress

---
# Allow specific communication patterns
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-to-api-policy
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: api-server
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Allow traffic from web frontend
  - from:
    - namespaceSelector:
        matchLabels:
          name: production
    - podSelector:
        matchLabels:
          app: web-frontend
    ports:
    - protocol: TCP
      port: 8080
  # Allow traffic from monitoring
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    - podSelector:
        matchLabels:
          app: prometheus
    ports:
    - protocol: TCP
      port: 9090
  egress:
  # Allow DNS resolution
  - to: []
    ports:
    - protocol: UDP
      port: 53
    - protocol: TCP
      port: 53
  # Allow database access
  - to:
    - podSelector:
        matchLabels:
          app: database
    ports:
    - protocol: TCP
      port: 5432
  # Allow external API calls
  - to: []
    ports:
    - protocol: TCP
      port: 443

---
# Namespace-level isolation
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: namespace-isolation
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  # Only allow traffic from same namespace
  - from:
    - namespaceSelector:
        matchLabels:
          name: production
  # Allow traffic from ingress controllers
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-system
  egress:
  # Allow traffic to same namespace
  - to:
    - namespaceSelector:
        matchLabels:
          name: production
  # Allow DNS
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    - podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

#### Cilium Network Policies (Extended)
```yaml
# L7 HTTP policy with Cilium
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: l7-http-policy
  namespace: production
spec:
  endpointSelector:
    matchLabels:
      app: api-server
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: web-frontend
    toPorts:
    - ports:
      - port: "8080"
        protocol: TCP
      rules:
        http:
        - method: "GET"
          path: "/api/v1/.*"
        - method: "POST"
          path: "/api/v1/users"
          headers:
          - "Content-Type: application/json"
        - method: "PUT"
          path: "/api/v1/users/[0-9]+"

---
# DNS-based egress policy
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: dns-egress-policy
spec:
  endpointSelector:
    matchLabels:
      app: web-scraper
  egress:
  - toFQDNs:
    - matchName: "api.github.com"
    - matchPattern: "*.googleapis.com"
  - toEndpoints:
    - matchLabels:
        "k8s:io.kubernetes.pod.namespace": kube-system
        "k8s:k8s-app": kube-dns
    toPorts:
    - ports:
      - port: "53"
        protocol: UDP
      rules:
        dns:
        - matchPattern: "*.github.com"
        - matchPattern: "*.googleapis.com"

---
# Service mesh integration
apiVersion: "cilium.io/v2"
kind: CiliumNetworkPolicy
metadata:
  name: service-mesh-policy
spec:
  endpointSelector:
    matchLabels:
      app: payment-service
  ingress:
  - fromEndpoints:
    - matchLabels:
        app: order-service
    toPorts:
    - ports:
      - port: "8080"
      rules:
        http:
        - method: "POST"
          path: "/payment/process"
          headers:
          - "X-Request-ID: .*"
          - "Authorization: Bearer .*"
```

### 2.2 TLS/mTLS Implementation

#### Certificate Management
```yaml
# Cert-manager configuration for automatic TLS
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@company.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
    - dns01:
        route53:
          region: us-west-2
          accessKeyID: AKIA...
          secretAccessKeySecretRef:
            name: route53-credentials
            key: secret-access-key

---
# Certificate for service
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: api-tls
  namespace: production
spec:
  secretName: api-tls-secret
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
  - api.company.com
  - api-internal.company.com

---
# Mutual TLS with Istio
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT  # Require mTLS for all communication

---
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: payment-service-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  rules:
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/order-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/payment/*"]
    when:
    - key: request.headers[x-request-id]
      values: ["*"]
```

### 2.3 Service Mesh Security

#### Istio Security Model
```yaml
# Workload identity and authentication
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: payment-service-mtls
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-service
  mtls:
    mode: STRICT
  portLevelMtls:
    8080:
      mode: STRICT
    9090:  # Metrics endpoint
      mode: DISABLE

---
# JWT authentication for end users
apiVersion: security.istio.io/v1beta1
kind: RequestAuthentication
metadata:
  name: jwt-auth
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-gateway
  jwtRules:
  - issuer: "https://auth.company.com"
    jwksUri: "https://auth.company.com/.well-known/jwks.json"
    audiences:
    - "api.company.com"
    forwardOriginalToken: true

---
# Authorization policies
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: api-gateway-authz
  namespace: production
spec:
  selector:
    matchLabels:
      app: api-gateway
  rules:
  # Allow authenticated users to access public API
  - from:
    - source:
        requestPrincipals: ["https://auth.company.com/*"]
    to:
    - operation:
        methods: ["GET", "POST"]
        paths: ["/api/v1/public/*"]
  # Allow admin users to access admin API
  - from:
    - source:
        requestPrincipals: ["https://auth.company.com/*"]
    to:
    - operation:
        methods: ["GET", "POST", "PUT", "DELETE"]
        paths: ["/api/v1/admin/*"]
    when:
    - key: request.auth.claims[role]
      values: ["admin"]
  # Allow service-to-service communication
  - from:
    - source:
        principals: ["cluster.local/ns/production/sa/order-service"]
    to:
    - operation:
        methods: ["POST"]
        paths: ["/api/v1/internal/*"]

---
# Security policy for external services
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: external-service-policy
  namespace: production
spec:
  selector:
    matchLabels:
      app: payment-processor
  rules:
  - to:
    - operation:
        hosts: ["payment-gateway.external.com"]
        methods: ["POST"]
        paths: ["/v2/charges"]
    when:
    - key: source.ip
      values: ["10.0.0.0/8"]  # Only from internal network
```

## 3. Secrets Management

### 3.1 Kubernetes Secrets Security

#### Secret Encryption at Rest
```yaml
# Encryption configuration for etcd
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
- resources:
  - secrets
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}  # Fallback for reading old data
- resources:
  - configmaps
  providers:
  - aescbc:
      keys:
      - name: key1
        secret: <base64-encoded-32-byte-key>
  - identity: {}

# Enable encryption in kube-apiserver
kube_apiserver_flags:
  - --encryption-provider-config=/etc/kubernetes/encryption-config.yaml
```

#### Secret Management Best Practices
```yaml
# Secure secret definition
apiVersion: v1
kind: Secret
metadata:
  name: database-credentials
  namespace: production
  labels:
    app: database
    environment: production
  annotations:
    # Rotation information
    secrets.company.com/last-rotated: "2023-07-15T10:30:00Z"
    secrets.company.com/rotation-schedule: "90d"
    # Access restrictions
    secrets.company.com/access-level: "high"
    secrets.company.com/audit-required: "true"
type: Opaque
data:
  username: <base64-encoded-username>
  password: <base64-encoded-password>
  connection-string: <base64-encoded-connection-string>

---
# ServiceAccount with limited access
apiVersion: v1
kind: ServiceAccount
metadata:
  name: app-service-account
  namespace: production
  annotations:
    secrets.company.com/allowed-secrets: "database-credentials,api-keys"
automountServiceAccountToken: false  # Disable automatic token mounting

---
# RBAC for secret access
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: production
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["database-credentials"]  # Specific secret access
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secret-reader-binding
  namespace: production
subjects:
- kind: ServiceAccount
  name: app-service-account
  namespace: production
roleRef:
  kind: Role
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io

---
# Pod with secure secret usage
apiVersion: v1
kind: Pod
metadata:
  name: secure-app
  namespace: production
spec:
  serviceAccountName: app-service-account
  securityContext:
    runAsNonRoot: true
    runAsUser: 1001
    fsGroup: 2001
  containers:
  - name: app
    image: myapp:secure
    env:
    # Use environment variables for non-sensitive config
    - name: DATABASE_HOST
      value: "db.production.svc.cluster.local"
    - name: DATABASE_PORT
      value: "5432"
    # Use secret for sensitive data
    - name: DATABASE_USERNAME
      valueFrom:
        secretKeyRef:
          name: database-credentials
          key: username
    - name: DATABASE_PASSWORD
      valueFrom:
        secretKeyRef:
          name: database-credentials
          key: password
    volumeMounts:
    # Mount secrets as files with restricted permissions
    - name: api-keys
      mountPath: /etc/secrets/api-keys
      readOnly: true
  volumes:
  - name: api-keys
    secret:
      secretName: api-keys
      defaultMode: 0400  # Read-only for owner only
      items:
      - key: api-key
        path: api.key
        mode: 0400
```

### 3.2 External Secret Management

#### HashiCorp Vault Integration
```yaml
# Vault authentication
apiVersion: v1
kind: ServiceAccount
metadata:
  name: vault-auth
  namespace: production

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: vault-auth-delegator
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: system:auth-delegator
subjects:
- kind: ServiceAccount
  name: vault-auth
  namespace: production

---
# External Secrets Operator configuration
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: vault-backend
  namespace: production
spec:
  provider:
    vault:
      server: "https://vault.company.com"
      path: "secret"
      version: "v2"
      auth:
        kubernetes:
          mountPath: "kubernetes"
          role: "production-app"
          serviceAccountRef:
            name: "vault-auth"

---
# External secret definition
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
  namespace: production
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: database-credentials
    creationPolicy: Owner
    template:
      type: Opaque
      metadata:
        labels:
          app: database
      data:
        username: "{{ .username }}"
        password: "{{ .password }}"
        connection-string: "postgresql://{{ .username }}:{{ .password }}@{{ .host }}:{{ .port }}/{{ .database }}"
  data:
  - secretKey: username
    remoteRef:
      key: database/production
      property: username
  - secretKey: password
    remoteRef:
      key: database/production
      property: password
  - secretKey: host
    remoteRef:
      key: database/production
      property: host
  - secretKey: port
    remoteRef:
      key: database/production
      property: port
  - secretKey: database
    remoteRef:
      key: database/production
      property: database
```

#### AWS Secrets Manager Integration
```yaml
# AWS Secrets Manager SecretStore
apiVersion: external-secrets.io/v1beta1
kind: SecretStore
metadata:
  name: aws-secrets-manager
  namespace: production
spec:
  provider:
    aws:
      service: SecretsManager
      region: us-west-2
      auth:
        serviceAccount:
          name: external-secrets-sa
        # Or use IRSA (IAM Roles for Service Accounts)
        # irsaRole: "arn:aws:iam::ACCOUNT:role/ExternalSecretsRole"

---
# IAM policy for external secrets
iam_policy:
  Version: "2012-10-17"
  Statement:
  - Effect: Allow
    Action:
    - secretsmanager:GetSecretValue
    - secretsmanager:DescribeSecret
    Resource:
    - "arn:aws:secretsmanager:us-west-2:ACCOUNT:secret:production/*"
  - Effect: Allow
    Action:
    - kms:Decrypt
    Resource:
    - "arn:aws:kms:us-west-2:ACCOUNT:key/KEY-ID"
    Condition:
      StringEquals:
        "kms:ViaService": "secretsmanager.us-west-2.amazonaws.com"
```

## 4. Compliance và Auditing

### 4.1 Security Benchmarks

#### CIS Kubernetes Benchmark
```yaml
cis_kubernetes_benchmark:
  control_plane_security:
    api_server:
      - "Ensure that the --anonymous-auth argument is set to false"
      - "Ensure that the --basic-auth-file argument is not set"
      - "Ensure that the --token-auth-file parameter is not set"
      - "Ensure that the --kubelet-https argument is set to true"
      - "Ensure that the --kubelet-client-certificate and --kubelet-client-key arguments are set"
      - "Ensure that the --kubelet-certificate-authority argument is set"
      - "Ensure that the --authorization-mode argument is not set to AlwaysAllow"
      - "Ensure that the --authorization-mode argument includes RBAC"
      - "Ensure that the admission control plugin EventRateLimit is set"
      - "Ensure that the admission control plugin AlwaysAdmit is not set"
      
    etcd:
      - "Ensure that the --cert-file and --key-file arguments are set"
      - "Ensure that the --client-cert-auth argument is set to true"
      - "Ensure that the --auto-tls argument is not set to true"
      - "Ensure that the --peer-cert-file and --peer-key-file arguments are set"
      - "Ensure that the --peer-client-cert-auth argument is set to true"
      - "Ensure that the --peer-auto-tls argument is not set to true"
      
  worker_node_security:
    kubelet:
      - "Ensure that the --anonymous-auth argument is set to false"
      - "Ensure that the --authorization-mode argument is not set to AlwaysAllow"
      - "Ensure that the --client-ca-file argument is set"
      - "Ensure that the --read-only-port argument is set to 0"
      - "Ensure that the --streaming-connection-idle-timeout argument is not set to 0"
      - "Ensure that the --protect-kernel-defaults argument is set to true"
      - "Ensure that the --make-iptables-util-chains argument is set to true"
      - "Ensure that the --hostname-override argument is not set"
      
  policies:
    pod_security_policies:
      - "Minimize the admission of privileged containers"
      - "Minimize the admission of containers wishing to share the host process ID namespace"
      - "Minimize the admission of containers wishing to share the host IPC namespace"
      - "Minimize the admission of containers wishing to share the host network namespace"
      - "Minimize the admission of containers with allowPrivilegeEscalation"
      - "Minimize the admission of root containers"
      - "Minimize the admission of containers with the NET_RAW capability"
      - "Minimize the admission of containers with added capabilities"
```

#### NSA/CISA Kubernetes Hardening Guide
```yaml
nsa_cisa_hardening:
  kubernetes_pod_security:
    - name: "Run containers as non-root users"
      implementation: |
        securityContext:
          runAsNonRoot: true
          runAsUser: 1000
          
    - name: "Use read-only root filesystems"
      implementation: |
        securityContext:
          readOnlyRootFilesystem: true
          
    - name: "Prevent privilege escalation"
      implementation: |
        securityContext:
          allowPrivilegeEscalation: false
          
    - name: "Use specific capability sets"
      implementation: |
        securityContext:
          capabilities:
            drop:
              - ALL
            add:
              - NET_BIND_SERVICE
              
  network_separation:
    - name: "Use CNI plugins that support network policies"
      options: ["Calico", "Cilium", "Weave Net"]
      
    - name: "Implement default deny network policies"
      implementation: |
        apiVersion: networking.k8s.io/v1
        kind: NetworkPolicy
        metadata:
          name: default-deny-all
        spec:
          podSelector: {}
          policyTypes:
          - Ingress
          - Egress
          
  authentication_authorization:
    - name: "Disable anonymous authentication"
      implementation: "--anonymous-auth=false"
      
    - name: "Use RBAC for authorization"
      implementation: "--authorization-mode=Node,RBAC"
      
    - name: "Implement Pod Security Standards"
      levels: ["Privileged", "Baseline", "Restricted"]
      
  logging_monitoring:
    - name: "Enable audit logging"
      implementation: |
        --audit-log-path=/var/log/audit.log
        --audit-log-maxage=30
        --audit-log-maxbackup=3
        --audit-log-maxsize=100
        --audit-policy-file=/etc/kubernetes/audit-policy.yaml
```

### 4.2 Audit Logging

#### Comprehensive Audit Policy
```yaml
# Kubernetes audit policy
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
# Log security-sensitive events at highest level
- level: Metadata
  namespaces: ["kube-system", "kube-public", "kube-node-lease"]
  verbs: ["get", "list", "watch"]
  resources:
  - group: ""
    resources: ["secrets", "configmaps"]
  - group: "rbac.authorization.k8s.io"
    resources: ["*"]

# Log all secret operations
- level: Request
  resources:
  - group: ""
    resources: ["secrets"]
  verbs: ["create", "update", "patch", "delete"]

# Log all RBAC changes
- level: Request
  resources:
  - group: "rbac.authorization.k8s.io"
    resources: ["*"]
  verbs: ["create", "update", "patch", "delete"]

# Log pod creation and deletion
- level: Request
  resources:
  - group: ""
    resources: ["pods"]
  verbs: ["create", "delete"]

# Log service account token creation
- level: Request
  resources:
  - group: ""
    resources: ["serviceaccounts/token"]

# Log exec and portforward
- level: Request
  resources:
  - group: ""
    resources: ["pods/exec", "pods/portforward", "pods/proxy", "services/proxy"]

# Log admission controller decisions
- level: Request
  users: ["system:serviceaccount:kube-system:*"]
  verbs: ["create", "update", "patch"]

# Log authentication failures
- level: Metadata
  omitStages:
  - RequestReceived
  - ResponseStarted
  resources:
  - group: "authentication.k8s.io"
    resources: ["*"]

# Don't log routine operations
- level: None
  users: ["system:kube-proxy"]
  verbs: ["watch"]
  resources:
  - group: ""
    resources: ["endpoints", "services"]

- level: None
  users: ["system:unsecured"]
  namespaces: ["kube-system"]
  verbs: ["get"]
  resources:
  - group: ""
    resources: ["configmaps"]

# Log everything else at minimal level
- level: Metadata
  omitStages:
  - RequestReceived
```

#### Audit Log Analysis
```bash
# Analyze audit logs for security events
# Failed authentication attempts
cat /var/log/audit.log | jq 'select(.verb=="create" and .objectRef.resource=="tokenreviews" and .responseStatus.code != 201)'

# Privileged pod creations
cat /var/log/audit.log | jq 'select(.verb=="create" and .objectRef.resource=="pods" and .requestObject.spec.securityContext.privileged==true)'

# Secret access events
cat /var/log/audit.log | jq 'select(.objectRef.resource=="secrets" and .verb=="get")'

# RBAC changes
cat /var/log/audit.log | jq 'select(.objectRef.apiGroup=="rbac.authorization.k8s.io" and (.verb=="create" or .verb=="update" or .verb=="delete"))'

# Exec into containers
cat /var/log/audit.log | jq 'select(.objectRef.subresource=="exec")'

# Suspicious user activities
cat /var/log/audit.log | jq 'select(.user.username != null and .user.username != "system:admin" and .verb=="delete" and .objectRef.resource=="pods")'
```

## 5. Runtime Security Monitoring

### 5.1 Falco Rules

#### Security Rules Configuration
```yaml
# Custom Falco rules for container security
- rule: Sensitive File Access
  desc: Detect access to sensitive files
  condition: >
    (open_read and fd.name in (sensitive_files))
    and not proc.name in (allowed_processes)
  output: >
    Sensitive file access (user=%user.name command=%proc.cmdline 
    file=%fd.name container=%container.name image=%container.image)
  priority: WARNING
  tags: [filesystem, mitre_credential_access]

- list: sensitive_files
  items: [
    /etc/passwd, /etc/shadow, /etc/sudoers,
    /root/.ssh/authorized_keys, /root/.ssh/id_rsa,
    /home/*/.ssh/authorized_keys, /home/*/.ssh/id_rsa,
    /etc/kubernetes/pki/*, /var/lib/kubelet/pki/*,
    /etc/docker/daemon.json
  ]

- list: allowed_processes
  items: [
    sshd, systemd, kubelet, dockerd
  ]

- rule: Container Privilege Escalation
  desc: Detect privilege escalation in containers
  condition: >
    spawned_process and container and
    ((proc.name in (privilege_escalation_binaries)) or
     (proc.args contains "chmod +s") or
     (proc.args contains "setuid") or
     (proc.args contains "setgid"))
  output: >
    Privilege escalation attempt (user=%user.name command=%proc.cmdline 
    container=%container.name image=%container.image)
  priority: HIGH
  tags: [privilege_escalation, mitre_privilege_escalation]

- list: privilege_escalation_binaries
  items: [
    su, sudo, passwd, chsh, newgrp, sg, gpasswd
  ]

- rule: Unexpected Network Connections
  desc: Detect unexpected outbound network connections
  condition: >
    outbound and container and
    not fd.sip in (allowed_outbound_ips) and
    not fd.sport in (common_ports)
  output: >
    Unexpected outbound connection (user=%user.name command=%proc.cmdline 
    connection=%fd.name container=%container.name image=%container.image)
  priority: NOTICE
  tags: [network, mitre_exfiltration]

- list: allowed_outbound_ips
  items: [
    "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"
  ]

- list: common_ports
  items: [
    80, 443, 53, 22, 8080, 8443, 9090, 9093
  ]

- rule: Container Filesystem Modification
  desc: Detect modification of container filesystem
  condition: >
    open_write and container and
    fd.name startswith "/bin/" or fd.name startswith "/usr/bin/" or
    fd.name startswith "/sbin/" or fd.name startswith "/usr/sbin/"
  output: >
    Container filesystem modification (user=%user.name command=%proc.cmdline 
    file=%fd.name container=%container.name image=%container.image)
  priority: WARNING
  tags: [filesystem, mitre_persistence]

- rule: Kubernetes Client Tool Usage
  desc: Detect usage of Kubernetes client tools in containers
  condition: >
    spawned_process and container and
    proc.name in (k8s_client_tools)
  output: >
    Kubernetes client tool usage (user=%user.name command=%proc.cmdline 
    tool=%proc.name container=%container.name image=%container.image)
  priority: NOTICE
  tags: [k8s, mitre_discovery]

- list: k8s_client_tools
  items: [
    kubectl, oc, helm, kustomize
  ]
```

### 5.2 Container Behavioral Analysis

#### Runtime Monitoring with Sysdig
```yaml
# Sysdig runtime policies
policies:
  container_security:
    - name: "Crypto Mining Detection"
      description: "Detect cryptocurrency mining activities"
      conditions:
        - process_name_regex: ".*(xmrig|ethminer|claymore|cgminer).*"
        - cpu_usage_percent: ">= 80"
        - network_connections: "> 10"
      actions:
        - kill_process: true
        - alert: critical
        
    - name: "Suspicious Network Activity"
      description: "Detect abnormal network patterns"
      conditions:
        - outbound_connections_count: "> 100"
        - connection_to_tor_exit_nodes: true
        - dns_requests_to_suspicious_domains: true
      actions:
        - isolate_container: true
        - alert: high
        
    - name: "File Integrity Monitoring"
      description: "Monitor critical file modifications"
      conditions:
        - file_modified:
          - "/bin/*"
          - "/usr/bin/*"
          - "/etc/passwd"
          - "/etc/shadow"
      actions:
        - create_snapshot: true
        - alert: medium
        
  kubernetes_security:
    - name: "Pod Escape Attempt"
      description: "Detect container escape attempts"
      conditions:
        - mount_host_filesystem: true
        - access_host_pid_namespace: true
        - privileged_container: true
      actions:
        - terminate_pod: true
        - alert: critical
        
    - name: "Unauthorized API Access"
      description: "Detect unauthorized Kubernetes API access"
      conditions:
        - kubectl_usage: true
        - service_account_token_access: true
        - rbac_permission_enumeration: true
      actions:
        - revoke_service_account: true
        - alert: high
```

#### Advanced Threat Detection
```yaml
threat_detection_rules:
  malware_detection:
    - name: "Reverse Shell Detection"
      pattern: |
        (proc.name in (shell_binaries) and 
         fd.type=ipv4 and fd.direction=outbound and 
         proc.args contains "-e" and proc.args contains "/bin/sh")
      severity: critical
      
    - name: "Fileless Malware"
      pattern: |
        (proc.name in (memory_execution_tools) or
         proc.args contains "exec" and proc.args contains "base64" or
         proc.cmdline contains "curl" and proc.cmdline contains "|" and proc.cmdline contains "sh")
      severity: high
      
  data_exfiltration:
    - name: "Large Data Transfer"
      pattern: |
        (fd.type=ipv4 and fd.direction=outbound and 
         fd.bytes_out > 100MB and
         not fd.sip in (trusted_networks))
      severity: medium
      
    - name: "Credential Harvesting"
      pattern: |
        (open_read and 
         (fd.name contains "passwd" or fd.name contains "shadow" or
          fd.name contains ".ssh" or fd.name contains "token" or
          fd.name contains "kubeconfig"))
      severity: high
      
  privilege_escalation:
    - name: "SUID Binary Execution"
      pattern: |
        (spawned_process and 
         proc.name in (suid_binaries) and
         user.uid != 0 and proc.euid = 0)
      severity: high
      
    - name: "Capability Abuse"
      pattern: |
        (spawned_process and
         proc.args contains "setcap" or
         proc.args contains "setuid" or
         proc.args contains "setgid")
      severity: medium

lists:
  shell_binaries: [bash, sh, zsh, fish, tcsh, csh]
  memory_execution_tools: [python, perl, ruby, node, java]
  trusted_networks: ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]
  suid_binaries: [su, sudo, passwd, chsh, newgrp]
```

Lý thuyết này cung cấp nền tảng toàn diện về container security, từ fundamentals đến advanced monitoring và threat detection, giúp engineers tại Viettel IDC triển khai và vận hành container infrastructure với mức độ bảo mật cao phù hợp với môi trường enterprise.
