from langchain_community.document_loaders import PyMuPDFLoader


from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker


from langchain_chroma import Chroma
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, models

from rag_pipeline.embedding import get_embedding, get_sparse_embedding
from utils.logger import get_logger
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from opik import track

logger = get_logger("Ingest")

os.environ["OMP_NUM_THREADS"] = "8"
os.environ["ORT_NUM_THREADS"] = "8"

client = QdrantClient(
    host= "localhost",
    port= 6334,
)

COLLECTION_NAME = "rag_pipeline"

dense_embedding = get_embedding()
sparse_embedding = get_sparse_embedding()

def init_qdrant_collection():
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "dense_vector": VectorParams(
                    size = 384,
                    distance = Distance.COSINE,
                    on_disk = True
                )
            },
            sparse_vectors_config={
                "sparse_vector": SparseVectorParams(

                )
            },
            quantization_config = models.QuantizationConfig(
                binary = models.BinaryQuantizationConfig(
                    always_ram = True,
                )
            )
        ) 
    
    logger.info(f"Collection {COLLECTION_NAME} initialized successfully")

def load_document(file_path):
        logger.info(f"Loading document: {file_path}")
        loader = PyMuPDFLoader(file_path)
        return loader.load()

def split_document(docs, strategy, chunk_size, chunk_overlap, progress_callback=None):

    logger.info(f"Splitting document with strategy: {strategy}")
    
    if strategy == "Recursive":
 
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        chunks = splitter.split_documents(docs)
    
    elif strategy == "Sentence":
 
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n"]
        )

        chunks = splitter.split_documents(docs)

 
    elif strategy == "Fixed":
        chunks = []
 
        for doc in docs:
            text = doc.page_content
 
            for i in range(0, len(text), chunk_size):
                chunk_text = text[i:i + chunk_size]
 
                chunks.append(type(doc)(
                    page_content=chunk_text,
                    metadata=doc.metadata
                ))

    elif strategy == "Token":
 
        splitter = CharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        chunks = splitter.split_documents(docs)
        logger.info(f"Token splitter created for chunk size: {chunk_size} and chunk overlap: {chunk_overlap}")
        

    elif strategy == "Semantic":
 
        embeddings = get_embedding()
 
        splitter = SemanticChunker(embeddings)

        chunks = splitter.split_documents(docs)

    else:
        raise ValueError(f"Unknown splitting strategy: {strategy}")
            
    return chunks

def create_vector_store(chunks, progress_callback=None):
    """Creates the vector store batch by batch sequentially to provide granular progress."""
    logger.info(f"Creating vector store from {len(chunks)} chunks...")


    db = QdrantVectorStore(
        client = client,
        collection_name = COLLECTION_NAME,
        embedding= dense_embedding,
        sparse_embedding= sparse_embedding,
        retrieval_mode= RetrievalMode.DENSE,
        vector_name= "dense_vector",
        sparse_vector_name= "sparse_vector",
    )

    batch_size = 64
    total_chunks = len(chunks)
    completed = 0

    batches = [chunks[i:i + batch_size] for i in range(0, total_chunks, batch_size)]
    total_batches = len(batches)

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(db.add_documents, batch): idx
            for idx, batch in enumerate(batches)
        }

        for future in as_completed(futures):
            future.result()  # raise if a batch failed
            batch_idx = futures[future]
            completed += len(batches[batch_idx])
            if progress_callback:
                # Scale from 40% up to 95% as batches complete
                percent = 40 + int((completed / total_chunks) * 55)
                progress_callback(percent, f"🔢 Generating embeddings ({completed}/{total_chunks} chunks)…")

    return db

@track
def ingest(file_paths, strategy, chunk_size, chunk_overlap, progress_callback=None):
    print("*" * 100)
    logger.info("Starting production ingestion pipeline...")
    current_metrics = {}
    
    # Initialize Qdrant collection
    init_qdrant_collection()
    
    if progress_callback:
        progress_callback(5, "📥 Initializing pipeline…", current_metrics)
    
    # 1. Loading Documents
    load_start = time.time()
    all_docs = []
    total_files = len(file_paths)
    completed_files = 0
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(load_document, fp): fp for fp in file_paths}
        for future in as_completed(futures):
            docs_list = future.result()
            all_docs.extend(docs_list)
            completed_files += 1
            if progress_callback:
                percent = 0 + int((completed_files / total_files) * 20)
                progress_callback(percent, f"📥 Loading documents ({completed_files}/{total_files} files)…", current_metrics)
            
    if not all_docs:
        raise Exception("No documents were successfully loaded.")
        
    load_end = time.time()
    current_metrics["loading"] = f"{load_end - load_start:.2f}s"
    logger.info(f" [1/3] Loading documents took: {load_end - load_start:.2f} seconds")
            
    if progress_callback:
        progress_callback(20, "✂️ Chunking text…", current_metrics)
        
    # 2. Chunking Text
    chunk_start = time.time()
    chunks = split_document(all_docs, strategy, chunk_size, chunk_overlap, progress_callback)
    chunk_end = time.time()
    current_metrics["chunking"] = f"{chunk_end - chunk_start:.2f}s"
    logger.info(f" [2/3] Chunking text took: {chunk_end - chunk_start:.2f} seconds")
    
    if progress_callback:
        progress_callback(40, " Preparing embedding vectors…", current_metrics)
    
    vector_start = time.time()
    create_vector_store(chunks, progress_callback)
    vector_end = time.time()
    current_metrics["embedding"] = f"{vector_end - vector_start:.2f}s"
    logger.info(f" [3/3] Generating embeddings & vector store took: {vector_end - vector_start:.2f} seconds")
    
    if progress_callback:
        current_metrics["total"] = f"{vector_end - load_start:.2f}s"
        progress_callback(100, "✅ Knowledge base ready!", current_metrics)
        
    print("-" * 50)
    logger.info(f"Total ingestion completed in {vector_end - load_start:.2f} seconds")
    print("*" * 100)

    return {
        "loading": f"{load_end - load_start:.2f}s",
        "chunking": f"{chunk_end - chunk_start:.2f}s",
        "embedding": f"{vector_end - vector_start:.2f}s",
        "total": f"{vector_end - load_start:.2f}s"
    }