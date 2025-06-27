import streamlit as st
import requests 
from typing import Any, Dict
from src.utils.logger import Logger
logger=Logger(__name__)

# --- Cấu hình chung ---
# Cấu hình page chỉ chạy một lần
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title="Agent Education", page_icon="🎓")
    st.session_state.page_config_set = True

# Định nghĩa URL của Agent FastAPI của bạn
# Đảm bảo Agent FastAPI đang chạy tại địa chỉ và cổng này
AGENT_API_URL = "http://localhost:2222/agent/request"

# --- Lớp GUI ---
class GUI:
    def __init__(self):
        # Không cần khởi tạo AgentConversation ở đây nữa vì nó là dịch vụ FastAPI riêng
        pass

    def init_gui(self):
        """Khởi tạo giao diện người dùng chính của Streamlit."""
        st.title("🎓 Agent Education - AI Giáo dục")
        st.markdown("*Hệ thống AI hỗ trợ giáo dục và tư vấn học tập*")

        # Sidebar để chọn mode và các tùy chọn khác
        with st.sidebar:
            st.header("⚙️ Cài đặt")
            # Nút toggle cho chế độ streaming (chỉ là giao diện, logic thực tế sẽ nhận full response)
            streaming_mode = st.toggle("🔄 Streaming Mode", value=True, help="Bật để hiển thị hiệu ứng 'đang suy nghĩ' và đợi phản hồi đầy đủ. (Lưu ý: API hiện tại không hỗ trợ streaming từng token)")

            if st.button("🗑️ Xóa lịch sử chat"):
                st.session_state.messages = []
                st.rerun() # Làm mới lại ứng dụng để xóa lịch sử

        # Khởi tạo session state cho messages nếu chưa có
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Hiển thị lịch sử chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Ô nhập liệu cho người dùng
        # Sử dụng st.chat_input để có giao diện nhập liệu đẹp và tự động lưu trạng thái
        if prompt := st.chat_input("Hãy hỏi gì đó về giáo dục, học tập hoặc sức khỏe..."):
            # Thêm tin nhắn người dùng vào lịch sử chat
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Xử lý phản hồi từ AI Agent (gọi API)
            with st.chat_message("assistant"):
                if streaming_mode:
                    self._handle_response_via_api_with_spinner(prompt)
                else:
                    self._handle_response_via_api_direct(prompt)

    def _call_agent_api(self, user_input: str):
        """
        Gửi yêu cầu HTTP POST đến Agent FastAPI và trả về phản hồi.
        """
        try:
            payload = {"input": user_input} # Dữ liệu cần gửi trong body của POST request

            # Gửi POST request đến Agent API
            response = requests.post(AGENT_API_URL, json=payload, timeout=60) # Thêm timeout
            response.raise_for_status() # Ném HTTPError cho mã trạng thái lỗi (4xx hoặc 5xx)

            # Phân tích phản hồi JSON từ Agent
            return response.json()

        except requests.exceptions.Timeout:
            return {"error": "API Timeout: Agent không phản hồi kịp thời."}
        except requests.exceptions.ConnectionError:
            return {"error": "Lỗi kết nối: Không thể kết nối tới Agent API. Đảm bảo Agent đang chạy."}
        except requests.exceptions.HTTPError as e:
            return {"error": f"Lỗi HTTP từ Agent: {e.response.status_code} - {e.response.text}"}
        except requests.exceptions.RequestException as e:
            return {"error": f"Lỗi yêu cầu: {e}"}
        except Exception as e:
            return {"error": f"Lỗi không xác định khi gọi API: {e}"}

    def _handle_response_via_api_with_spinner(self, prompt):
        """
        Xử lý phản hồi bằng cách gọi API, hiển thị spinner và update đầy đủ khi có kết quả.
        (Mô phỏng "streaming" nhưng thực tế là chờ full response từ API).
        """
        message_placeholder = st.empty() # Placeholder để cập nhật tin nhắn
        debug_placeholder = st.empty() # Placeholder cho debug/loading info

        message_placeholder.markdown("🤔 Agent đang suy nghĩ... ")
        debug_placeholder.info("Đang chờ phản hồi từ Agent API...")

        try:
            api_result = self._call_agent_api(prompt)
            logger.info(f"Result from agent : {api_result.keys()}")

            if "error" in api_result:
                full_response = f"❌ Lỗi: {api_result['error']}"
                message_placeholder.error(full_response)
                debug_placeholder.empty() # Xóa debug placeholder
            else:
                # Giả sử Agent FastAPI trả về {"response": "..."}
                response_content = api_result.get("response", "Không nhận được phản hồi hợp lệ từ Agent.")
                full_response:Any|Dict = response_content
                with message_placeholder.container():
                    st.markdown(full_response['output']) # Hiển thị toàn bộ phản hồi

                debug_placeholder.empty() # Xóa debug placeholder sau khi có kết quả

            # Thêm phản hồi vào lịch sử chat
            st.session_state.messages.append({"role": "assistant", "content": full_response['output']})

        except Exception as e:
            error_msg = f"❌ Đã xảy ra lỗi không mong muốn trong Streamlit: {str(e)}"
            message_placeholder.error(error_msg)
            debug_placeholder.empty()
            st.session_state.messages.append({"role": "assistant", "content": error_msg})


    def _handle_response_via_api_direct(self, prompt):
        """
        Xử lý phản hồi bằng cách gọi API và hiển thị kết quả trực tiếp (không có hiệu ứng streaming).
        """
        with st.spinner("Đang suy nghĩ..."):
            try:
                api_result = self._call_agent_api(prompt)
            
                if "error" in api_result:
                    response_content = f"❌ Lỗi: {api_result['error']}"
                    st.error(response_content)
                else:
                    # Giả sử Agent FastAPI trả về {"response": "..."}
                    response_content = api_result.get("response", "Không nhận được phản hồi hợp lệ từ Agent.")
                    st.markdown(response_content)

                # Thêm phản hồi vào lịch sử chat
                st.session_state.messages.append({"role": "assistant", "content": response_content})

            except Exception as e:
                error_msg = f"❌ Đã xảy ra lỗi không mong muốn trong Streamlit: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

# --- Hàm chạy ứng dụng Streamlit ---
def run_gui():
    gui = GUI()
    gui.init_gui()

# --- Điểm bắt đầu của ứng dụng ---
if __name__ == "__main__":
    run_gui()