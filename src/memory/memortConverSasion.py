from langchain.memory import ConversationBufferMemory, ConversationSummaryBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.memory.redis_memory import RedisConversationMemory
from src.memory.redis_summaryMemory import SummarizingRedisMemory
from src.utils.logger import Logger
logger = Logger(__name__)

class MemoryConversation:
    def __init__(self, **kwargs):
        self.memory_key = "chat_history"
        self.MAX_TOKEN_LIMIT = 500
        self.RETURN_MESSAGES = True
        
    def conversation_buffer_memory(self):
        memory = ConversationBufferMemory(
            memory_key=self.memory_key,     
            return_messages=self.RETURN_MESSAGES,    #True for agent 
            output_key="output",
        )
        return memory
        
    def conversation_summary_buffer_memory(self, llm):
        summary_memory = ConversationSummaryBufferMemory(
                llm=llm, 
                max_token_limit=self.MAX_TOKEN_LIMIT,  
                return_messages=self.RETURN_MESSAGES,
                memory_key=self.memory_key,
                output_key="output",
            )
        return summary_memory
        
    def redis_conversation_memory(self, session_id="default"):
        """Create a Redis-backed conversation memory."""
        logger.info(f"Creating RedisConversationMemory for session_id: {session_id}")
        memory = RedisConversationMemory(session_id=session_id) 
        return memory
    
    def redis_conversation_summary_memory(self, llm, redis_url="redis://localhost:6379", session_id="default"):
        """Create a Redis-backed conversation memory."""
        logger.info(f"Creating RedisConversationMemory for session_id: {session_id}")
        memory = SummarizingRedisMemory(llm=llm, redis_url=redis_url, session_id=session_id) 
        return memory
