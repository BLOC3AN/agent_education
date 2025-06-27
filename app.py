from fastapi import FastAPI, Body # Import Body để nhận input từ request body
import uvicorn
from src.agents.agent import AgentConversation 
from src.tools.get_all_MCP_tools import discover_and_create_mcp_tools
from pydantic import BaseModel

app = FastAPI()
agent = AgentConversation()
agent.tools.extend(discover_and_create_mcp_tools())
class AgentRequest(BaseModel):
    input: str # Tên trường phải khớp với JSON mà client gửi (ví dụ: {"input": "Hello"})


@app.post("/agent/request")
def call_agent(request_data: AgentRequest): # FastAPI sẽ tự động parse JSON body vào đối tượng này
    print(f"Nhận yêu cầu từ GUI: {request_data.input}")
    result = agent.run(request_data.input) # Truy cập dữ liệu thông qua .input
    return {"response": result} # FastAPI sẽ tự động chuyển đổi dictionary này thành JSON response

if __name__ =="__main__":
    print("Khởi động Agent FastAPI server trên http://0.0.0.0:2222")
    uvicorn.run(app, host='0.0.0.0', port=2222) 