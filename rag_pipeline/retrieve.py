from langchain_chroma import Chroma
from rag_pipeline.embedding import get_embedding 
from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
# from chromadb import Search, K, Knn, Rrf
from langchain_core.documents import Document

from langchain_qdrant import QdrantVectorStore, RetrievalMode
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, SparseVectorParams, models

from flashrank import Ranker, RerankRequest

from rag_pipeline.embedding import get_embedding, get_sparse_embedding

from utils.logger import get_logger
from opik import track
logger = get_logger("Retrieve")

ranker = Ranker(model_name="ms-marco-MiniLM-L-12-v2") 

@track
def retrieve(query):

    dense_vector = get_embedding().embed_query(query)
    sparse_vector = get_sparse_embedding().embed_query(query)

    client = QdrantClient(
        url="http://localhost:6334",
        prefer_grpc=True,
    )

    # db = QdrantVectorStore(
    #     client=client,
    #     collection_name="rag_pipeline",
    #     embedding=get_embedding(),
    #     vector_name="dense_vector",
    #     retrieval_mode=RetrievalMode.DENSE,
    # )

    # search_result = db.similarity_search(query, k=3)

    db = client.query_points(
        collection_name="rag_pipeline",
        prefetch= [
            models.Prefetch(query = dense_vector, using = "dense_vector", limit = 50),
            models.Prefetch(
                query = models.SparseVector(
                indices = sparse_vector.indices,
                values = sparse_vector.values
            ),
            using = "sparse_vector",
            limit = 50
            ),
        ],
        query = models.FusionQuery(fusion = models.Fusion.RRF),
        limit = 30,
        with_payload = False
    )

    hits = db.points

    top_ids = [hit.id for hit in hits]

    payload_docs = client.retrieve(
        collection_name="rag_pipeline",
        ids=top_ids,
        with_payload=True,
    )

    passages = [
        {
            "id": d.id,
            "text": d.payload["page_content"],
            "meta": d.payload
        }
        for d in payload_docs
    ]

    passages = passages[:30]

    rerank_result = RerankRequest(query=query, passages=passages)
    reranked_result =  ranker.rerank(rerank_result)

    final_passages = reranked_result[:5]

    docs = [
        Document(
            page_content=p["text"],
            metadata=p["meta"].get("metadata", {})
        )
        for p in final_passages
    ]   

    return docs