from fastapi import FastAPI
from .routes import link, documents, bot_users


app = FastAPI(title="Crypto API", version="0.1.0")

app.include_router(link.router)
app.include_router(documents.router)
app.include_router(bot_users.router)

@app.get("/")
def health() -> dict:
    return {"status": "ok"}
