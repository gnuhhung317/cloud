#!/bin/bash
# setup.sh - Script thiết lập môi trường học tập

echo "🚀 Setting up Viettel IDC Learning Environment..."

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
python -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "📚 Installing Python packages..."
pip install -r requirements.txt

# Create local config directory
echo "📁 Creating configuration directories..."
mkdir -p config/
mkdir -p logs/
mkdir -p tmp/

# Set up git hooks (if in git repo)
if [ -d ".git" ]; then
    echo "🔧 Setting up git hooks..."
    cp scripts/pre-commit .git/hooks/
    chmod +x .git/hooks/pre-commit
fi

# Create initial progress file
echo "📊 Initializing progress tracking..."
python scripts/tracker.py status > /dev/null

# Setup complete
echo "✅ Setup complete!"
echo ""
echo "🎯 Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "2. Check progress: python scripts/tracker.py status"
echo "3. Start with Module 1: cd modules/01-operating-systems"
echo "4. Read the README: cat modules/01-operating-systems/README.md"
echo ""
echo "📚 Happy learning! Target: Viettel IDC position preparation"
