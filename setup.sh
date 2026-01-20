#!/bin/bash

# MFA Project Setup Script
# This script sets up the development environment

set -e  # Exit on error

echo "🚀 Setting up MFA Authentication Project..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}Project root: $PROJECT_ROOT${NC}"

# Check Python version
echo -e "\n${BLUE}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python version: $(python3 --version)"

# Create virtual environment in project root
echo -e "\n${BLUE}Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment already exists. Skipping...${NC}"
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo -e "\n${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate
echo "✓ Virtual environment activated"

# Upgrade pip
echo -e "\n${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo "✓ pip upgraded"

# Install all dependencies from root requirements.txt
echo -e "\n${BLUE}Installing project dependencies...${NC}"
pip install -r requirements.txt --quiet
echo "✓ All dependencies installed"

# Check for .env file
echo -e "\n${BLUE}Checking environment configuration...${NC}"
if [ ! -f "backend/.env" ]; then
    echo -e "${YELLOW}⚠ .env file not found. Creating from template...${NC}"
    if [ -f "backend/env.example.txt" ]; then
        cp backend/env.example.txt backend/.env
        echo "✓ Created backend/.env from template"
        echo -e "${YELLOW}⚠ Please edit backend/.env and configure your settings!${NC}"
    else
        echo "⚠ env.example.txt not found. Please create backend/.env manually."
    fi
else
    echo "✓ .env file exists"
fi

# Check MongoDB connection
echo -e "\n${BLUE}Checking MongoDB connection...${NC}"
if command -v mongosh &> /dev/null || command -v mongo &> /dev/null; then
    echo "✓ MongoDB client found"
    if mongosh --eval "db.runCommand({ping:1})" --quiet &> /dev/null || mongo --eval "db.runCommand({ping:1})" --quiet &> /dev/null; then
        echo "✓ MongoDB is running and accessible"
    else
        echo -e "${YELLOW}⚠ MongoDB client found but connection failed. Make sure MongoDB is running.${NC}"
    fi
else
    echo -e "${YELLOW}⚠ MongoDB client not found. Install MongoDB if you haven't already.${NC}"
fi

# Summary
echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Configure backend/.env with your settings"
echo ""
echo "3. Start the backend server:"
echo "   cd backend && python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "4. (Optional) Run the admin tool:"
echo "   cd admin && python admin_tool.py"
echo ""
echo -e "${GREEN}Happy coding! 🎉${NC}"

