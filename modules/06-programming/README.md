# Module 6: Ngôn ngữ Lập trình (Python, Java)

## 🎯 Mục tiêu Module
Thành thạo Python và Java để hỗ trợ tự động hóa, maintain hệ thống, và phát triển các công cụ hỗ trợ vận hành tại Viettel IDC.

## 📋 Nội dung Chính

### Python (70% trọng số)
#### 1. Python Fundamentals
- **Syntax & Data Types**: strings, lists, dictionaries, sets
- **Control Flow**: conditions, loops, functions
- **Object-Oriented**: classes, inheritance, polymorphism
- **Error Handling**: try/except, custom exceptions

#### 2. System Administration với Python
- **File Operations**: os, pathlib, shutil modules
- **Process Management**: subprocess, threading, multiprocessing
- **Network Programming**: socket, requests, urllib
- **System Monitoring**: psutil, monitoring scripts

#### 3. Automation & Scripting
- **API Integration**: REST APIs, JSON handling
- **Database Connectivity**: SQLAlchemy, pymongo, psycopg2
- **Configuration Management**: ConfigParser, YAML, JSON
- **Logging**: logging module, structured logging

#### 4. Infrastructure Tools
- **Cloud SDKs**: boto3 (AWS), azure-sdk, google-cloud
- **Container APIs**: docker-py, kubernetes client
- **Monitoring**: Prometheus client, custom metrics
- **DevOps Tools**: GitLab API, Jenkins API integration

### Java (30% trọng số)
#### 1. Java Fundamentals
- **Core Concepts**: OOP, collections, exception handling
- **Concurrency**: threads, executors, synchronization
- **I/O Operations**: file handling, serialization
- **Networking**: sockets, HTTP clients

#### 2. Enterprise Java
- **Spring Framework**: dependency injection, web applications
- **Database Access**: JDBC, JPA/Hibernate
- **Build Tools**: Maven, Gradle basics
- **Testing**: JUnit, integration testing

#### 3. Application Maintenance
- **Debugging**: profiling tools, log analysis
- **Performance Tuning**: JVM tuning, memory management
- **Monitoring**: JMX, application metrics
- **Troubleshooting**: common issues, stack trace analysis

## 🛠️ Kỹ năng Thực hành

### Python Projects

#### 1. System Monitoring Script
```python
#!/usr/bin/env python3
"""
System Monitoring Script for Viettel IDC
Monitors CPU, memory, disk, and network usage
"""

import psutil
import json
import logging
import time
import smtplib
from datetime import datetime
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/system_monitor.log'),
        logging.StreamHandler()
    ]
)

class SystemMonitor:
    def __init__(self, config_file='monitor_config.json'):
        """Initialize monitor with configuration"""
        with open(config_file, 'r') as f:
            self.config = json.load(f)
        
        self.thresholds = self.config['thresholds']
        self.email_config = self.config['email']
        self.check_interval = self.config.get('check_interval', 60)
    
    def get_system_metrics(self):
        """Collect system metrics"""
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory': psutil.virtual_memory()._asdict(),
            'disk': {},
            'network': psutil.net_io_counters()._asdict(),
            'processes': len(psutil.pids())
        }
        
        # Disk usage for all mounted filesystems
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                metrics['disk'][partition.mountpoint] = {
                    'total': usage.total,
                    'used': usage.used,
                    'free': usage.free,
                    'percent': (usage.used / usage.total) * 100
                }
            except PermissionError:
                continue
        
        return metrics
    
    def check_thresholds(self, metrics):
        """Check if metrics exceed thresholds"""
        alerts = []
        
        # CPU check
        if metrics['cpu_percent'] > self.thresholds['cpu_percent']:
            alerts.append(f"CPU usage high: {metrics['cpu_percent']:.1f}%")
        
        # Memory check
        if metrics['memory']['percent'] > self.thresholds['memory_percent']:
            alerts.append(f"Memory usage high: {metrics['memory']['percent']:.1f}%")
        
        # Disk check
        for mount, disk_info in metrics['disk'].items():
            if disk_info['percent'] > self.thresholds['disk_percent']:
                alerts.append(f"Disk usage high on {mount}: {disk_info['percent']:.1f}%")
        
        return alerts
    
    def send_alert(self, alerts):
        """Send email alert"""
        if not alerts:
            return
        
        msg = MimeMultipart()
        msg['From'] = self.email_config['from']
        msg['To'] = ', '.join(self.email_config['to'])
        msg['Subject'] = f"System Alert - {psutil.os.uname().nodename}"
        
        body = "System Alert Summary:\\n\\n" + "\\n".join(alerts)
        msg.attach(MimeText(body, 'plain'))
        
        try:
            server = smtplib.SMTP(self.email_config['smtp_server'], 
                                self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], 
                        self.email_config['password'])
            server.send_message(msg)
            server.quit()
            logging.info("Alert email sent successfully")
        except Exception as e:
            logging.error(f"Failed to send alert email: {e}")
    
    def run(self):
        """Main monitoring loop"""
        logging.info("System monitor started")
        
        while True:
            try:
                metrics = self.get_system_metrics()
                alerts = self.check_thresholds(metrics)
                
                if alerts:
                    logging.warning(f"Alerts triggered: {alerts}")
                    self.send_alert(alerts)
                else:
                    logging.info("System metrics normal")
                
                # Log metrics to file
                with open('/var/log/system_metrics.json', 'a') as f:
                    json.dump(metrics, f)
                    f.write('\\n')
                
                time.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logging.info("Monitor stopped by user")
                break
            except Exception as e:
                logging.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying

if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()
```

