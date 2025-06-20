import streamlit as st
from src.agents.agent import AgentConversation

# Cấu hình page chỉ chạy một lần
if "page_config_set" not in st.session_state:
    st.set_page_config(page_title="Agent Education", page_icon="🎓")
    st.session_state.page_config_set = True

class GUI:
    def __init__(self, agent):
        self.agent = agent

    def init_gui(self):
        st.title("🎓 Agent Education - AI Giáo dục")
        st.markdown("*Hệ thống AI hỗ trợ giáo dục và tư vấn học tập*")

        # Sidebar để chọn mode
        with st.sidebar:
            st.header("⚙️ Cài đặt")
            streaming_mode = st.toggle("🔄 Streaming Mode", value=True, help="Bật để xem phản hồi theo thời gian thực")

            if st.button("🗑️ Xóa lịch sử chat"):
                st.session_state.messages = []
                st.rerun()

        # Khởi tạo session state cho messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Hiển thị lịch sử chat
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input với key duy nhất dựa trên session
        chat_key = f"chat_input_{len(st.session_state.messages)}"
        if prompt := st.chat_input("Hãy hỏi gì đó về giáo dục, học tập hoặc sức khỏe...", key=chat_key):
            # Thêm tin nhắn người dùng
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Xử lý phản hồi từ AI
            with st.chat_message("assistant"):
                if streaming_mode:
                    # Sử dụng streaming mode
                    self._handle_streaming_response(prompt)
                else:
                    # Sử dụng invoke mode (truyền thống)
                    self._handle_invoke_response(prompt)

    def _handle_streaming_response(self, prompt):
        """Xử lý phản hồi với streaming mode"""
        message_placeholder = st.empty()
        debug_placeholder = st.empty()

        try:
            full_response = ""
            intermediate_steps = []

            # Sử dụng streaming
            for chunk in self.agent.stream(input=prompt, session_id="streamlit"):
                if chunk["type"] == "output":
                    # Cập nhật response theo thời gian thực
                    full_response = chunk["full_response"]
                    message_placeholder.markdown(full_response + "▌")

                elif chunk["type"] == "intermediate_step":
                    # Lưu intermediate steps để hiển thị sau
                    intermediate_steps.extend(chunk["content"])

                elif chunk["type"] == "action":
                    # Hiển thị action đang thực hiện
                    with debug_placeholder.container():
                        st.info(f"🔧 Đang thực hiện: {chunk['content']}")

                elif chunk["type"] == "final":
                    # Kết thúc streaming
                    full_response = chunk["full_response"]
                    message_placeholder.markdown(full_response)

                    # Hiển thị thông tin debug nếu có
                    if intermediate_steps:
                        with debug_placeholder.expander("🔧 Chi tiết xử lý"):
                            for i, step in enumerate(intermediate_steps):
                                st.write(f"**Bước {i+1}:** {step}")
                    else:
                        debug_placeholder.empty()

                    # Lưu vào session state
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    break

                elif chunk["type"] == "error":
                    # Xử lý lỗi
                    error_msg = f"❌ Đã xảy ra lỗi: {chunk['content']}"
                    message_placeholder.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    break

        except Exception as e:
            error_msg = f"❌ Đã xảy ra lỗi không mong muốn: {str(e)}"
            message_placeholder.error(error_msg)
            st.session_state.messages.append({"role": "assistant", "content": error_msg})

    def _handle_invoke_response(self, prompt):
        """Xử lý phản hồi với invoke mode (truyền thống)"""
        with st.spinner("Đang suy nghĩ..."):
            try:
                result = self.agent.run(input=prompt, session_id="streamlit")

                # Lấy phản hồi từ output
                if "output" in result:
                    response = result["output"]
                else:
                    response = "Xin lỗi, tôi không thể xử lý câu hỏi này lúc này."

                # Hiển thị phản hồi
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

                # Hiển thị thông tin debug nếu có intermediate_steps
                if "intermediate_steps" in result and result["intermediate_steps"]:
                    with st.expander("🔧 Chi tiết xử lý"):
                        for i, step in enumerate(result["intermediate_steps"]):
                            st.write(f"**Bước {i+1}:** {step}")

            except Exception as e:
                error_msg = f"❌ Đã xảy ra lỗi: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

def run_gui():
    # Khởi tạo agent chỉ một lần
    if "agent" not in st.session_state:
        st.session_state.agent = AgentConversation()

    # Khởi tạo GUI
    gui = GUI(st.session_state.agent)
    gui.init_gui()