from langchain.memory import ConversationBufferMemory,ConversationSummaryBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class MemoryConversation:
    def __init__(self, **kwargs):
        self.memory_key = "chat_history"
        self.MAX_TOKEN_LIMIT = 500
        self.RETURN_MESSAGES = True
        
    
    def conversation_buffer_memory(self):
        memory = ConversationBufferMemory(
            memory_key=self.memory_key,     
            return_messages=self.RETURN_MESSAGES    #True for agent 
        )
        return memory
    def conversation_summary_buffer_memory(self, llm):
        summary_memory = ConversationSummaryBufferMemory(
                llm=llm, 
                max_token_limit=self.MAX_TOKEN_LIMIT,  
                return_messages=self.RETURN_MESSAGES,
                memory_key=self.memory_key,
            )
        return summary_memory