#### 2. AWS Resource Management Tool
```python
#!/usr/bin/env python3
"""
AWS Resource Management Tool
Automate common AWS operations for Viettel IDC
"""

import boto3
import json
import argparse
import logging
from botocore.exceptions import ClientError
from datetime import datetime, timedelta

class AWSManager:
    def __init__(self, profile='default', region='us-west-2'):
        """Initialize AWS session"""
        self.session = boto3.Session(profile_name=profile)
        self.ec2 = self.session.client('ec2', region_name=region)
        self.s3 = self.session.client('s3')
        self.rds = self.session.client('rds', region_name=region)
        self.region = region
    
    def list_instances(self, state='running'):
        """List EC2 instances by state"""
        try:
            response = self.ec2.describe_instances(
                Filters=[{'Name': 'instance-state-name', 'Values': [state]}]
            )
            
            instances = []
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    instance_info = {
                        'InstanceId': instance['InstanceId'],
                        'InstanceType': instance['InstanceType'],
                        'State': instance['State']['Name'],
                        'LaunchTime': instance['LaunchTime'].isoformat(),
                        'PrivateIpAddress': instance.get('PrivateIpAddress', 'N/A'),
                        'PublicIpAddress': instance.get('PublicIpAddress', 'N/A'),
                        'Tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
                    }
                    instances.append(instance_info)
            
            return instances
        except ClientError as e:
            logging.error(f"Error listing instances: {e}")
            return []
    
    def create_backup_snapshot(self, instance_id, description=None):
        """Create EBS snapshots for instance volumes"""
        try:
            instance = self.ec2.describe_instances(InstanceIds=[instance_id])
            volumes = []
            
            for reservation in instance['Reservations']:
                for inst in reservation['Instances']:
                    for block_device in inst.get('BlockDeviceMappings', []):
                        if 'Ebs' in block_device:
                            volumes.append(block_device['Ebs']['VolumeId'])
            
            snapshots = []
            for volume_id in volumes:
                if description is None:
                    description = f"Backup of {volume_id} from {instance_id}"
                
                response = self.ec2.create_snapshot(
                    VolumeId=volume_id,
                    Description=description,
                    TagSpecifications=[{
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {'Key': 'Name', 'Value': f"backup-{volume_id}"},
                            {'Key': 'InstanceId', 'Value': instance_id},
                            {'Key': 'CreatedBy', 'Value': 'aws-manager-tool'}
                        ]
                    }]
                )
                snapshots.append(response['SnapshotId'])
                logging.info(f"Created snapshot {response['SnapshotId']} for volume {volume_id}")
            
            return snapshots
        except ClientError as e:
            logging.error(f"Error creating snapshots: {e}")
            return []
    
    def cleanup_old_snapshots(self, days=30):
        """Delete snapshots older than specified days"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            response = self.ec2.describe_snapshots(
                OwnerIds=['self'],
                Filters=[
                    {'Name': 'tag:CreatedBy', 'Values': ['aws-manager-tool']}
                ]
            )
            
            deleted_count = 0
            for snapshot in response['Snapshots']:
                if snapshot['StartTime'].replace(tzinfo=None) < cutoff_date:
                    try:
                        self.ec2.delete_snapshot(SnapshotId=snapshot['SnapshotId'])
                        logging.info(f"Deleted old snapshot: {snapshot['SnapshotId']}")
                        deleted_count += 1
                    except ClientError as e:
                        logging.warning(f"Could not delete snapshot {snapshot['SnapshotId']}: {e}")
            
            return deleted_count
        except ClientError as e:
            logging.error(f"Error cleaning up snapshots: {e}")
            return 0
    
    def get_cost_report(self, days=30):
        """Generate cost report for recent usage"""
        try:
            cost_explorer = self.session.client('ce')
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            response = cost_explorer.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.isoformat(),
                    'End': end_date.isoformat()
                },
                Granularity='DAILY',
                Metrics=['BlendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            return response['ResultsByTime']
        except ClientError as e:
            logging.error(f"Error getting cost report: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='AWS Resource Management Tool')
    parser.add_argument('--profile', default='default', help='AWS profile to use')
    parser.add_argument('--region', default='us-west-2', help='AWS region')
    parser.add_argument('action', choices=['list', 'backup', 'cleanup', 'cost'], 
                       help='Action to perform')
    parser.add_argument('--instance-id', help='Instance ID for backup action')
    parser.add_argument('--days', type=int, default=30, help='Days for cleanup/cost actions')
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    aws_manager = AWSManager(profile=args.profile, region=args.region)
    
    if args.action == 'list':
        instances = aws_manager.list_instances()
        print(json.dumps(instances, indent=2, default=str))
    
    elif args.action == 'backup':
        if not args.instance_id:
            print("Instance ID required for backup action")
            return
        snapshots = aws_manager.create_backup_snapshot(args.instance_id)
        print(f"Created snapshots: {snapshots}")
    
    elif args.action == 'cleanup':
        deleted = aws_manager.cleanup_old_snapshots(args.days)
        print(f"Deleted {deleted} old snapshots")
    
    elif args.action == 'cost':
        cost_data = aws_manager.get_cost_report(args.days)
        print(json.dumps(cost_data, indent=2, default=str))

if __name__ == "__main__":
    main()
```

