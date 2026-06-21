import uuid
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(name="local_ocr_documents")

embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def add_chunks(chunks, metadata):
    """
    Embed chunks and store them in ChromaDB with metadata.
    """
    ids = []
    embeddings = []
    metadatas = []

    for index, chunk in enumerate(chunks):
        ids.append(str(uuid.uuid4()))
        embeddings.append(embedding_model.encode(chunk).tolist())

        item = metadata.copy()
        item["chunk_index"] = index
        metadatas.append(item)

    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    return len(chunks)


def search_chunks(query, filters=None, top_k=5):
    """
    Manual metadata filters are applied first by ChromaDB's where clause.
    Then vector similarity is calculated only inside matching chunks.
    """
    query_embedding = embedding_model.encode(query).tolist()

    where_filter = {}
    if filters:
        for key, value in filters.items():
            if value:
                where_filter[key] = value

def search_chunks(query, filters=None, top_k=5):

    query_embedding = embedding_model.encode(query).tolist()

    # No filters
    if not filters or not any(filters.values()):
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

    conditions = []

    for key, value in filters.items():
        if value:
            conditions.append({
                key: {
                    "$eq": value
                }
            })

    where_clause = {
        "$and": conditions
    }

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where=where_clause
    )

    return results
