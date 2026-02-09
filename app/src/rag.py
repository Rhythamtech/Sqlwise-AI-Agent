import logging
import json
import uuid
from config import settings
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_cohere import CohereEmbeddings

class RAGPipeline:
    def __init__(self):
        self.embedder = CohereEmbeddings(model="embed-v3.0")
        self.qdrant_url = settings.QDRANT_URL

    def create_qna_index(self, qna: List[dict]):
        logging.info("Creating QnA index.")
        qna_docs = []
        for q in qna:
            doc = Document(
                page_content=f"Question: {q['Q']}\n Answer: {q['A']}",
                metadata={"id": str(uuid.uuid4()), "source": q['source']}
            )
            qna_docs.append(doc)
            
        try:
            queries = json.loads(response.choices[0].message.content)
            for query in queries["items"]:
                user_query = query["Q"]
                answer = query["A"]
                doc = Document(
                    page_content=f"Question: {user_query}\n Answer: {answer}",
                    metadata={"id": str(uuid.uuid4()), "source": chunk.metadata["source"]}
                )
                qna_docs.append(doc)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to decode JSON: {e}")
            logging.error(f"Invalid JSON string: {response.choices[0].message.content}")


        QdrantVectorStore.from_documents(
            documents=qna_docs,
            embedding=self.embedder,
            collection_name="Ecom QnA RAG",
            url=self.qdrant_url
        )
        logging.info("QnA vector store created successfully.")

    def query_qna_index(self, user_query):
        logging.info(f"Querying QnA index with: {user_query}")
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=self.embedder,
            collection_name="Ecom QnA RAG",
            url=self.qdrant_url
        )
        results = vector_store.similarity_search(query=user_query, k=3)
        return results


        