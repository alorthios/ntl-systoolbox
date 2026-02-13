# NTL-SysToolbox

CLI application for system monitoring and analysis.

## Installation

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python -m src.main
```

## Features

- **Module 1**: Server Statistics (CPU, RAM, Disk, Uptime)
- **Module 2**: MySQL Database Queries
- **Module 3**: End of Life Information

## Project Structure

```
mspr_monitoring/
├── src/
│   ├── main.py              # Main menu and navigation
│   ├── module1_server_stats.py
│   ├── module2_mysql.py
│   ├── module3_eol.py
│   └── utils.py
├── config.py                # Configuration file
├── requirements.txt
└── README.md
```
