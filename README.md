# StockX

## Setup and run the app (Linux/MacOS)

```bash
cd stockx-main
python3 -m venv . && source bin/activate
pip install -r requirements.txt
flask --app src/stockx:create_app --debug run 
```
