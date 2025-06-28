from fastapi import FastAPI, Body # Import Body để nhận input từ request body
import uvicorn
from src.agents.agent import AgentConversation 
from src.tools.get_all_MCP_tools import discover_and_create_mcp_tools
from src.tools.retrieve import retrieve_data_giao_an, get_all_collections

from pydantic import BaseModel

app = FastAPI()
agent = AgentConversation()
agent.tools.append(retrieve_data_giao_an)
agent.tools.extend(discover_and_create_mcp_tools())
class AgentRequest(BaseModel):
    input: str # Tên trường phải khớp với JSON mà client gửi (ví dụ: {"input": "Hello"})


@app.post("/agent/request")
def call_agent(request_data: AgentRequest):
    try:
        result = agent.run(request_data.input)
        if isinstance(result, str):
            result = {"output": result}
        return {"response": result}
    except Exception as e:
        return {"error": str(e)}

if __name__ =="__main__":
    print("Khởi động Agent FastAPI server trên http://0.0.0.0:2222")
    uvicorn.run(app, host='0.0.0.0', port=2222) 