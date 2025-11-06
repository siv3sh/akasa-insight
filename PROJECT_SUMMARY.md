# Project Summary: Akasa Air Data Engineering Task

## Overview
This is a complete, production-ready data engineering solution that successfully implements all requirements specified in the task.

## ✅ Requirements Met

### 1. Dual Processing Approaches
- ✅ **SQL-based (MySQL + SQLAlchemy ORM)**: Complete implementation with optimized queries
- ✅ **In-memory (Pandas)**: Full DataFrame-based processing pipeline

### 2. Data Sources
- ✅ **CSV**: Customer data parsing with validation
- ✅ **XML**: Orders data parsing with comprehensive error handling

### 3. Data Cleaning & Quality
- ✅ Date normalization (handles 12+ date formats)
- ✅ Mobile number validation and cleaning
- ✅ Missing value handling
- ✅ Type conversion and validation
- ✅ Comprehensive error logging

### 4. KPIs Implemented
All 4 KPIs fully implemented in both SQL and Pandas:

1. **Repeat Customers** - Customers with > 1 order
2. **Monthly Order Trends** - Orders and revenue per month
3. **Regional Revenue** - Revenue breakdown by region
4. **Top Spenders (30 Days)** - Top 10 customers by recent spend

### 5. Database Design
- ✅ Proper SQLAlchemy models (Customer, Order)
- ✅ Indexes on frequently queried columns
- ✅ Connection pooling
- ✅ Transaction management
- ✅ No SQL injection vulnerabilities (ORM-based)

### 6. Security & Best Practices
- ✅ Environment variables for credentials (.env)
- ✅ No hardcoded passwords
- ✅ .gitignore for sensitive files
- ✅ Parameterized queries via ORM

### 7. Code Quality
- ✅ PEP 8 compliant
- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Modular, reusable functions
- ✅ Separation of concerns

### 8. Logging & Error Handling
- ✅ Centralized logging system
- ✅ Data quality issue tracking
- ✅ Graceful error handling
- ✅ Structured error messages

### 9. Documentation
- ✅ Detailed README.md
- ✅ Quick Start Guide
- ✅ API documentation in docstrings
- ✅ Example outputs
- ✅ Troubleshooting guide

### 10. Deliverables
- ✅ Working code (both SQL and Pandas)
- ✅ Requirements.txt
- ✅ .env.example
- ✅ Sample data files
- ✅ Complete documentation

## 📁 Project Structure

```
AkasaAir-DataEngineer-Task1/
├── README.md                    # Comprehensive documentation
├── QUICKSTART.md                # 5-minute setup guide
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Security & cleanup
├── data/
│   ├── customers.csv           # Sample customer data
│   └── orders.xml              # Sample orders data
├── outputs/                     # Generated KPI results
└── src/
    ├── main.py                 # Main entry point
    ├── config/
    │   └── config.py           # Configuration management
    ├── database/
    │   ├── db_setup.py         # SQLAlchemy models
    │   └── load_data.py        # CSV/XML data loading
    ├── processing/
    │   ├── sql_queries.py      # SQL-based KPIs
    │   └── pandas_processing.py # Pandas-based KPIs
    └── utils/
        ├── logger.py           # Logging system
        └── helpers.py          # Data cleaning utilities
```

## 🎯 Key Features

1. **Automated Pipeline**: Single command execution (`python -m src.main`)
2. **Dual Validation**: Compare SQL vs Pandas results
3. **Production Ready**: Error handling, logging, security
4. **Extensible**: Easy to add new KPIs or data sources
5. **Well-Documented**: Clear code with comprehensive docs

## 📊 Sample Data

- **20 Customers** across 4 regions (North, South, East, West)
- **28 Orders** spanning September-November 2024
- **5 SKUs** with varying prices
- Realistic order patterns with repeat customers

## 🚀 Running the Application

```bash
# 1. Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your MySQL credentials

# 3. Run
python -m src.main
```

## 📈 Output Files Generated

**SQL Approach (JSON)**:
- sql_repeat_customers.json
- sql_monthly_trends.json
- sql_regional_revenue.json
- sql_top_spenders.json

**Pandas Approach (CSV)**:
- pandas_repeat_customers.csv
- pandas_monthly_trends.csv
- pandas_regional_revenue.csv
- pandas_top_spenders.csv

## 🔍 Code Highlights

### Data Cleaning Example
```python
def normalize_date(date_value):
    """Handles 12+ date formats automatically"""
    # Tries multiple formats, returns datetime or None
    
def normalize_mobile_number(mobile):
    """Cleans and validates mobile numbers"""
    # Removes special chars, validates length
```

### SQL Query Example
```python
def get_repeat_customers(self):
    """SQL-based approach with JOIN and GROUP BY"""
    query = session.query(
        Customer, func.count(Order.order_id)
    ).join(Order).group_by(Customer).having(
        func.count(Order.order_id) > 1
    )
```

### Pandas Processing Example
```python
def get_repeat_customers(self):
    """Pandas-based approach with groupby and merge"""
    order_counts = df_orders.groupby('mobile_number').size()
    repeat_customers = df_customers.merge(order_counts)
```

## 🛡️ Security Features

- Environment variable management
- No SQL injection (ORM-based)
- Secure credential handling
- .gitignore for sensitive files

## 📚 Technologies Used

- **Python 3.8+**: Core language
- **MySQL**: Relational database
- **SQLAlchemy 2.0**: ORM and query builder
- **Pandas**: Data manipulation
- **PyMySQL**: MySQL connector
- **python-dotenv**: Environment management
- **lxml**: XML parsing
- **tabulate**: Result formatting

## ✨ Production Considerations

The code includes:
- Connection pooling for database efficiency
- Indexes on frequently queried columns
- Transaction management for data integrity
- Comprehensive error handling
- Structured logging for debugging
- Type safety with type hints
- Modular design for maintainability

## 🎓 Learning Outcomes

This project demonstrates:
1. ETL pipeline design
2. Multi-source data integration (CSV/XML)
3. Dual processing approaches (SQL vs Pandas)
4. Data quality management
5. Production-ready coding practices
6. Clean architecture principles

---

**Status**: ✅ Complete and ready for review
**Date**: November 2024
**Version**: 1.0.0
