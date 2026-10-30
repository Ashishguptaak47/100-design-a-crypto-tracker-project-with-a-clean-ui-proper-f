import os
import sys
import webbrowser
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from app.routes.api import router as api_router
from app.services.portfolio import portfolio_repo

app = FastAPI(title="ApexCrypto Tracker", version="1.0.0")
app.include_router(api_router)

@app.on_event("startup")
def startup_event():
    # Ensure database tables exist
    portfolio_repo.init_db()

@app.get("/", response_class=HTMLResponse)
def index():
    template_path = Path(__file__).parent / "templates" / "index.html"
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    # Automatically launch browser if not disabled
    if os.getenv("AUTO_OPEN", "true").lower() == "true" and "pytest" not in sys.modules:
        import threading
        threading.Timer(1.2, lambda: webbrowser.open(f"http://{host}:{port}")).start()
        
    uvicorn.run("main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
