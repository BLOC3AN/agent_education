import pypandoc
import os
from datetime import datetime
from src.utils.google_drive_manager import GoogleDriveManager
from src.utils.logger import Logger
logger=Logger(__name__)

def convert_md_to_docx_with_template(message, output_filename=None, output_dir:str='/app/data/agent_data'):
    """
    Convert markdown content to docx file
    Args:
        message: Markdown content to convert
        output_filename: Name of output file (without extension)
        output_dir: Directory to save the file
    """
    # Tạo output directory nếu chưa có
    os.makedirs(output_dir, exist_ok=True)

    # Tạo filename nếu không có
    if not output_filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"document_{timestamp}"

    # Đảm bảo có extension .docx
    if not output_filename.endswith('.docx'):
        output_filename += '.docx'

    # Full path
    output_path = os.path.join(output_dir, output_filename)

    try:
        drive_manager=GoogleDriveManager()
        # Convert markdown to docx
        pypandoc.convert_text(
            source=message,
            to='docx',
            format='md',
            outputfile=output_path
        )
        logger.info(f"Đã tạo file: {output_path}")

        docx_mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        drive_manager.upload_file(output_path, mimetype=docx_mime_type)
        logger.info("Uploaded into Google Driver")
        
        return {
            "status": "success",
            "output_path": output_path,
            "filename": output_filename
        }
    except Exception as e:
        logger.error(f"❌ Lỗi khi tạo file: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
  
