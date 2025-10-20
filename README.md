# Data Engineering with GitHub Copilot - Workshop

Welcome to the Data Engineering with GitHub Copilot workshop! This hands-on workshop teaches you how to leverage GitHub Copilot for data engineering tasks including SQL generation, data pipeline development, and debugging.

## Workshop Structure

This repository contains:
- **Module 1**: SQL generation and basic data operations
- **Modules 2-3**: Advanced data pipelines, debugging exercises, and PySpark demos
- **Pre-configured Azure PostgreSQL database** with sample sales data

## Prerequisites

Before the workshop, ensure you have the following installed and configured:

### 1. Visual Studio Code + GitHub Copilot
- Install [Visual Studio Code](https://code.visualstudio.com/)
- **GitHub Copilot License**: Ensure you have an active GitHub Copilot subscription (Individual, Business, or Enterprise) or access through an organization
- Install the [GitHub Copilot extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot) in VS Code
- Install the [GitHub Copilot Chat extension](https://marketplace.visualstudio.com/items?itemName=GitHub.copilot-chat) in VS Code
- Sign in to VS Code with your GitHub account that has Copilot access

### 2. Git & GitHub CLI
- Install [Git](https://git-scm.com/downloads)
- Install [GitHub CLI](https://cli.github.com/) (optional but recommended)

### 3. Python 3.11
- **Windows**: Download and install [Python 3.11](https://www.python.org/downloads/) (make sure to check "Add Python to PATH" during installation)
- **macOS**: Install via Homebrew: `brew install python@3.11`
- **Linux**: Install via package manager: `sudo apt-get install python3.11 python3.11-venv`

### 4. Python 3.11 Virtual Environment

**Windows:**
```bash
# Clone the repository
git clone <repository-url>
cd data-engineering-copilot-workshop

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**macOS/Linux:**
```bash
# Clone the repository
git clone <repository-url>
cd data-engineering-copilot-workshop

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. PySpark Setup

PySpark requires Java 8 or 11.

**Windows:**
1. Download and install [Java JDK 11](https://adoptium.net/)
2. Set `JAVA_HOME` environment variable:
   - Search for "Environment Variables" in Windows
   - Add `JAVA_HOME` pointing to your JDK installation (e.g., `C:\Program Files\Eclipse Adoptium\jdk-11.0.XX`)
   - Add `%JAVA_HOME%\bin` to your PATH

**macOS:**
```bash
# Install Java using Homebrew
brew install openjdk@11

# Add to PATH (add to ~/.zshrc or ~/.bash_profile)
export JAVA_HOME=$(/usr/libexec/java_home -v 11)
export PATH="$JAVA_HOME/bin:$PATH"
```

**Linux:**
```bash
# Install Java
sudo apt-get update
sudo apt-get install openjdk-11-jdk

# Set JAVA_HOME (add to ~/.bashrc)
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
```

### 6. Verify Installation

Run the following to verify your setup:

```bash
# Activate virtual environment first
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Verify Python
python --version  # Should show Python 3.11.x

# Verify Java
java -version  # Should show Java 11

# Test database connection
python quick_db_test.py
```

Expected output:
```
🔗 Connecting to database...
Database Test Results:
   customers  orders  total_revenue
0       1000    5000     12345678.90

[OK] Database connection successful!
```

## Database Connection

The workshop uses a pre-configured Azure PostgreSQL database. The connection string is already set in the code:
- **Host**: `copilot-workshop-db.postgres.database.azure.com`
- **Database**: `workshop_db`
- **Schema**: `raw` (for raw data), `analytics` (for views)

All exercises are ready to run - no additional database setup required!

## Getting Started

1. Open the repository in VS Code
2. Activate your virtual environment
3. Start with `Modules/Module_1/Exercises/01_sql_exercise_azure.py`
4. Follow along with the instructor

## Troubleshooting

**"Module not found" error:**
- Make sure your virtual environment is activated
- Run `pip install -r requirements.txt` again

**Java-related errors:**
- Verify `JAVA_HOME` is set correctly
- Restart your terminal/IDE after setting environment variables

**Database connection failed:**
- Check your internet connection
- Verify the connection using `python quick_db_test.py`

## Workshop Resources

- Database schema: `schema/database_schema.sql`
- Copilot instructions: `.github/copilot-instructions.md`
- Sample data: `setup/sample_data`

## Support

If you encounter issues during setup, please reach out to the workshop facilitators before the session begins.

Happy coding with Copilot! 🚀
