# Module 7: Kỹ năng Mềm (Soft Skills)

## 🎯 Mục tiêu Module
Phát triển kỹ năng tư duy logic, phân tích vấn đề và viết tài liệu kỹ thuật - những kỹ năng thiết yếu cho vị trí System Administrator tại Viettel IDC.

## 📋 Nội dung Chính

### Tư duy Logic & Phân tích Vấn đề (40% trọng số)
#### 1. Root Cause Analysis (RCA)
- **Phương pháp 5 Whys**: tìm nguyên nhân gốc rễ
- **Fishbone Diagram**: phân tích đa chiều vấn đề
- **FMEA (Failure Mode and Effects Analysis)**: phòng ngừa sự cố
- **Timeline Analysis**: tái hiện chuỗi sự kiện

#### 2. Problem-Solving Framework
- **PDCA Cycle**: Plan-Do-Check-Act
- **8D Method**: 8 Disciplines problem solving
- **ITIL Problem Management**: quy trình chuẩn ITIL
- **Decision Trees**: ra quyết định có hệ thống

#### 3. Critical Thinking
- **Logic reasoning**: suy luận logic
- **Data analysis**: phân tích dữ liệu khách quan
- **Assumption validation**: kiểm chứng giả định
- **Risk assessment**: đánh giá rủi ro

### Viết Tài liệu Kỹ thuật (35% trọng số)
#### 1. Documentation Standards
- **Technical Writing**: nguyên tắc viết kỹ thuật
- **Document Structure**: cấu trúc tài liệu chuẩn
- **Version Control**: quản lý phiên bản tài liệu
- **Documentation Templates**: mẫu tài liệu chuẩn

#### 2. Operational Documentation
- **Runbooks**: hướng dẫn vận hành
- **SOPs**: quy trình chuẩn
- **Troubleshooting Guides**: hướng dẫn xử lý sự cố
- **Architecture Diagrams**: sơ đồ kiến trúc

#### 3. Incident Documentation
- **Incident Reports**: báo cáo sự cố
- **Post-mortem Analysis**: phân tích sau sự cố
- **Lessons Learned**: bài học kinh nghiệm
- **Knowledge Base**: cơ sở tri thức

### Giao tiếp & Làm việc Nhóm (25% trọng số)
#### 1. Technical Communication
- **Status Reporting**: báo cáo tình trạng
- **Escalation Procedures**: quy trình leo thang
- **Stakeholder Management**: quản lý stakeholder
- **Cross-team Collaboration**: hợp tác đa bộ phận

#### 2. Meeting & Presentation Skills
- **Technical Presentations**: thuyết trình kỹ thuật
- **Meeting Facilitation**: điều phối cuộc họp
- **Documentation Review**: review tài liệu
- **Knowledge Sharing**: chia sẻ kiến thức

## 🛠️ Kỹ năng Thực hành

### Root Cause Analysis Templates

#### 1. 5 Whys Analysis Template
```
INCIDENT: [Mô tả sự cố]
DATE: [Ngày xảy ra]
IMPACT: [Tác động]

WHY 1: Tại sao sự cố xảy ra?
→ [Câu trả lời]

WHY 2: Tại sao [câu trả lời Why 1]?
→ [Câu trả lời]

WHY 3: Tại sao [câu trả lời Why 2]?
→ [Câu trả lời]

WHY 4: Tại sao [câu trả lời Why 3]?
→ [Câu trả lời]

WHY 5: Tại sao [câu trả lời Why 4]?
→ [Nguyên nhân gốc rễ]

ROOT CAUSE: [Nguyên nhân chính xác]
CORRECTIVE ACTIONS: [Hành động khắc phục]
PREVENTIVE ACTIONS: [Hành động phòng ngừa]
```

