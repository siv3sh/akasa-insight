# Quick Start Guide

Get up and running in 5 minutes.

## Step 1: Setup Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configure Database

```bash
# Start MySQL (if not running)
mysql.server start  # macOS
# OR
sudo service mysql start  # Linux

# Create database
mysql -u root -p
```

In MySQL console:
```sql
CREATE DATABASE akasa_air_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

## Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
nano .env  # or use your preferred editor
```

Update these values in `.env`:
```
DB_USER=root
DB_PASSWORD=your_mysql_password
```

## Step 4: Run the Application

```bash
python -m src.main
```

That's it! The application will:
- Create database tables
- Load data from CSV/XML
- Calculate all KPIs using both SQL and Pandas
- Save results to `outputs/` directory

## Verify Results

Check the output directory:
```bash
ls -la outputs/
```

You should see 8 files:
- 4 JSON files (SQL results)
- 4 CSV files (Pandas results)

## Troubleshooting

**MySQL Connection Error?**
```bash
# Check if MySQL is running
mysql.server status

# Verify credentials
mysql -u root -p
```

**Module Import Error?**
```bash
# Ensure you're in the project root directory
pwd
# Should show: /Users/siv3sh/Downloads/AkasaAir-DataEngineer-Task1

# Run with module syntax
python -m src.main
```

**Missing Dependencies?**
```bash
pip install -r requirements.txt --upgrade
```

## Need Help?

See the full [README.md](README.md) for detailed documentation.
