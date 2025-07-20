# Lý Thuyết Nền Tảng về Container và Docker

## 1. Tổng Quan về Containerization

### 1.1 Khái Niệm Container
Container là một phương pháp ảo hóa ở cấp độ hệ điều hành cho phép đóng gói ứng dụng cùng với tất cả dependencies, thư viện và cấu hình cần thiết thành một đơn vị triển khai độc lập.

#### Định Nghĩa Chính Thức
Container là một process (hoặc nhóm processes) được cô lập từ phần còn lại của hệ thống bằng cách sử dụng kernel namespaces và cgroups, chia sẻ kernel với host OS nhưng có môi trường runtime riêng biệt.

#### Nguyên Lý Hoạt Động
```
┌─────────────────────────────────────────────────────────┐
│                    Host Operating System                │
├─────────────────────────────────────────────────────────┤
│                      Container Runtime                  │
├──────────────┬──────────────┬──────────────┬────────────┤
│  Container 1 │  Container 2 │  Container 3 │ Container N│
│ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │┌──────────┐│
│ │   App 1  │ │ │   App 2  │ │ │   App 3  │ ││  App N   ││
│ │ + Deps   │ │ │ + Deps   │ │ │ + Deps   │ ││ + Deps   ││
│ └──────────┘ │ └──────────┘ │ └──────────┘ │└──────────┘│
└──────────────┴──────────────┴──────────────┴────────────┘
```

### 1.2 So Sánh Container vs Virtual Machine

#### Virtual Machine Architecture
```
┌─────────────────────────────────────────────────────────┐
│                  Physical Hardware                      │
├─────────────────────────────────────────────────────────┤
│                    Host OS (Hypervisor)                │
├──────────────┬──────────────┬──────────────┬────────────┤
│   Guest OS   │   Guest OS   │   Guest OS   │  Guest OS  │
│ ┌──────────┐ │ ┌──────────┐ │ ┌──────────┐ │┌──────────┐│
│ │   App 1  │ │ │   App 2  │ │ │   App 3  │ ││  App N   ││
│ └──────────┘ │ └──────────┘ │ └──────────┘ │└──────────┘│
└──────────────┴──────────────┴──────────────┴────────────┘
```

#### Sự Khác Biệt Cốt Lõi

| Đặc Điểm | Container | Virtual Machine |
|----------|-----------|-----------------|
| **Kernel** | Chia sẻ với host | Kernel riêng cho mỗi VM |
| **Boot Time** | Milliseconds | Minutes |
| **Resource Usage** | Minimal overhead | Significant overhead |
| **Isolation Level** | Process-level | Hardware-level |
| **Portability** | Cao (image-based) | Thấp (platform-dependent) |
| **Security** | Shared kernel risks | Strong isolation |

### 1.3 Linux Kernel Technologies

#### Namespaces (Cô Lập Tài Nguyên)
Namespaces cung cấp cô lập cho các tài nguyên hệ thống:

```bash
# PID Namespace - Process isolation
unshare --pid --fork --mount-proc /bin/bash
ps aux  # Chỉ thấy processes trong namespace

# Network Namespace - Network isolation
ip netns add container1
ip netns exec container1 ip addr show

# Mount Namespace - Filesystem isolation
unshare --mount /bin/bash
mount -t tmpfs tmpfs /tmp  # Chỉ ảnh hưởng trong namespace

# UTS Namespace - Hostname isolation
unshare --uts /bin/bash
hostname container-host

# IPC Namespace - Inter-process communication isolation
unshare --ipc /bin/bash
ipcs  # Hiển thị IPC objects riêng biệt

# User Namespace - User/Group ID isolation
unshare --user --map-root-user /bin/bash
id  # Hiển thị root trong namespace
```

#### Control Groups (cgroups) - Quản Lý Tài Nguyên
Cgroups giới hạn và theo dõi việc sử dụng tài nguyên:

```bash
# Memory Control
echo "100M" > /sys/fs/cgroup/memory/docker/container_id/memory.limit_in_bytes
cat /sys/fs/cgroup/memory/docker/container_id/memory.usage_in_bytes

# CPU Control
echo "50000" > /sys/fs/cgroup/cpu/docker/container_id/cpu.cfs_quota_us
echo "100000" > /sys/fs/cgroup/cpu/docker/container_id/cpu.cfs_period_us
# Này giới hạn container sử dụng 50% của 1 CPU core

# I/O Control
echo "8:0 1048576" > /sys/fs/cgroup/blkio/docker/container_id/blkio.throttle.read_bps_device
# Giới hạn read bandwidth đến 1MB/s cho device 8:0
```

#### Union Filesystems
Cho phép kết hợp nhiều directories thành một view thống nhất:

