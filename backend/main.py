from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="My App")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


# Startup probe — start.sh polls this before launching the frontend so
# Vite never serves traffic that races a still-warming uvicorn.
# Keep this lightweight (no DB / external calls) and at the root path,
# not under /api, so internal scripts and external monitors can both
# hit it without coupling to the API surface.
@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from FastAPI!"}
