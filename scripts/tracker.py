#!/usr/bin/env python3
"""
Learning Progress Tracker
Script để theo dõi tiến độ học tập cho Viettel IDC preparation
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

class LearningTracker:
    def __init__(self, data_file="learning_progress.json"):
        self.data_file = data_file
        self.data = self.load_data()
    
    def load_data(self):
        """Load existing progress data or create new"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {
                "start_date": datetime.now().isoformat(),
                "modules": {
                    "01-operating-systems": {
                        "name": "Hệ Điều Hành",
                        "status": "not_started",
                        "progress": 0,
                        "labs_completed": [],
                        "time_spent": 0,
                        "notes": []
                    },
                    "02-virtualization-cloud": {
                        "name": "Ảo hóa & Cloud",
                        "status": "not_started",
                        "progress": 0,
                        "labs_completed": [],
                        "time_spent": 0,
                        "notes": []
                    },
                    "03-container-management": {
                        "name": "Container Management",
                        "status": "not_started",
                        "progress": 0,
                        "labs_completed": [],
                        "time_spent": 0,
                        "notes": []
                    },
                    "04-database-management": {
                        "name": "Database Management",
                        "status": "not_started",
                        "progress": 0,
                        "labs_completed": [],
                        "time_spent": 0,
                        "notes": []
                    },
                    "05-automation-tools": {
                        "name": "Automation Tools",
                        "status": "not_started",
                        "progress": 0,
                        "labs_completed": [],
                        "time_spent": 0,
                        "notes": []
                    },
                    "06-programming": {
                        "name": "Programming",
                        "status": "not_started",
                        "progress": 0,
                        "labs_completed": [],
                        "time_spent": 0,
                        "notes": []
                    },
                    "07-soft-skills": {
                        "name": "Soft Skills",
                        "status": "not_started",
                        "progress": 0,
                        "labs_completed": [],
                        "time_spent": 0,
                        "notes": []
                    }
                },
                "certifications": {
                    "planned": [],
                    "in_progress": [],
                    "completed": []
                },
                "projects": {
                    "planned": [],
                    "in_progress": [],
                    "completed": []
                }
            }
    
    def save_data(self):
        """Save progress data to file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def update_module_progress(self, module_id, progress, status=None, time_spent=0):
        """Update module progress"""
        if module_id in self.data["modules"]:
            self.data["modules"][module_id]["progress"] = progress
            self.data["modules"][module_id]["time_spent"] += time_spent
            if status:
                self.data["modules"][module_id]["status"] = status
            self.save_data()
            print(f"✅ Updated {self.data['modules'][module_id]['name']}: {progress}%")
        else:
            print(f"❌ Module {module_id} not found")
    
    def complete_lab(self, module_id, lab_name):
        """Mark lab as completed"""
        if module_id in self.data["modules"]:
            if lab_name not in self.data["modules"][module_id]["labs_completed"]:
                self.data["modules"][module_id]["labs_completed"].append(lab_name)
                self.save_data()
                print(f"✅ Completed lab: {lab_name}")
            else:
                print(f"ℹ️ Lab {lab_name} already completed")
        else:
            print(f"❌ Module {module_id} not found")
    
    def add_note(self, module_id, note):
        """Add study note to module"""
        if module_id in self.data["modules"]:
            note_entry = {
                "date": datetime.now().isoformat(),
                "content": note
            }
            self.data["modules"][module_id]["notes"].append(note_entry)
            self.save_data()
            print(f"📝 Added note to {self.data['modules'][module_id]['name']}")
        else:
            print(f"❌ Module {module_id} not found")
    
    def show_progress(self):
        """Display current learning progress"""
        print("🎯 VIETTEL IDC LEARNING PROGRESS")
        print("=" * 50)
        
        start_date = datetime.fromisoformat(self.data["start_date"])
        days_since_start = (datetime.now() - start_date).days
        
        print(f"📅 Started: {start_date.strftime('%Y-%m-%d')}")
        print(f"⏱️ Days learning: {days_since_start}")
        print()
        
        total_progress = 0
        completed_modules = 0
        
        for module_id, module_data in self.data["modules"].items():
            status_icon = {
                "not_started": "⚪",
                "in_progress": "🟡", 
                "completed": "🟢"
            }.get(module_data["status"], "⚪")
            
            progress = module_data["progress"]
            total_progress += progress
            
            if progress == 100:
                completed_modules += 1
            
            print(f"{status_icon} {module_data['name']}: {progress}% "
                  f"(Labs: {len(module_data['labs_completed'])}, "
                  f"Time: {module_data['time_spent']}h)")
        
        avg_progress = total_progress / len(self.data["modules"])
        print()
        print(f"📊 Overall Progress: {avg_progress:.1f}%")
        print(f"✅ Completed Modules: {completed_modules}/7")
        
        # Certification progress
        cert_data = self.data["certifications"]
        print(f"🎓 Certifications - Planned: {len(cert_data['planned'])}, "
              f"In Progress: {len(cert_data['in_progress'])}, "
              f"Completed: {len(cert_data['completed'])}")
        
        # Project progress  
        proj_data = self.data["projects"]
        print(f"🚀 Projects - Planned: {len(proj_data['planned'])}, "
              f"In Progress: {len(proj_data['in_progress'])}, "
              f"Completed: {len(proj_data['completed'])}")
    
    def show_next_steps(self):
        """Show recommended next steps"""
        print("\n🎯 RECOMMENDED NEXT STEPS")
        print("=" * 30)
        
        # Find current module
        current_module = None
        for module_id, module_data in self.data["modules"].items():
            if module_data["status"] == "in_progress":
                current_module = module_id
                break
        
        if not current_module:
            # Find first not started module
            for module_id, module_data in self.data["modules"].items():
                if module_data["status"] == "not_started":
                    current_module = module_id
                    break
        
        if current_module:
            module_name = self.data["modules"][current_module]["name"]
            print(f"📚 Continue with: {module_name}")
            print(f"📁 Path: modules/{current_module}/")
            
            # Check for README
            readme_path = f"modules/{current_module}/README.md"
            if os.path.exists(readme_path):
                print(f"📖 Start with: {readme_path}")
        else:
            print("🎉 All modules completed! Time for projects!")
    
    def add_certification(self, cert_name, status="planned"):
        """Add certification to tracking"""
        cert_data = self.data["certifications"]
        cert_entry = {
            "name": cert_name,
            "added_date": datetime.now().isoformat()
        }
        
        if status in cert_data:
            cert_data[status].append(cert_entry)
            self.save_data()
            print(f"🎓 Added certification: {cert_name} ({status})")
        else:
            print(f"❌ Invalid status: {status}")
    
    def generate_weekly_report(self):
        """Generate weekly learning report"""
        print("\n📊 WEEKLY REPORT")
        print("=" * 20)
        
        # Calculate this week's progress
        week_start = datetime.now() - timedelta(days=7)
        
        total_time_this_week = 0
        modules_worked_on = []
        
        for module_id, module_data in self.data["modules"].items():
            if module_data["status"] in ["in_progress", "completed"]:
                modules_worked_on.append(module_data["name"])
                # Note: This is simplified - in real implementation,
                # you'd track time spent per day
        
        print(f"⏰ Estimated time this week: {total_time_this_week}h")
        print(f"📚 Modules worked on: {len(modules_worked_on)}")
        
        if modules_worked_on:
            for module in modules_worked_on:
                print(f"  - {module}")

def main():
    """Main CLI interface"""
    tracker = LearningTracker()
    
    if len(sys.argv) < 2:
        print("🎯 Viettel IDC Learning Tracker")
        print("\nUsage:")
        print("  python tracker.py status          - Show current progress")
        print("  python tracker.py update <module> <progress> [hours] - Update progress")
        print("  python tracker.py lab <module> <lab_name> - Mark lab completed")
        print("  python tracker.py note <module> <note> - Add study note")
        print("  python tracker.py cert <name> [status] - Add certification")
        print("  python tracker.py report          - Generate weekly report")
        print("\nModules:")
        for module_id in tracker.data["modules"].keys():
            print(f"  - {module_id}")
        return
    
    command = sys.argv[1]
    
    if command == "status":
        tracker.show_progress()
        tracker.show_next_steps()
    
    elif command == "update" and len(sys.argv) >= 4:
        module_id = sys.argv[2]
        progress = int(sys.argv[3])
        hours = float(sys.argv[4]) if len(sys.argv) > 4 else 0
        
        status = None
        if progress == 0:
            status = "not_started"
        elif progress == 100:
            status = "completed"
        else:
            status = "in_progress"
        
        tracker.update_module_progress(module_id, progress, status, hours)
    
    elif command == "lab" and len(sys.argv) >= 4:
        module_id = sys.argv[2]
        lab_name = sys.argv[3]
        tracker.complete_lab(module_id, lab_name)
    
    elif command == "note" and len(sys.argv) >= 4:
        module_id = sys.argv[2]
        note = " ".join(sys.argv[3:])
        tracker.add_note(module_id, note)
    
    elif command == "cert" and len(sys.argv) >= 3:
        cert_name = sys.argv[2]
        status = sys.argv[3] if len(sys.argv) > 3 else "planned"
        tracker.add_certification(cert_name, status)
    
    elif command == "report":
        tracker.generate_weekly_report()
    
    else:
        print("❌ Invalid command or missing arguments")

if __name__ == "__main__":
    main()
