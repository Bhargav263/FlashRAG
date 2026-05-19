from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.upload import app as upload_router
from backend.query import app as query_router

app = FastAPI(title="QA_Bot")

# ── CORS — allow the React dev server (Vite) ────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Vite dev server
        "http://127.0.0.1:5173",
        "http://localhost:3000",   # fallback if CRA is used
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount existing routers ───────────────────────────────────────────
app.include_router(upload_router)
app.include_router(query_router)


@app.get("/")
def home():
    return {"message": "Sales bot running..."}