#### 2. Incident Report Template
```markdown
# INCIDENT REPORT

## Thông tin Cơ bản
- **Incident ID**: INC-2024-001
- **Severity**: Critical/High/Medium/Low
- **Status**: Open/In Progress/Resolved/Closed
- **Reporter**: [Tên người báo cáo]
- **Assignee**: [Người xử lý]
- **Date Reported**: [Ngày báo cáo]
- **Date Resolved**: [Ngày giải quyết]

## Tóm tắt Sự cố
[Mô tả ngắn gọn về sự cố]

## Tác động
- **Services Affected**: [Dịch vụ bị ảnh hưởng]
- **Users Affected**: [Số lượng user bị ảnh hưởng]
- **Business Impact**: [Tác động kinh doanh]
- **Downtime**: [Thời gian ngừng hoạt động]

## Timeline
| Time | Action | Owner |
|------|--------|-------|
| 09:00 | Incident detected | Monitoring System |
| 09:05 | Alert sent to on-call engineer | Automated |
| 09:10 | Initial investigation started | John Doe |
| 09:30 | Root cause identified | John Doe |
| 10:00 | Fix implemented | Team Lead |
| 10:15 | Service restored | Team Lead |

## Root Cause Analysis
### Immediate Cause
[Nguyên nhân trực tiếp]

### Root Cause
[Nguyên nhân gốc rễ]

### Contributing Factors
- [Yếu tố góp phần 1]
- [Yếu tố góp phần 2]

## Resolution Steps
1. [Bước khắc phục 1]
2. [Bước khắc phục 2]
3. [Bước khắc phục 3]

## Lessons Learned
### What Went Well
- [Điều tốt 1]
- [Điều tốt 2]

### What Could Be Improved
- [Cải tiến 1]
- [Cải tiến 2]

## Action Items
| Action | Owner | Due Date | Status |
|--------|-------|----------|---------|
| Update monitoring thresholds | DevOps Team | 2024-01-15 | Open |
| Improve documentation | Tech Writer | 2024-01-20 | Open |
| Conduct training session | Team Lead | 2024-01-25 | Open |

## Prevention Measures
- [Biện pháp phòng ngừa 1]
- [Biện pháp phòng ngừa 2]
```

### Standard Operating Procedures (SOPs)

#### 1. Server Maintenance SOP
```markdown
# SOP: Server Maintenance Procedures

## Mục đích
Quy trình chuẩn cho việc bảo trì server định kỳ tại Viettel IDC.

## Phạm vi Áp dụng
- Tất cả production servers
- Development và staging servers (khi cần thiết)

## Trách nhiệm
- **System Administrator**: Thực hiện bảo trì
- **Team Lead**: Approve maintenance window
- **Network Operations**: Monitor during maintenance

## Quy trình

### Phase 1: Pre-Maintenance (T-24h)
1. **Notification**
   - Send maintenance notification to stakeholders
   - Update maintenance calendar
   - Coordinate with dependent teams

2. **Preparation**
   - Review maintenance checklist
   - Prepare rollback procedures
   - Verify backup systems

3. **Documentation**
   - Create maintenance ticket
   - Document current system state
   - Prepare change request

### Phase 2: Maintenance Window
1. **Pre-checks** (T-30min)
   ```bash
   # System health check
   systemctl status critical-services
   df -h  # Check disk space
   free -m  # Check memory
   uptime  # Check load average
   ```

2. **Backup** (T-15min)
   ```bash
   # Database backup
   pg_dump production_db > backup_$(date +%Y%m%d_%H%M).sql
   
   # Configuration backup
   tar -czf config_backup_$(date +%Y%m%d_%H%M).tar.gz /etc/
   ```

3. **Maintenance Tasks**
   - Apply OS patches
   - Update applications
   - Clean up old files
   - Optimize databases

4. **Post-maintenance Verification**
   ```bash
   # Service verification
   systemctl status all-services
   
   # Application verification
   curl -I http://localhost/health
   
   # Database verification
   psql -c "SELECT 1;" production_db
   ```

### Phase 3: Post-Maintenance
1. **Documentation**
   - Update maintenance log
   - Document any issues encountered
   - Update configuration documentation

2. **Monitoring**
   - Monitor system for 2 hours post-maintenance
   - Check application logs
   - Verify all alerts are cleared

3. **Communication**
   - Send completion notification
   - Update stakeholders on any issues
   - Schedule follow-up if needed

## Rollback Procedures
1. Stop affected services
2. Restore from backup
3. Restart services
4. Verify functionality
5. Document rollback actions

## Emergency Contacts
- **Team Lead**: +84-xxx-xxx-xxx
- **Network Operations**: +84-xxx-xxx-xxx
- **Database Team**: +84-xxx-xxx-xxx

## Approval Matrix
| Change Type | Approver |
|-------------|----------|
| Minor updates | System Admin |
| Major changes | Team Lead |
| Critical systems | Manager + Team Lead |
```

### Troubleshooting Guide Template

#### 1. Network Connectivity Issues
```markdown
# Troubleshooting: Network Connectivity Issues

## Symptoms
- Cannot reach remote servers
- Intermittent connection drops
- Slow network performance
- DNS resolution failures

## Quick Diagnosis
```bash
# Step 1: Check local network interface
ip addr show
ip route show

