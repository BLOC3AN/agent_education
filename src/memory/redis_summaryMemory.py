from langchain_core.memory import BaseMemory
from langchain_core.messages import BaseMessage
from pydantic import PrivateAttr

from pydantic import Field
from typing import List, Dict, Any
import redis
import logging

logger = logging.getLogger(__name__)

class SummarizingRedisMemory(BaseMemory):
    llm: Any = Field(...)
    redis_url: str = Field(...)
    session_id: str = Field(...)
    max_token_limit: int = Field(default=1000, description="Maximum number of tokens for the summary")

    _redis_client: redis.Redis = PrivateAttr()
    _summary_key: str = PrivateAttr()
    _chat_history_key: str = PrivateAttr()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        self._summary_key = f"{self.session_id}:summary"
        self._chat_history_key = f"{self.session_id}:chat_history"

        if not self._redis_client.exists(self._summary_key):
            self._redis_client.set(self._summary_key, "Conversation summary will be generated here.")

    @property
    def memory_variables(self) -> List[str]:
        return ["chat_history", "conversation_summary"]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        summary = self._redis_client.get(self._summary_key)
        chat_history = self._redis_client.lrange(self._chat_history_key, 0, -1)
        return {
            "chat_history": chat_history,
            "conversation_summary": summary
        }

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        user_message = inputs.get("input", "")
        self._redis_client.rpush(self._chat_history_key, user_message)
        self.update_summary(outputs["output"])

    def update_summary(self, message):
        """Update the conversation summary with a new message."""
        try:
            current_summary = self._redis_client.get(self._summary_key)
            logger.info(f"Current summary: {current_summary[:100] if current_summary else 'None'}...") #type:ignore
            
            # Xử lý message có thể là chuỗi hoặc đối tượng Message
            message_content = ""
            message_type = "Unknown"
            
            if isinstance(message, str):
                message_content = message
                message_type = "Text"
            elif hasattr(message, 'content'):
                # Đối tượng Message từ langchain
                message_content = message.content
                message_type = getattr(message, 'type', type(message).__name__)
            elif isinstance(message, dict) and 'content' in message:
                # Dictionary với key 'content'
                message_content = message['content']
                message_type = message.get('type', 'Dict')
            else:
                # Chuyển đổi đối tượng thành chuỗi
                message_content = str(message)
                message_type = type(message).__name__
                
            logger.info(f"Processing message of type {message_type}")
            
            # Tạo prompt để cập nhật tóm tắt
            prompt = f"""Hãy cập nhật tóm tắt cuộc hội thoại dưới đây:

Tóm tắt hiện tại:
{current_summary}

Tin nhắn mới ({message_type}):
{message_content}

Tóm tắt mới (giữ ngắn gọn, dưới {self.max_token_limit} tokens):
"""
            
            # Gọi LLM để tạo tóm tắt mới
            logger.info("Generating new summary...")
            new_summary = self.llm.invoke(prompt).content
            logger.info(f"New summary generated: {new_summary[:100]}...")
            
            # Lưu tóm tắt mới vào Redis
            self._redis_client.set(self._summary_key, new_summary)
            logger.info("✅ Summary updated successfully")
            
            return new_summary
        except Exception as e:
            logger.error(f"❌ Error updating summary: {e}")
            logger.error(f"Message type: {type(message)}")
            if hasattr(message, '__dict__'):
                logger.error(f"Message attributes: {message.__dict__}")
            return current_summary #type:ignore

    def clear(self) -> None:
        self._redis_client.delete(self._chat_history_key)
        self._redis_client.set(self._summary_key, "Conversation summary will be generated here.")