```bash
# OverlayFS Example
mkdir lower upper work merged
echo "base file" > lower/file1.txt
mount -t overlay overlay -o lowerdir=lower,upperdir=upper,workdir=work merged
echo "modified" > merged/file1.txt
# file1.txt xuất hiện ở cả lower và upper, với upper có priority
```

### 1.4 Container Image Architecture

#### Image Layers và Layer Caching
Container images được xây dựng từ nhiều read-only layers:

```dockerfile
# Dockerfile example với layer optimization
FROM ubuntu:20.04                    # Layer 1: Base OS
RUN apt-get update                   # Layer 2: Package cache
RUN apt-get install -y python3      # Layer 3: Python installation
COPY requirements.txt .              # Layer 4: Requirements file
RUN pip3 install -r requirements.txt # Layer 5: Python dependencies
COPY src/ ./src/                     # Layer 6: Application code
CMD ["python3", "src/app.py"]       # Layer 7: Metadata layer
```

#### Content-Addressable Storage
Images được lưu trữ sử dụng content hashing:

```bash
# Image manifest structure
{
  "mediaType": "application/vnd.docker.distribution.manifest.v2+json",
  "schemaVersion": 2,
  "config": {
    "mediaType": "application/vnd.docker.container.image.v1+json",
    "size": 7023,
    "digest": "sha256:83c22b9c2a6b8e7f..."
  },
  "layers": [
    {
      "mediaType": "application/vnd.docker.image.rootfs.diff.tar.gzip",
      "size": 32654,
      "digest": "sha256:50644c29ef5a27c9..."
    }
  ]
}
```

## 2. Docker Architecture Deep Dive

### 2.1 Docker Engine Components

#### Docker Daemon (dockerd)
Service chạy trên background, quản lý Docker objects:

```bash
# Daemon configuration
cat /etc/docker/daemon.json
{
  "storage-driver": "overlay2",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "registry-mirrors": ["https://registry.docker-cn.com"],
  "insecure-registries": ["private-registry:5000"]
}

# Daemon monitoring
systemctl status docker
journalctl -u docker -f  # Real-time logs
docker system events     # Event stream
```

#### Docker CLI Client
Giao diện command-line giao tiếp với daemon qua REST API:

```bash
# Remote daemon connection
export DOCKER_HOST=tcp://remote-host:2376
export DOCKER_TLS_VERIFY=1
export DOCKER_CERT_PATH=/path/to/certs

# API direct access
curl --unix-socket /var/run/docker.sock http://localhost/containers/json
```

#### Container Runtime (containerd)
High-level runtime quản lý container lifecycle:

```bash
# containerd namespace management
ctr --namespace moby containers list
ctr --namespace k8s.io containers list

# Image operations via containerd
ctr images pull docker.io/library/nginx:latest
ctr run docker.io/library/nginx:latest nginx-test
```

### 2.2 Docker Network Architecture

#### Network Drivers Deep Dive

**Bridge Network (Default)**
```bash
# Bridge network internals
docker network inspect bridge
brctl show docker0           # Host bridge information
iptables -t nat -L DOCKER    # NAT rules for port forwarding

# Custom bridge network
docker network create --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.240.0/20 \
  custom-bridge
```

**Host Network**
Container chia sẻ network stack với host:
```bash
docker run --network host nginx
# Container sẽ bind directly lên host's ports
netstat -tulpn | grep :80  # Hiển thị nginx process
```

**Overlay Network (Multi-host)**
```bash
# Swarm overlay network
docker swarm init
docker network create --driver overlay --attachable multi-host-net

# VXLAN tunneling
ip link show flannel.1  # VXLAN interface
bridge fdb show dev flannel.1  # Forwarding database
```

**Macvlan Network**
```bash
# Macvlan configuration
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  --gateway=192.168.1.1 \
  -o parent=eth0 macvlan-net

# Container gets unique MAC address
docker run --network macvlan-net alpine ip addr show
```

#### Container Networking Model (CNM)

```
┌─────────────────────────────────────────┐
│              Application                │
├─────────────────────────────────────────┤
│              Container                  │
├─────────────────────────────────────────┤
│              Sandbox                    │  <- Network namespace
│  ┌─────────────┐ ┌─────────────────────┐│
│  │  Endpoint   │ │      Endpoint       ││  <- veth pairs
│  └─────────────┘ └─────────────────────┘│
├─────────────────────────────────────────┤
│              Network                    │  <- Bridge, overlay, etc.
└─────────────────────────────────────────┘
```

### 2.3 Storage Architecture

#### Storage Drivers Comparison

