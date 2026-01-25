# jiggas_forinvestly

stack:
backend/ fastapi, postgresql, sqlalchemy, jwt auth, openai api
frontend/ html, js, css

setting:
download all files and open in VS code -> open pgAdmin 4 (PostgreSQL) -> connect postgresql (as extension) to VScode -> add .\backend\.env & upload there your openai api key -> download 'pip install -r requirements.txt' -> in 1st terminal, type 'cd .\backend', type 'uvicorn main:app --reload' && in 2nd terminal, type 'cd .\frontend', type 'python -m http.server 5500' -> go into 'http://localhost:5500'
