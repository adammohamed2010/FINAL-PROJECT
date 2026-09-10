from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

app = FastAPI()

frontend_path = Path(__file__).resolve().parent.parent / "frontend.html"


@app.get("/")
def root():
    return FileResponse(frontend_path)


@app.get("/api/message")
def message():
    return {"message": "Hello from the FastAPI backend!"}

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()
@app.get("/users")
def list_users(db = Depends(get_db)):
    return db.query(Users).all()