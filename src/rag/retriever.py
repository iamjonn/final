from typing import List, Dict
from src.rag.indexer import Indexer
from src.bedrock.models import chat_with_nova

def search(q: str, k: int = 4) -> List[Dict]:
    get_collection = Indexer.get_collection
    col = get_collection()
    res = col.query(query_texts=[q], n_results=k)
    docs = res["documents"][0]
    metas = res["metadatas"][0]
    out = []
    for d, m in zip(docs, metas):
        out.append({"text": d, "source": m.get("source")})
    return out

PROMPT = """Você é um(a) assistente jurídico(a).
Use APENAS o contexto abaixo para responder de forma objetiva.
Se não houver informação suficiente, diga que não encontrou no material.

Pergunta: {question}

Contexto:
{context}

Responda em português, cite as partes relevantes do contexto (resumo + fonte).
"""

def answer(q: str, k: int = 4) -> Dict:
    hits = search(q, k=k)
    context = "\n\n".join([f"[{i+1}] ({h['source']})\n{h['text']}" for i, h in enumerate(hits)])
    prompt = PROMPT.format(question=q, context=context)
    text = chat_with_nova(prompt)
    return {"answer": text, "context": hits}
