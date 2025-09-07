import os, io, tempfile, json, logging, boto3
from typing import List, Tuple
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import chromadb
from chromadb.utils import embedding_functions
from src.config.env_config import Configuration
from src.bedrock.models import titan_embed_texts
Configuration.load_env()

S3_BUCKET, S3_PREFIX, DATASET_DIR, CHROMA_DIR = Configuration.get("S3_BUCKET"), Configuration.get("S3_PREFIX"), Configuration.get("DATASET_DIR"), Configuration.get("CHROMA_DIR")

log = logging.getLogger("rag.indexer")

# Chroma EmbeddingFunction chamando Titan
class TitanEF(embedding_functions.EmbeddingFunction):
    def __call__(self, inputs: List[str]) -> List[List[float]]:
        return titan_embed_texts(inputs)

class Indexer:
    def get_collection():
        client = chromadb.PersistentClient(path=CHROMA_DIR)
        return client.get_or_create_collection(name="juridico", embedding_function=TitanEF())

    def _iter_local_pdfs() -> List[str]:
        paths = []
        for root, _, files in os.walk(DATASET_DIR):
            for f in files:
                if f.lower().endswith(".pdf"):
                    paths.append(os.path.join(root, f))
        return paths

    def _download_s3_pdfs() -> List[str]:
        if not S3_BUCKET:
            return []
        s3 = boto3.client("s3")
        tmpdir = tempfile.mkdtemp(prefix="dataset_")
        keys = []
        paginator = s3.get_paginator("list_objects_v2").paginate(Bucket=S3_BUCKET, Prefix=S3_PREFIX)
        for page in paginator:
            for it in page.get("Contents", []):
                key = it["Key"]
                if key.lower().endswith(".pdf"):
                    dest = os.path.join(tmpdir, os.path.basename(key))
                    s3.download_file(S3_BUCKET, key, dest)
                    keys.append(dest)
        return keys

    def _load_and_split(pdf_path: str) -> List[str]:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=120, separators=["\n\n", "\n", " ", ""])
        chunks = splitter.split_documents(docs)
        return [c.page_content for c in chunks]

    def build_index(cls) -> Tuple[int, int]:
        col = cls.get_collection()

        pdfs = []
        pdfs += cls._iter_local_pdfs()
        pdfs += cls._download_s3_pdfs()
        pdfs = list(dict.fromkeys(pdfs))  # de-dup

        added = 0
        for path in pdfs:
            chunks = cls._load_and_split(path)
            ids = [f"{os.path.basename(path)}::{i}" for i in range(len(chunks))]
            metas = [{"source": os.path.basename(path)} for _ in chunks]
            col.upsert(documents=chunks, metadatas=metas, ids=ids)
            added += len(ids)
            log.info("Indexed %s chunks from %s", len(ids), path)
        return len(pdfs), added
