import json
from typing import List
from src.bedrock.client import createBedrockRuntime
from src.config.env_config import Configuration

MODEL_EMBED, MODEL_CHAT = Configuration.get("MODEL_EMBED"), Configuration.get("MODEL_CHAT")
_rt = createBedrockRuntime()

def titan_embed_texts(texts: List[str]) -> List[List[float]]:
    vecs: List[List[float]] = []
    for t in texts:
        body = {"inputText": t}
        resp = _rt.invoke_model(
            modelId=MODEL_EMBED,
            accept="application/json",
            contentType="application/json",
            body=json.dumps(body),
        )
        payload = json.loads(resp["body"].read())
        vecs.append(payload["embedding"])
    return vecs

def chat_with_nova(
    user_text: str,
    system_text: str = "Você é um assistente jurídico objetivo. Cite trechos do contexto quando possível.",
    max_tokens: int = 800,
) -> str:
    resp = _rt.converse(
        modelId=MODEL_CHAT,
        messages=[{"role": "user", "content": [{"text": user_text}]}],
        system=[{"text": system_text}],
        inferenceConfig={
            "maxTokens": max_tokens,
            "temperature": 0.2,
            "topP": 0.9,
        },
    )
    parts = resp["output"]["message"]["content"]
    texts = [p["text"] for p in parts if "text" in p]
    return "\n".join(texts) if texts else ""