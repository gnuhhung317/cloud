# 🚀 Quick Start Guide - Hướng dẫn Bắt đầu Nhanh

Chào mừng bạn đến với **Viettel IDC Learning Repository**! Đây là hướng dẫn để bắt đầu hành trình học tập theo nguyên tắc 20/80.

## ⚡ Bắt đầu Ngay (5 phút)

### Bước 1: Thiết lập Môi trường
```powershell
# Tạo Python virtual environment
python -m venv venv

# Kích hoạt environment (Windows)
venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### Bước 2: Kiểm tra Tiến độ
```powershell
# Kiểm tra trạng thái học tập
python scripts/tracker.py status
```

### Bước 3: Bắt đầu Module 1
```powershell
# Đọc hướng dẫn Module 1
Get-Content modules\01-operating-systems\README.md
```

## 🎯 Lộ trình 24 Tuần

| Tuần | Module | Nội dung Chính |
|------|--------|----------------|
| 1-3 | Module 1 | **Hệ Điều Hành** - Linux/Windows admin |
| 4-7 | Module 2 | **Ảo hóa & Cloud** - VMware, AWS, Azure |
| 8-11 | Module 3 | **Container** - Docker, Kubernetes, CI/CD |
| 12-14 | Module 4 | **Database** - PostgreSQL, MongoDB, MySQL |
| 15-17 | Module 5 | **Automation** - Ansible, Terraform |
| 18-20 | Module 6 | **Programming** - Python, Java |
| 21-24 | Integration | **Projects** + **Soft Skills** |

## 📊 Theo dõi Tiến độ

### Cập nhật Tiến độ Module
```powershell
# Ví dụ: Module 1 đã hoàn thành 50%, học 5 giờ
python scripts/tracker.py update 01-operating-systems 50 5
```

### Đánh dấu Lab Hoàn thành
```powershell
# Hoàn thành lab1 của Module 1
python scripts/tracker.py lab 01-operating-systems lab1-system-setup
```

### Thêm Ghi chú Học tập
```powershell
# Thêm ghi chú về kiến thức học được
python scripts/tracker.py note 01-operating-systems "Đã nắm vững systemd service management"
```

## 🛠️ VS Code Tasks (Recommended)

Sử dụng VS Code Command Palette (`Ctrl+Shift+P`):

1. **Tasks: Run Task** → **Check Learning Progress**
2. **Tasks: Run Task** → **Update Module Progress**  
3. **Tasks: Run Task** → **Generate Weekly Report**

## 📚 Tài nguyên Học tập

### Online Labs (Free)
- **Katacoda**: https://katacoda.com
- **Play with Docker**: https://labs.play-with-docker.com
- **Play with Kubernetes**: https://labs.play-with-k8s.com

### Documentation & Guides
- **Red Hat Documentation**: https://access.redhat.com/documentation
- **Kubernetes Docs**: https://kubernetes.io/docs
- **AWS Documentation**: https://docs.aws.amazon.com

### Community Support
- **Reddit r/sysadmin**: https://reddit.com/r/sysadmin
- **Stack Overflow**: Tag `linux`, `kubernetes`, `aws`
- **Discord DevOps Community**: Search "DevOps Discord"

## 🎓 Chứng chỉ Đầu tiên (Khuyến nghị)

**Target trong 3 tháng đầu:**
1. **RHCSA** (Red Hat Certified System Administrator)
2. **AWS Cloud Practitioner** (Entry level)

## 📈 Metrics Thành công

### Tuần 4 Check-in:
- [ ] Module 1 hoàn thành 80%+
- [ ] Có thể setup Linux server từ đầu
- [ ] Hiểu được systemd và networking cơ bản

### Tuần 8 Check-in:
- [ ] Module 2 hoàn thành 80%+  
- [ ] Deploy được VM trên VMware/AWS
- [ ] Hiểu được cloud concepts cơ bản

### Tuần 12 Check-in:
- [ ] Module 3 hoàn thành 80%+
- [ ] Deploy được app với Docker/Kubernetes
- [ ] Setup được CI/CD pipeline cơ bản

## 🚨 Troubleshooting

### Python Environment Issues
```powershell
# Nếu gặp lỗi Python
python --version  # Cần Python 3.8+
pip --version     # Kiểm tra pip

# Tái tạo environment
Remove-Item -Recurse -Force venv
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Tracking Script Issues
```powershell
# Nếu tracker.py lỗi
python scripts/tracker.py status

# Tạo lại progress file
Remove-Item learning_progress.json
python scripts/tracker.py status
```

## 🎯 Daily Study Routine

### Morning (30-45 phút)
- Review progress: `python scripts/tracker.py status`
- Read module documentation
- Plan today's lab exercises

### Evening (1-2 giờ)  
- Hands-on lab practice
- Update progress: `python scripts/tracker.py update ...`
- Add notes về những gì học được

### Weekend (3-4 giờ)
- Complete major labs
- Work on projects
- Review và consolidate knowledge

## 📞 Support & Community

- **Issues**: Tạo GitHub issue cho technical problems
- **Discussions**: Sử dụng GitHub Discussions cho questions
- **Email**: [your-email] cho urgent matters

## 🏆 Next Steps

1. ✅ **Setup environment** (bạn đang làm bước này)
2. 📖 **Read Module 1** (`modules/01-operating-systems/README.md`)
3. 🧪 **Start first lab** (`labs/01-linux-fundamentals/`)
4. 📊 **Track progress** daily
5. 🚀 **Stay consistent** - 1-2 hours/day

---

**Remember**: *"20% kiến thức đúng sẽ mang lại 80% thành công tại Viettel IDC"*

Good luck! 🍀
