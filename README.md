# StockX

A demo of a simple web application in Flask for managing stock portfolios with price data updates via Yahoo Finance.

## Setup and run the app (Linux/MacOS)

```bash
cd stockx-main
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app src/stockx:create_app --debug run 
```
