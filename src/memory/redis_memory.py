
from typing import Dict, Any, List
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from src.utils.redis_client import RedisClient
from src.utils.logger import Logger

logger = Logger(__name__)

class RedisConversationMemory(ConversationBufferMemory):
    """Memory class that uses Redis to store conversation history."""
    
    def __init__(
        self,
        session_id: str = "default",
        memory_key: str = "chat_history",
        input_key: str = "input",
        output_key: str = "output",
        return_messages: bool = True,
        redis_ttl: int = 3600 * 24 * 7,
        redis_url: str = None #type:ignore
    ):
        # Khởi tạo Redis connection
        if not redis_url:
            redis_client = RedisClient()
            redis_url = f"redis://{redis_client.redis_host}:{redis_client.redis_port}"
        
        logger.info(f"Connecting to Redis at {redis_url} with session ID: {session_id}")
        
        # Tạo RedisChatMessageHistory
        chat_history = RedisChatMessageHistory(
            session_id=session_id,
            url=redis_url,
            ttl=redis_ttl
        )
        
        # Khởi tạo ConversationBufferMemory với chat_history từ Redis
        super().__init__(
            chat_memory=chat_history,
            memory_key=memory_key,
            input_key=input_key,
            output_key=output_key,
            return_messages=return_messages
        )
    
    @property
    def chat_messages(self) -> List[BaseMessage]:
        """Get messages from chat memory."""
        return self.chat_memory.messages
    
    def add_message(self, message: BaseMessage) -> None:
        """Add a message to the chat memory."""
        logger.info(f"Adding message to chat memory: {message}")
        self.chat_memory.add_message(message)
    
    def clear(self) -> None:
        """Clear memory contents."""
        try:
            self.chat_memory.clear()
            logger.info(f"Cleared chat memory")
        except Exception as e:
            logger.error(f"Error clearing chat memory from Redis: {e}")
    
    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """Save context from this conversation to buffer."""
        user_input = inputs.get(self.input_key) #type:ignore
        model_output = outputs.get(self.output_key) #type:ignore

        logger.info(f"Saving context to Redis. User input: {user_input[:50] if user_input else None}... Model output: {model_output[:50] if model_output else None}...")
        
        try:
            if user_input:
                self.chat_memory.add_message(HumanMessage(content=user_input))
                logger.info(f"✅ Added human message to Redis")
            if model_output:
                self.chat_memory.add_message(AIMessage(content=model_output))
                logger.info(f"✅ Added AI message to Redis")
        except Exception as e:
            logger.error(f"❌ Error saving context to Redis: {e}")

    def get_chat_history(self) -> List[Dict[str, Any]]:
        """Get formatted chat history from Redis."""
        messages = self.chat_memory.messages
        formatted_messages = []
        
        for msg in messages:
            formatted_messages.append({
                "type": msg.type,
                "content": msg.content,
                "timestamp": getattr(msg, "timestamp", None)
            })
        
        logger.info(f"Retrieved {len(formatted_messages)} messages from Redis")
        return formatted_messages

