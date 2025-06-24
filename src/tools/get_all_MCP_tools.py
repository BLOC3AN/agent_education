from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
import requests
from src.utils.logger import Logger
import json
import os
logger = Logger(__name__)

class Settings:
    def __init__(self):
        # Load environment variables with defaults
        self.mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp-server:9099")
# Create settings instance
settings = Settings()


class MCPTool(BaseTool):
    """
    Một lớp BaseTool của LangChain đại diện cho một tool được khám phá từ MCP Service.
    """
    name: str = "mcp_booking_tool"
    description: str = "Tool được khám phá thông qua MCP Service"
    endpoint: str
    token: str
    user_id: str
    
    
    def _run(self, tool_input: Optional[Dict[str, Any]] = None, **kwargs) -> str:
        headers = {"Content-Type": "application/json"}
        full_url = f"{settings.mcp_server_url}{self.endpoint}"
        
        logger.info(f"🔧 MCPTool '{self.name}' called with endpoint: {self.endpoint}")
        logger.info(f"🔗 Full URL: {full_url}")
        
        try:
            # Log the incoming parameters
            logger.info(f"📥 Tool input type: {type(tool_input)}")
            logger.info(f"📥 Tool input: {tool_input}")
            logger.info(f"📥 kwargs keys: {list(kwargs.keys())}")
            
            payload = tool_input if tool_input is not None else kwargs
            if not isinstance(payload, dict):
                logger.error(f"⚠️ Invalid payload type: {type(payload)}")
                return f"⚠️ MCPTool expects a dictionary input but got: {type(payload)}"
            
            # Log the payload before context addition
            logger.info(f"📦 Initial payload keys: {list(payload.keys())}")
            
            payload['token'] = self.token
            payload['user_id'] = self.user_id
            
            # Log the final payload
            logger.info(f"📦 Final payload keys: {list(payload.keys())}")
            
            # Log request details
            logger.info(f"🚀 Sending request to MCP endpoint: {self.endpoint}")
            
            response = requests.post(full_url, json=payload, headers=headers)
            logger.info(f"📡 Response status code: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"✅ Received successful response from MCP {result}")
            
            return json.dumps(result, ensure_ascii=False)

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"❌ HTTP error: {str(http_err)}")
            return f"❌ HTTP error: {str(http_err)}"
        except Exception as e:
            logger.error(f"❌ MCPTool Error: {str(e)}")
            import traceback
            logger.error(f"❌ Traceback: {traceback.format_exc()}")
            return f"❌ MCPTool Error: {str(e)}"

def discover_and_create_mcp_tools(token: str = "", user_id: str = "") -> List[BaseTool]:
    """
    Khám phá các tools từ MCP Service và tạo các đối tượng BaseTool của LangChain.
    """
    headers = {"Content-Type": "application/json"}
    capabilities_url = f"{settings.mcp_server_url}/capabilities"

    try:
        response = requests.get(capabilities_url, headers=headers)
        response.raise_for_status()
        capabilities = response.json()
        logger.info(f"Capabilities discovered: {[cap['mcp_schema'].get('name', 'unknown') for cap in capabilities]}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error discovering MCP capabilities: {e}")
        return []

    langchain_tools = []
    for capability in capabilities:
        try:
            schema = capability['mcp_schema']
            # Log the full schema structure to debug
            logger.info(f"Schema structure keys: {list(schema.keys())}")
            
            name = schema.get("name")
            description = schema.get("description")
            
            # Check if endpoint exists and has the expected structure
            if "endpoint" not in schema or "url" not in schema["endpoint"]:
                logger.error(f"Missing endpoint or url in schema for {name}")
                continue
                
            endpoint = schema["endpoint"]["url"]
            
            # Get args_schema if it exists
            args_schema = schema.get("args_schema")
            if not args_schema:
                logger.warning(f"Missing args_schema for {name}, using default empty schema")
                args_schema = {
                    "type": "object",
                    "properties": {}
                }
            
            logger.info(f"Creating tool: {name} with endpoint {endpoint}")
            
            mcp_tool_instance = MCPTool(
                name=name, 
                description=description,
                args_schema=args_schema,
                endpoint=endpoint,
                token=token,
                user_id=user_id
            )
            langchain_tools.append(mcp_tool_instance)
            
        except KeyError as ke:
            logger.error(f"Missing required key in capability schema: {ke}")
            logger.error(f"Schema content: {capability.get('mcp_schema', {})}")
            continue
        except Exception as e:
            logger.error(f"Error creating tool from capability: {e}")
            continue

    logger.info(f"Discovered {len(langchain_tools)} tools from MCP Service.")
    return langchain_tools