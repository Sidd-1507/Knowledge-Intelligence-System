from langchain_openai import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from src.utils.logger import get_logger

logger = get_logger(__name__)

class LLMService:
    def __init__(self, settings, vector_store_service):
        self.settings = settings
        self.vector_store_service = vector_store_service
        self.llm = ChatOpenAI(
            model_name=settings.openai_model,
            openai_api_key=settings.openai_api_key,
            temperature=0
        )
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            k=5,
            return_messages=True,
            output_key="answer"
        )
        self.chain = self._build_retrieval_chain()

    def _build_retrieval_chain(self):
        prompt_template = """Use the following pieces of context to answer the user's question.
If you don't have enough information to answer the question, just say "I don't have enough information", don't try to make up an answer.
Always cite your sources.

Context: {context}

Question: {question}

Helpful Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"]
        )
        
        retriever = self.vector_store_service.vector_store.as_retriever(search_kwargs={"k": 5})
        
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=retriever,
            memory=self.memory,
            return_source_documents=True,
            combine_docs_chain_kwargs={"prompt": PROMPT}
        )
        return chain

    def query(self, question: str, chat_history: list = None) -> dict:
        try:
            response = self.chain.invoke({"question": question})
            return {
                "answer": response["answer"],
                "source_documents": response.get("source_documents", []),
                "chat_history": self.memory.buffer
            }
        except Exception as e:
            logger.error(f"Query processing failed: {e}")
            raise

    def reset_memory(self):
        self.memory.clear()
        logger.info("Memory reset.")
