from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.embeddings import FastEmbedEmbeddings
from langchain_qdrant import FastEmbedSparse
from utils.logger import get_logger
from dotenv import load_dotenv
from opik import track

load_dotenv()

logger = get_logger("Embedding")

logger.info("Loading embedding model...")

@track
def get_embedding():
    logger.info("Initializing FastEmbeddings...")
    
    dense_vector = FastEmbedEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        encode_kwargs={'normalize_embeddings': True, 'batch_size': 64},
    )

    logger.info("Embedding model loaded successfully")
    
    return dense_vector

@track
def get_sparse_embedding():

    logger.info("Initializing SparseEmbeddings...")

    sparse_vector = FastEmbedSparse(
        model_name="Qdrant/bm25",
        encode_kwargs={'normalize_embeddings': True, 'batch_size': 64},
    )

    logger.info("Sparse Embedding model loaded successfully")

    return sparse_vector
