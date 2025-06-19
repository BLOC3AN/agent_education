from langchain.memory import ConversationBufferMemory,ConversationSummaryBufferMemory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

class MemoryConversation:
    def __init__(self):
        pass
    
    def conversation_buffer_memory(self):
        memory = ConversationBufferMemory(
            memory_key="chat_history",     
            return_messages=True    #True for agent 
        )
        return memory
    def conversation_summary_buffer_memory(self, llm):
        summary_memory = ConversationSummaryBufferMemory(
                llm=llm,  # cần truyền LLM để nó có thể tóm tắt
                max_token_limit=1000,  # tối đa số token cho phần tóm tắt
                return_messages=True,
                memory_key="chat_history"
            )
        return summary_memory
