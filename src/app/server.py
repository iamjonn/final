from src.config.env_config import Configuration
import logging
env_status = Configuration.load_env()
from src.config.logging_config import setup_logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from src.rag.indexer import Indexer
from src.rag.retriever import search, answer
import requests
from contextlib import asynccontextmanager
from src.services.telegram.bot import main as telegram_app_builder

dict_env = Configuration._dict_env
telegram_app = telegram_app_builder()
setup_logging(dict_env.get("LOG_GROUP"))
logger = logging.getLogger("chatbot-g1")

@asynccontextmanager
async def lifespan(app: FastAPI):
    if env_status["warnings"]:
        for w in env_status["warnings"]:
            logger.warning(w)

    logger.info("Starting Telegram bot...")
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()
    logger.info("Telegram bot started.")
    yield

    logger.info("Stopping Telegram bot...")
    await telegram_app.updater.stop()
    await telegram_app.stop()
    await telegram_app.shutdown()
    logger.info("Telegram bot stopped.")

app = FastAPI(title="RAG Jurídico", lifespan=lifespan)


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/index")
def index():
    indexer = Indexer()
    build_index = indexer.build_index
    files, chunks = build_index()
    logger.info("INDEX_DONE files=%s chunks=%s", files, chunks)
    return {"ok": True, "files": files, "chunks": chunks}


@app.get("/search")
def search_route(q: str, k: int = 4):
    return {"ok": True, "hits": search(q, k)}


@app.get("/chat")
def chat_route(q: str, k: int = 4):
    res = answer(q, k)
    logger.info("CHAT q=%s", q)
    return {"ok": True, **res}


# -------- Telegram Webhook --------
def _verify_secret(request: Request, secret: str):
    hdr = request.headers.get("x-telegram-bot-api-secret-token", "")
    if not secret or hdr != secret:
        raise HTTPException(status_code=401, detail="invalid webhook secret")


@app.post("/webhook/telegram")
async def telegram_webhook(request: Request):
    _verify_secret(request, dict_env["WEBHOOK_SECRET"])
    update = await request.json()
    msg = update.get("message") or update.get("edited_message") or {}
    chat_id = msg.get("chat", {}).get("id")
    text = msg.get("text", "") if msg else ""
    if not chat_id or not text:
        return JSONResponse({"ok": True})

    res = answer(text, k=4)
    reply = res["answer"]

    url = f"https://api.telegram.org/bot{dict_env['TELEGRAM_TOKEN']}/sendMessage"
    payload = {"chat_id": chat_id, "text": reply}
    requests.post(url, json=payload, timeout=20)

    logger.info("TELEGRAM_CHAT chat_id=%s prompt_len=%s", chat_id, len(text))
    return {"ok": True}


@app.get("/")
async def root():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("src.app.server:app", host="0.0.0.0", port=8000, reload=False)
