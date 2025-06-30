from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from typing import Dict, List
import os
import json
import sys

# Thêm thư mục gốc vào sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))  # Chỉ đi lên 2 cấp thay vì 3
sys.path.insert(0, project_root)

from src.tools.convert_md_to_docx import convert_md_to_docx_with_template
from src.utils.logger import Logger

logger = Logger(__name__)
logger.info(f"Current directory: {current_dir}")
logger.info(f"Project root: {project_root}")

app = FastAPI(
    title="MCP Research Tool Service",
    description="An API Gateway mimicking MCP for research purposes.",
    version="0.1.0"
)

# Add custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"❌ Validation error: {exc.errors()}")
    logger.error(f"❌ Request body: {exc.body}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

logger.info("✅ CORS middleware added to MCP server")

class ToolMetadata(BaseModel):
    mcp_schema:Dict

@app.get("/capabilities", 
         response_model=List[ToolMetadata],
         summary="Khám phá các khả năng (tools) có sẵn theo định dạng MCP.",
         dependencies=[])
async def get_capabilities():
    response_model = []
    schema_dir = os.path.join(project_root, "src", "MCP", "schema")

    if os.path.exists(schema_dir):
        for file in os.listdir(schema_dir):
            if file.endswith(".json"):
                schema_path = os.path.join(schema_dir, file)
                with open(schema_path, "r", encoding="utf-8") as f:
                    schema = json.load(f)
                    logger.info(f"Loading schema: {schema.keys()}")
                    response_model.append(ToolMetadata(mcp_schema=schema))

    logger.info("Providing list of available tools (capabilities).")
    return response_model


@app.post("/tools/convert_md_to_docx",
          summary="Convert markdown content to docx file with template",
          )
async def convert_md_to_docx(content_markdown:Dict):
    logger.info("Converting markdown content to docx file")
    logger.info(f"content_markdown: {content_markdown}")

    # Validate content_markdown
    if not content_markdown.get("message"):
        return {"status": "error", "error": "Missing 'message' field"}

    # Extract parameters
    message = content_markdown["message"]
    output_filename = content_markdown.get("output_filename", None)

    # Handle backward compatibility với output_path
    if not output_filename and "output_path" in content_markdown:
        output_path = content_markdown["output_path"]
        # Extract filename from path
        if "/" in output_path:
            output_filename = output_path.split("/")[-1]
        else:
            output_filename = output_path
        # Remove .docx extension if present
        if output_filename.endswith('.docx'):
            output_filename = output_filename[:-5]

    user_id = content_markdown.get("user_id", "default_user")

    # Add user_id to filename if provided
    if user_id and user_id != "default_user":
        if output_filename:
            output_filename = f"{user_id}_{output_filename}"
        else:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{user_id}_document_{timestamp}"

    try:
        result = convert_md_to_docx_with_template(message, output_filename)
        logger.info(f"Conversion result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in convert_md_to_docx: {str(e)}")
        return {"status": "error", "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9099, reload=True)
