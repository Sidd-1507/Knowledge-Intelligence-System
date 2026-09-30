from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class VectorStoreService:
    def __init__(self, settings):
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.collection_name = settings.chroma_collection_name
        self.persist_directory = settings.chroma_persist_dir
        self.vector_store = Chroma(
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
            persist_directory=self.persist_directory
        )

    def add_documents(self, documents: list) -> int:
        try:
            self.vector_store.add_documents(documents)
            logger.info(f"Added {len(documents)} document chunks to vector store.")
            return len(documents)
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")
            raise

    def search(self, query: str, k: int = 5) -> list:
        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def delete_document(self, source_filename: str) -> bool:
        try:
            collection = self.vector_store.get()
            ids_to_delete = []
            for i, metadata in zip(collection['ids'], collection['metadatas']):
                if metadata.get("source") == source_filename:
                    ids_to_delete.append(i)
            if ids_to_delete:
                self.vector_store.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} chunks for {source_filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document {source_filename}: {e}")
            raise

    def get_document_sources(self) -> list[str]:
        try:
            collection = self.vector_store.get()
            sources = set()
            for metadata in collection['metadatas']:
                if metadata and "source" in metadata:
                    sources.add(metadata["source"])
            return list(sources)
        except Exception as e:
            logger.error(f"Failed to get document sources: {e}")
            return []

    def get_collection_stats(self) -> dict:
        try:
            collection = self.vector_store.get()
            total_chunks = len(collection['ids'])
            sources = self.get_document_sources()
            return {
                "total_chunks": total_chunks,
                "sources_count": len(sources)
            }
        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"total_chunks": 0, "sources_count": 0}