| Driver | Use Case | Performance | Features |
|--------|----------|-------------|----------|
| **overlay2** | Production (recommended) | Good | Copy-on-write, hardlinks |
| **aufs** | Legacy Ubuntu | Good | Multiple lower layers |
| **devicemapper** | RHEL/CentOS | Fair | LVM thin provisioning |
| **btrfs** | BTRFS filesystems | Good | Subvolumes, snapshots |
| **zfs** | ZFS filesystems | Excellent | Copy-on-write, compression |

#### Volume Management
```bash
# Volume types deep dive

# Named Volume
docker volume create --driver local \
  --opt type=tmpfs \
  --opt device=tmpfs \
  --opt o=size=100m \
  temp-volume

# Bind Mount with options
docker run -v /host/path:/container/path:ro,z nginx
# ro = read-only, z = SELinux relabeling

# tmpfs Mount
docker run --tmpfs /tmp:noexec,nosuid,size=1g nginx
```

#### Copy-on-Write Mechanics
```bash
# Monitoring layer changes
docker diff container_name  # Shows filesystem changes
docker history image_name   # Shows layer composition

# Layer storage location
ls -la /var/lib/docker/overlay2/  # Layer directories
cat /var/lib/docker/image/overlay2/layerdb/sha256/*/cache-id  # Layer mappings
```

## 3. Container Security Model

### 3.1 Security Boundaries

#### Kernel-level Security
```bash
# Capability management
docker run --cap-drop ALL --cap-add NET_ADMIN nginx
# Drops all capabilities except NET_ADMIN

# Viewing container capabilities
docker inspect container_name | grep -A 10 "CapAdd"
grep Cap /proc/PID/status  # Process capabilities

# User namespace remapping
echo "dockremap:231072:65536" >> /etc/subuid
echo "dockremap:231072:65536" >> /etc/subgid
# Maps container root to unprivileged user
```

#### AppArmor/SELinux Integration
```bash
# AppArmor profile
docker run --security-opt apparmor:docker-default nginx

# SELinux contexts
docker run --security-opt label=type:container_t nginx
ls -Z /var/lib/docker/  # SELinux contexts on Docker files
```

#### Seccomp Profiles
```json
{
  "defaultAction": "SCMP_ACT_ERRNO",
  "architectures": ["SCMP_ARCH_X86_64"],
  "syscalls": [
    {
      "names": ["read", "write", "open"],
      "action": "SCMP_ACT_ALLOW"
    }
  ]
}
```

### 3.2 Runtime Security

#### Resource Limits
```bash
# Memory limits with OOM handling
docker run --memory=256m --oom-kill-disable=false nginx

# CPU limits
docker run --cpus="1.5" --cpu-shares=512 nginx
# cpus: absolute limit, cpu-shares: relative weight

# Process limits
docker run --pids-limit=100 nginx
```

#### Image Security
```bash
# Image vulnerability scanning
docker scan nginx:latest
trivy image nginx:latest

# Content trust
export DOCKER_CONTENT_TRUST=1
docker pull nginx:latest  # Verifies signature

# Multi-stage builds for minimal attack surface
FROM alpine:latest AS builder
RUN apk add --no-cache build-tools
# ... build process ...

FROM alpine:latest AS runtime
RUN apk add --no-cache ca-certificates
COPY --from=builder /app/binary /usr/local/bin/
USER 1000:1000  # Non-root user
```

## 4. Performance và Optimization

### 4.1 Image Optimization

#### Layer Optimization Strategies
```dockerfile
# BAD: Multiple layers
RUN apt-get update
RUN apt-get install -y package1
RUN apt-get install -y package2
RUN rm -rf /var/lib/apt/lists/*

# GOOD: Single optimized layer
RUN apt-get update && \
    apt-get install -y package1 package2 && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean
```

#### Multi-stage Build Patterns
```dockerfile
# Builder stage
FROM golang:1.19-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o main .

# Runtime stage
FROM scratch
COPY --from=builder /app/main /
COPY --from=builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
EXPOSE 8080
CMD ["/main"]
```

### 4.2 Runtime Performance

#### Container Resource Monitoring
```bash
# Real-time monitoring
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"

# cgroup metrics
cat /sys/fs/cgroup/memory/docker/CONTAINER_ID/memory.stat
cat /sys/fs/cgroup/cpu/docker/CONTAINER_ID/cpuacct.stat

# Performance profiling
perf record -g docker run --rm alpine sleep 10
perf report  # Analyze performance data
```

#### Network Performance Tuning
```bash
# Network buffer tuning
docker run --sysctl net.core.rmem_max=134217728 \
           --sysctl net.core.wmem_max=134217728 \
           nginx

# SR-IOV for high-performance networking
docker network create -d macvlan \
  --subnet=192.168.1.0/24 \
  -o parent=eth0.100 sriov-net
```

## 5. Enterprise Patterns

### 5.1 Registry Management

