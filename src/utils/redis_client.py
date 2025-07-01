import redis
import os
from src.utils.logger import Logger
logger = Logger(__name__)

class RedisClient:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "redis")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_client = None
        self.connect()
        
    def connect(self):
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                decode_responses=True
            )
            ping = self.redis_client.ping()
            logger.info(f"✅ Connected to Redis: {ping}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            self.redis_client = None
    
    def set(self, key, value, expiry=None):
        """Set a key-value pair in Redis with optional expiry in seconds"""
        if not self.redis_client:
            return False
        try:
            return self.redis_client.set(key, value, ex=expiry)
        except Exception as e:
            logger.error(f"❌ Redis SET error: {e}")
            return False
    
    def get(self, key):
        """Get value for a key from Redis"""
        if not self.redis_client:
            return None
        try:
            return self.redis_client.get(key)
        except Exception as e:
            logger.error(f"❌ Redis GET error: {e}")
            return None

    def debug_redis(self):
        """Print debug information about Redis connection and keys"""
        if not self.redis_client:
            logger.error("❌ Redis client is not connected")
            return False
        
        try:
            # Kiểm tra kết nối
            ping = self.redis_client.ping()
            logger.info(f"✅ Redis connection: {ping}")
            
            # Liệt kê tất cả các key
            keys = self.redis_client.keys("*")
            logger.info(f"📋 Redis keys: {keys}")
            
            # Kiểm tra các key liên quan đến chat history
            chat_keys = self.redis_client.keys("chat:*")
            logger.info(f"💬 Chat history keys: {chat_keys}")
            
            # Hiển thị thông tin về bộ nhớ Redis
            info = self.redis_client.info("memory")
            logger.info(f"🧠 Redis memory: {info.keys()}")
            
            return True
        except Exception as e:
            logger.error(f"❌ Redis debug error: {e}")
            return False
