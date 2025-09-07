from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from telegram.constants import ChatAction
from src.rag.retriever import answer
import logging

from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
TOKEN = os.getenv("TELEGRAM_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )
    await update.message.reply_text("bot juridico ativo! Envie sua pergunta.")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_msg = update.message.text
    print(f"Mensagem recebida: {user_msg}")
    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id, action=ChatAction.TYPING
    )
    try:
        rag_result = answer(user_msg)
        resposta = rag_result["answer"]
        print(f"Resposta enviada: {resposta}")
        await update.message.reply_text(resposta)
    except Exception as e:
        logging.exception("Erro ao consultar RAG")
        await update.message.reply_text(
            "Desculpe, ocorreu um erro ao consultar os documentos jurídicos."
        )


def main() -> ApplicationBuilder:
    print("Initiating main()...")
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    return application


if __name__ == "__main__":
    print("Starting bot...")
    print(f"Using token: {TOKEN}")
    main()
