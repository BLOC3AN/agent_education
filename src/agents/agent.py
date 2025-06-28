from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import AgentExecutor, create_tool_calling_agent
from src.llms.gemini import Gemini 
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.memory.memortConverSasion import MemoryConversation
from src.utils.redis_client import RedisClient

import time

from src.utils.logger import Logger
logger = Logger(__name__)

def get_prompt_conversation():
    """Create a conversation prompt template with memory placeholder."""
    from datetime import datetime
    current_time = datetime.now().strftime("%Y/%m/%d-%H:%M:%S")
    
    with open("src/prompts/conversation_agent.md", "r", encoding="utf-8") as f:
        system_prompt = f.read()
        
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"{system_prompt}+\nThời gian hiện tại: {current_time}"),
        MessagesPlaceholder(variable_name="chat_history"),  
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),  
    ],)
    return prompt

class AgentConversation:
    def __init__(self):
        self.MAX_ITERATIONS = 100
        self.EARLY_STOPPING_METHOD = "generate"
        self.MAX_EXECUTION_TIME = 200.5
        self.HANDLE_PARSING_ERRORS = True
        self.VERBOSE = True

        self.tools = []

        self.prompt = get_prompt_conversation()
        logger.info(f"📑 System prompt loaded")     

        self.llm_model = Gemini()
        self.model_name = self.llm_model.model_name
        logger.info(f"✅ LLM model {self.model_name} loaded.")

    def run(self, input:str, session_id:str="default"):
        start_time = time.time()
        logger.info(f"📝 Using session ID: {session_id}")
        logger.info(f"⏱️ Starting agent execution at: {start_time}")

        try:
            # Kiểm tra Redis trước khi tạo memory
            redis_client = RedisClient()
            redis_client.debug_redis()
            
            # Sử dụng Redis memory
            memory = MemoryConversation().redis_conversation_memory(session_id=session_id)
            logger.info(f"✅ RedisConversationMemory created successfully for session: {session_id}")
            agent = create_tool_calling_agent(self.llm_model.llm, self.tools, self.prompt)
            agent_executor = AgentExecutor(
                agent=agent,
                memory=memory,
                tools=self.tools,
                verbose=self.VERBOSE,
                max_iterations=self.MAX_ITERATIONS,
                early_stopping_method=self.EARLY_STOPPING_METHOD,
                max_execution_time=self.MAX_EXECUTION_TIME,
                handle_parsing_errors=self.HANDLE_PARSING_ERRORS,
                return_intermediate_steps=True,
            )
            logger.info("✅ Conversation Agent created successfully")
            
            before_invoke = time.time()
            logger.info(f"⏱️ Time to create agent: {before_invoke - start_time:.4f} seconds")

            result = agent_executor.invoke({ "input": f"{input}", "chat_history": memory, },return_intermediate_steps=True)
            
            end_time = time.time()
            logger.info(f"⏱️ Agent execution completed in: {end_time - start_time:.4f} seconds")
            logger.info(f"⏱️ LLM invocation time: {end_time - before_invoke:.4f} seconds")
            
            logger.info(f"📜 Response keys from Agent: {result.keys()}")

            # Kiểm tra và log intermediate_steps nếu có
            if 'intermediate_steps' in result and result['intermediate_steps']:
                logger.info(f"🔧 Tools used in this conversation: {len(result['intermediate_steps'])} steps")
            else:
                logger.info("🔧 No tools were used in this conversation")

            return result

        except Exception as e:
            logger.error(f"❌ Error in create Conversation Agent execution: {str(e)}")
            logger.warning(f"input:{input}")
            return {"Error as conversation_agent": str(e)}

    def stream(self, input: str, session_id: str = "default"):
        """
        Stream response từ agent theo thời gian thực
        Yields từng chunk của response
        """
        start_time = time.time()
        logger.info(f"📝 Using session ID: {session_id}")
        logger.info(f"⏱️ Starting agent streaming at: {start_time}")

        try:
            # Sử dụng Redis memory thay vì buffer memory
            memory = MemoryConversation().redis_conversation_memory(session_id=session_id)
            logger.info(f"✅ RedisConversationMemory created for streaming with session: {session_id}")

            agent = create_tool_calling_agent(self.llm_model.llm, self.tools, self.prompt)
            agent_executor = AgentExecutor(
                agent=agent,
                memory=memory,
                tools=self.tools,
                verbose=self.VERBOSE,
                max_iterations=self.MAX_ITERATIONS,
                max_execution_time=self.MAX_EXECUTION_TIME,
                handle_parsing_errors=self.HANDLE_PARSING_ERRORS,
                return_intermediate_steps=True,
            )
            logger.info("✅ Conversation Agent created successfully for streaming")

            before_stream = time.time()
            logger.info(f"⏱️ Time to create agent: {before_stream - start_time:.4f} seconds")

            # Sử dụng stream thay vì invoke
            full_response = ""
            for chunk in agent_executor.stream({"input": f"{input}", "chat_history": memory},return_intermediate_steps=True):
                if "output" in chunk:
                    # Yield từng phần của output
                    chunk_text = chunk["output"]
                    full_response += chunk_text
                    yield {
                        "type": "output",
                        "content": chunk_text,
                        "full_response": full_response
                    }
                elif "intermediate_steps" in chunk:
                    # Yield thông tin về intermediate steps nếu có
                    yield {
                        "type": "intermediate_step",
                        "content": chunk["intermediate_steps"],
                        "full_response": full_response
                    }
                elif "actions" in chunk:
                    # Yield thông tin về actions
                    yield {
                        "type": "action",
                        "content": str(chunk["actions"]),
                        "full_response": full_response
                    }

            end_time = time.time()
            logger.info(f"⏱️ Agent streaming completed in: {end_time - start_time:.4f} seconds")
            logger.info(f"⏱️ LLM streaming time: {end_time - before_stream:.4f} seconds")

            # Yield kết quả cuối cùng
            yield {
                "type": "final",
                "content": full_response,
                "full_response": full_response,
                "execution_time": end_time - start_time
            }

        except Exception as e:
            logger.error(f"❌ Error in agent streaming execution: {str(e)}")
            logger.warning(f"input:{input}")
            yield {
                "type": "error",
                "content": f"Error: {str(e)}",
                "full_response": ""
            }
