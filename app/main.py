import os
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from pathlib import Path

DB_USER = os.getenv("POSTGRES_USER", "appuser")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "apppass")
DB_NAME = os.getenv("POSTGRES_DB", "appdb")
DB_HOST = os.getenv("POSTGRES_HOST", "db")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

app = FastAPI(title="Docker Lab API with UI")
engine: Engine = create_engine(DATABASE_URL, pool_pre_ping=True)

STATIC_DIR = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
def _startup():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))

@app.get("/ping")
def ping() -> dict:
    return {"status": "ok"}

@app.get("/users")
def list_users() -> List[Dict]:
    with engine.connect() as conn:
        rows = conn.execute(text("SELECT id, name, created_at FROM users ORDER BY id")).mappings().all()
        return [dict(r) for r in rows]

@app.post("/users")
def add_user(name: str) -> dict:
    if not name.strip():
        raise HTTPException(status_code=400, detail="Name must be non-empty")
    with engine.connect() as conn:
        row = conn.execute(text("INSERT INTO users(name) VALUES (:n) RETURNING id"), {"n": name}).first()
        conn.commit()
        return {"id": row[0], "name": name}

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    with engine.connect() as conn:
        users = conn.execute(text("SELECT id, name, created_at FROM users ORDER BY id")).mappings().all()
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset='utf-8'>
        <title>Users</title>
        <link rel='stylesheet' href='/static/style.css'>
    </head>
    <body>
        <div class='container'>
            <h1>👤 User List</h1>
            <form method='post' action='/add'>
                <input type='text' name='name' placeholder='Enter name' required>
                <button type='submit'>Add</button>
            </form>
            <table>
                <tr><th>ID</th><th>Name</th><th>Created At</th></tr>
                {"".join(f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['created_at']}</td></tr>" for u in users)}
            </table>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(html)

@app.post("/add", response_class=RedirectResponse)
def add_user_form(name: str = Form(...)):
    if not name.strip():
        raise HTTPException(status_code=400, detail="Name must be non-empty")
    with engine.connect() as conn:
        conn.execute(text("INSERT INTO users(name) VALUES (:n)"), {"n": name})
        conn.commit()
    return RedirectResponse(url="/", status_code=303)