# Step 2: Test local connectivity
ping 127.0.0.1
ping gateway_ip

# Step 3: Test external connectivity
ping 8.8.8.8
nslookup google.com

# Step 4: Check network services
systemctl status NetworkManager
systemctl status network
```

## Common Solutions

### Problem: No IP Address
**Cause**: DHCP client not running or interface down
**Solution**:
```bash
# Restart network interface
sudo ifdown eth0 && sudo ifup eth0

# Or restart NetworkManager
sudo systemctl restart NetworkManager

# Manual IP configuration if needed
sudo ip addr add 192.168.1.100/24 dev eth0
sudo ip route add default via 192.168.1.1
```

### Problem: DNS Resolution Failure
**Cause**: DNS server misconfiguration
**Solution**:
```bash
# Check DNS configuration
cat /etc/resolv.conf

# Test DNS servers
nslookup google.com 8.8.8.8
dig @8.8.8.8 google.com

# Update DNS configuration
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

### Problem: Firewall Blocking
**Cause**: Firewall rules blocking traffic
**Solution**:
```bash
# Check firewall status
sudo iptables -L -n
sudo firewall-cmd --list-all

# Temporarily disable firewall for testing
sudo systemctl stop firewalld
# Remember to restart after testing

# Add specific rules if needed
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --reload
```

## Escalation
- **Level 1**: System Administrator (Basic troubleshooting)
- **Level 2**: Network Team (Advanced network issues)
- **Level 3**: ISP/Vendor (External connectivity issues)
```

## 📚 Resources & Templates

### Communication Templates

#### 1. Status Update Email
```
Subject: [SYSTEM ALERT] Database Performance Degradation - Investigation in Progress

Dear Team,

We are currently investigating performance issues with our primary database server that started at 14:30 today.

IMPACT:
- Application response times increased by 300%
- Some users may experience slow page loads
- No data loss or service outage

CURRENT STATUS:
- Issue detected at 14:30 via monitoring alerts
- Database team is investigating high CPU usage
- Preliminary analysis shows potential query optimization needed

NEXT STEPS:
- Continue investigation of root cause
- Implement temporary performance optimizations
- Provide update by 16:00 or sooner if resolved

For questions, please contact:
- John Doe (System Administrator): john.doe@viettel.com
- Emergency hotline: +84-xxx-xxx-xxx

Regards,
IT Operations Team
```

#### 2. Post-Incident Communication
```
Subject: [RESOLVED] Database Performance Issue - Post-Incident Summary

Dear Stakeholders,

The database performance issue reported earlier today has been resolved. Below is a summary of the incident:

INCIDENT SUMMARY:
- Start Time: 14:30
- End Time: 16:45
- Duration: 2 hours 15 minutes
- Severity: Medium

ROOT CAUSE:
- Inefficient database query consuming excessive CPU resources
- Query introduced in recent application deployment

RESOLUTION:
- Optimized problematic query
- Added missing database index
- Implemented query performance monitoring

PREVENTION MEASURES:
- Enhanced code review process for database queries
- Automated query performance testing in CI/CD pipeline
- Improved monitoring alerts for query performance

We apologize for any inconvenience caused and have implemented measures to prevent similar issues in the future.

Regards,
IT Operations Team
```

## 📊 Metrics & KPIs

### Documentation Quality Metrics
- **Completeness**: Percentage of procedures documented
- **Accuracy**: Error rate in documentation
- **Accessibility**: Time to find relevant information
- **Usefulness**: Feedback scores from users

### Problem-Solving Effectiveness
- **Mean Time to Resolution (MTTR)**: Average resolution time
- **First Call Resolution**: Percentage resolved without escalation
- **Root Cause Accuracy**: Percentage of correctly identified causes
- **Recurrence Rate**: Percentage of incidents that repeat

## 🎓 Chứng chỉ Liên quan
- **ITIL Foundation**: IT Service Management
- **PMP**: Project Management Professional
- **Technical Writing Certification**

## ⏱️ Thời gian Học: Xuyên suốt quá trình
- **Tuần 1-2**: Problem-solving frameworks
- **Tuần 3-4**: Documentation standards
- **Tuần 5-6**: Communication skills
- **Ongoing**: Practice và improvement

## 🏆 Kết thúc Lộ trình
Chúc mừng! Bạn đã hoàn thành tất cả 7 module học tập. Bây giờ hãy bắt đầu áp dụng kiến thức vào các dự án thực tế trong thư mục `projects/`.