#### Private Registry Architecture
```yaml
# registry-compose.yml
version: '3.8'
services:
  registry:
    image: registry:2
    environment:
      REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY: /var/lib/registry
      REGISTRY_AUTH: htpasswd
      REGISTRY_AUTH_HTPASSWD_PATH: /auth/htpasswd
      REGISTRY_AUTH_HTPASSWD_REALM: Registry Realm
    volumes:
      - registry-data:/var/lib/registry
      - ./auth:/auth:ro
      - ./certs:/certs:ro
    ports:
      - "5000:5000"

volumes:
  registry-data:
```

#### Image Promotion Pipeline
```bash
# Image promotion strategy
# Dev -> Staging -> Production
docker tag myapp:latest dev-registry/myapp:v1.0.0
docker push dev-registry/myapp:v1.0.0

# After testing
docker pull dev-registry/myapp:v1.0.0
docker tag dev-registry/myapp:v1.0.0 staging-registry/myapp:v1.0.0
docker push staging-registry/myapp:v1.0.0

# Production promotion
skopeo copy docker://staging-registry/myapp:v1.0.0 docker://prod-registry/myapp:v1.0.0
```

### 5.2 Monitoring và Logging

#### Structured Logging
```dockerfile
# Application logging configuration
ENV LOG_LEVEL=info
ENV LOG_FORMAT=json
ENV LOG_OUTPUT=stdout

# Log driver configuration
docker run --log-driver=fluentd \
           --log-opt fluentd-address=fluentd:24224 \
           --log-opt tag="docker.{{.Name}}" \
           myapp:latest
```

#### Metrics Collection
```bash
# Prometheus metrics endpoint
docker run -p 9323:9323 \
  --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
  prom/docker-metrics-exporter

# Custom metrics in application
# /metrics endpoint exposing:
# container_cpu_usage_seconds_total
# container_memory_usage_bytes
# container_network_receive_bytes_total
```

## 6. Troubleshooting Framework

### 6.1 Systematic Debugging

#### Container State Analysis
```bash
# Container inspection
docker inspect --format='{{.State.Running}}' container_name
docker inspect --format='{{.NetworkSettings.IPAddress}}' container_name
docker inspect --format='{{range .Mounts}}{{.Source}}:{{.Destination}}{{end}}' container_name

# Process analysis
docker exec container_name ps aux
docker exec container_name netstat -tulpn
docker exec container_name df -h
```

#### Resource Exhaustion Detection
```bash
# Memory analysis
docker exec container_name cat /proc/meminfo
docker exec container_name cat /proc/PID/smaps  # Memory mapping

# I/O analysis
docker exec container_name iostat -x 1
iotop -p $(docker inspect -f '{{.State.Pid}}' container_name)

# Network analysis
docker exec container_name ss -tuln
tcpdump -i docker0 host CONTAINER_IP
```

### 6.2 Common Issues và Solutions

#### Image Pull Failures
```bash
# Debugging image pulls
docker pull nginx:latest 2>&1 | tee pull.log

# Registry connectivity
curl -v https://registry-1.docker.io/v2/
curl -v https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/nginx:pull

# DNS resolution in containers
docker exec container_name nslookup registry-1.docker.io
docker exec container_name cat /etc/resolv.conf
```

#### Network Connectivity Issues
```bash
# Network troubleshooting
docker network ls
docker network inspect network_name

# Container connectivity
docker exec container1 ping container2
docker exec container1 telnet container2 80
docker exec container1 traceroute container2
```

#### Performance Bottlenecks
```bash
# Container performance profiling
docker exec container_name top
docker exec container_name iotop
docker exec container_name iftop

# System-level analysis
perf top -p $(docker inspect -f '{{.State.Pid}}' container_name)
strace -p $(docker inspect -f '{{.State.Pid}}' container_name)
```

## 7. Future Trends và Considerations

### 7.1 Security Enhancements
- **Rootless containers**: Chạy Docker daemon không cần root privileges
- **gVisor/Kata containers**: Additional isolation layers
- **Image signing**: Cosign và Sigstore integration
- **Runtime security**: Falco, Twistlock patterns

### 7.2 Performance Innovations
- **Lazy loading**: Stargz, eStargz formats
- **Image streaming**: Faster container startup
- **Hardware acceleration**: GPU, FPGA container support
- **Storage optimization**: Zstd compression, deduplication

### 7.3 Development Integration
- **DevContainers**: VS Code integration
- **Buildkit**: Advanced build features
- **BuildX**: Multi-platform builds
- **Docker Desktop alternatives**: Podman Desktop, Rancher Desktop

Lý thuyết này cung cấp nền tảng sâu sắc để hiểu container technology từ kernel level đến enterprise patterns, giúp engineers tại Viettel IDC có kiến thức vững chắc để triển khai và vận hành container infrastructure hiệu quả.