### Java Projects

#### 1. Application Health Checker
```java
package com.viettelidc.monitoring;

import java.io.*;
import java.net.*;
import java.util.*;
import java.util.concurrent.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Application Health Checker for Viettel IDC
 * Monitors application endpoints and services
 */
public class HealthChecker {
    
    private static final ObjectMapper mapper = new ObjectMapper();
    private final List<HealthCheck> healthChecks;
    private final ExecutorService executor;
    private final int timeoutSeconds;
    
    public HealthChecker(List<HealthCheck> healthChecks, int timeoutSeconds) {
        this.healthChecks = healthChecks;
        this.timeoutSeconds = timeoutSeconds;
        this.executor = Executors.newFixedThreadPool(10);
    }
    
    public static class HealthCheck {
        private String name;
        private String url;
        private String type; // HTTP, TCP, PING
        private int expectedStatus;
        private String expectedContent;
        
        // Constructors, getters, setters
        public HealthCheck(String name, String url, String type) {
            this.name = name;
            this.url = url;
            this.type = type;
            this.expectedStatus = 200;
        }
        
        // Getters and setters
        public String getName() { return name; }
        public String getUrl() { return url; }
        public String getType() { return type; }
        public int getExpectedStatus() { return expectedStatus; }
        public String getExpectedContent() { return expectedContent; }
        
        public void setExpectedStatus(int status) { this.expectedStatus = status; }
        public void setExpectedContent(String content) { this.expectedContent = content; }
    }
    
    public static class HealthResult {
        private String name;
        private boolean healthy;
        private String message;
        private long responseTime;
        private LocalDateTime timestamp;
        
        public HealthResult(String name, boolean healthy, String message, long responseTime) {
            this.name = name;
            this.healthy = healthy;
            this.message = message;
            this.responseTime = responseTime;
            this.timestamp = LocalDateTime.now();
        }
        
        // Getters
        public String getName() { return name; }
        public boolean isHealthy() { return healthy; }
        public String getMessage() { return message; }
        public long getResponseTime() { return responseTime; }
        public LocalDateTime getTimestamp() { return timestamp; }
        
        @Override
        public String toString() {
            return String.format("[%s] %s: %s (%dms) - %s",
                timestamp.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME),
                name, healthy ? "HEALTHY" : "UNHEALTHY", responseTime, message);
        }
    }
    
    public CompletableFuture<HealthResult> checkHealth(HealthCheck check) {
        return CompletableFuture.supplyAsync(() -> {
            long startTime = System.currentTimeMillis();
            
            try {
                switch (check.getType().toUpperCase()) {
                    case "HTTP":
                        return checkHttpHealth(check, startTime);
                    case "TCP":
                        return checkTcpHealth(check, startTime);
                    case "PING":
                        return checkPingHealth(check, startTime);
                    default:
                        return new HealthResult(check.getName(), false, 
                                              "Unknown check type: " + check.getType(), 
                                              System.currentTimeMillis() - startTime);
                }
            } catch (Exception e) {
                return new HealthResult(check.getName(), false, 
                                      "Exception: " + e.getMessage(), 
                                      System.currentTimeMillis() - startTime);
            }
        }, executor);
    }
    
    private HealthResult checkHttpHealth(HealthCheck check, long startTime) {
        try {
            URL url = new URL(check.getUrl());
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(timeoutSeconds * 1000);
            connection.setReadTimeout(timeoutSeconds * 1000);
            connection.setRequestMethod("GET");
            connection.setRequestProperty("User-Agent", "ViettelIDC-HealthChecker/1.0");
            
            int responseCode = connection.getResponseCode();
            long responseTime = System.currentTimeMillis() - startTime;
            
            if (responseCode == check.getExpectedStatus()) {
                String content = "";
                if (check.getExpectedContent() != null) {
                    BufferedReader reader = new BufferedReader(
                        new InputStreamReader(connection.getInputStream()));
                    StringBuilder response = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        response.append(line);
                    }
                    content = response.toString();
                    reader.close();
                    
                    if (!content.contains(check.getExpectedContent())) {
                        return new HealthResult(check.getName(), false, 
                                              "Expected content not found", responseTime);
                    }
                }
                
                return new HealthResult(check.getName(), true, 
                                      "HTTP " + responseCode, responseTime);
            } else {
                return new HealthResult(check.getName(), false, 
                                      "HTTP " + responseCode + " (expected " + 
                                      check.getExpectedStatus() + ")", responseTime);
            }
            
        } catch (Exception e) {
            long responseTime = System.currentTimeMillis() - startTime;
            return new HealthResult(check.getName(), false, 
                                  "HTTP Error: " + e.getMessage(), responseTime);
        }
    }
    
    private HealthResult checkTcpHealth(HealthCheck check, long startTime) {
        try {
            URL url = new URL(check.getUrl());
            String host = url.getHost();
            int port = url.getPort();
            
            Socket socket = new Socket();
            socket.connect(new InetSocketAddress(host, port), timeoutSeconds * 1000);
            socket.close();
            
            long responseTime = System.currentTimeMillis() - startTime;
            return new HealthResult(check.getName(), true, 
                                  "TCP connection successful", responseTime);
            
        } catch (Exception e) {
            long responseTime = System.currentTimeMillis() - startTime;
            return new HealthResult(check.getName(), false, 
                                  "TCP Error: " + e.getMessage(), responseTime);
        }
    }
    
    private HealthResult checkPingHealth(HealthCheck check, long startTime) {
        try {
            URL url = new URL(check.getUrl());
            InetAddress address = InetAddress.getByName(url.getHost());
            boolean reachable = address.isReachable(timeoutSeconds * 1000);
            
            long responseTime = System.currentTimeMillis() - startTime;
            
            if (reachable) {
                return new HealthResult(check.getName(), true, 
                                      "Ping successful", responseTime);
            } else {
                return new HealthResult(check.getName(), false, 
                                      "Ping failed", responseTime);
            }
            
        } catch (Exception e) {
            long responseTime = System.currentTimeMillis() - startTime;
            return new HealthResult(check.getName(), false, 
                                  "Ping Error: " + e.getMessage(), responseTime);
        }
    }
    
    public List<HealthResult> checkAllHealth() {
        List<CompletableFuture<HealthResult>> futures = healthChecks.stream()
            .map(this::checkHealth)
            .collect(Collectors.toList());
        
        return futures.stream()
            .map(CompletableFuture::join)
            .collect(Collectors.toList());
    }
    
    public void shutdown() {
        executor.shutdown();
    }
    
    public static void main(String[] args) {
        // Example usage
        List<HealthCheck> checks = Arrays.asList(
            new HealthCheck("Web Server", "http://localhost:8080/health", "HTTP"),
            new HealthCheck("Database", "tcp://localhost:5432", "TCP"),
            new HealthCheck("External API", "https://api.example.com/status", "HTTP")
        );
        
        HealthChecker checker = new HealthChecker(checks, 5);
        
        // Run health checks
        List<HealthResult> results = checker.checkAllHealth();
        
        // Print results
        results.forEach(System.out::println);
        
        // Generate JSON report
        try {
            String json = mapper.writeValueAsString(results);
            System.out.println("\nJSON Report:");
            System.out.println(json);
        } catch (Exception e) {
            System.err.println("Error generating JSON report: " + e.getMessage());
        }
        
        checker.shutdown();
    }
}
```

## 📚 Tài liệu Tham khảo

### Python
- Python Official Documentation
- Automate the Boring Stuff with Python
- Effective Python by Brett Slatkin
- Python for DevOps by Noah Gift

### Java
- Oracle Java Documentation
- Effective Java by Joshua Bloch
- Java: The Complete Reference
- Spring Framework Documentation

## 🎓 Chứng chỉ Liên quan
- **Python**: PCEP, PCAP (Python Institute)
- **Java**: Oracle Certified Professional Java Programmer

## ⏱️ Thời gian Học: 2-3 tuần
- Tuần 1: Python fundamentals + system scripting
- Tuần 2: Python automation + cloud SDKs
- Tuần 3: Java applications + integration

## 🔗 Chuyển sang Module tiếp theo
Hoàn thành module này, bạn sẵn sàng cho **Module 7: Soft Skills** - module cuối cùng.
