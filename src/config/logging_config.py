import logging, socket
import watchtower


def setup_logging(log_group: str | None = None) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("app.log", encoding="utf-8"),
            watchtower.CloudWatchLogHandler(
                log_group=log_group or "/chatbot/rag-telegram",
                stream_name=f"{socket.gethostname()}-{logging.getLogger().name}",
            ),
        ],
    )
    logger = logging.getLogger("chatbot-g1")
    return logger
