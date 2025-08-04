# HitQuiz2 backend

## Setup and run the backend (Linux/MacOS)

```bash
cd stockx-main
python3 -m venv . && source bin/activate
pip install -r requirements.txt
flask --app src/stockx:create_app --debug run 
```
