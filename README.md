# 🎓 Agent Education - Hệ thống AI Giáo dục

Một hệ thống AI Agent thông minh được xây dựng bằng LangChain và Google Gemini, chuyên biệt cho lĩnh vực giáo dục và tư vấn học tập.

## 📋 Mô tả dự án

Agent Education là một chatbot AI được thiết kế để hoạt động như một giáo sư thông thái, có khả năng:
- Trả lời các câu hỏi giáo dục
- Tư vấn học tập và sức khỏe
- Hỗ trợ giải đáp thắc mắc của học sinh, sinh viên
- Lưu trữ và quản lý lịch sử hội thoại

## 🏗️ Kiến trúc hệ thống

```
agent_education/
├── src/
│   ├── agents/          # Các AI Agent chính
│   │   └── agent.py     # Agent hội thoại chính
│   ├── llms/           # Tích hợp mô hình ngôn ngữ
│   │   └── gemini.py   # Google Gemini LLM
│   ├── memory/         # Quản lý bộ nhớ hội thoại
│   │   └── memortConverSasion.py
│   ├── prompts/        # Template prompt cho agent
│   │   └── conversation_agent.md
│   ├── utils/          # Tiện ích hỗ trợ
│   │   └── logger.py   # Hệ thống logging
│   ├── tools/          # Công cụ mở rộng (đang phát triển)
│   ├── config/         # Cấu hình hệ thống
│   └── MCP/           # Model Context Protocol
├── data/              # Dữ liệu giáo dục
├── docs/              # Tài liệu dự án
├── deployment/        # Triển khai
├── notebook/          # Jupyter notebooks
└── main.py           # File chạy chính
```

## ✨ Tính năng chính

### 🤖 AI Agent thông minh
- **Conversation Agent**: Agent hội thoại chính với khả năng hiểu ngữ cảnh
- **Memory Management**: Lưu trữ và quản lý lịch sử hội thoại
- **Context Awareness**: Hiểu ngữ cảnh và duy trì mạch hội thoại

### 🧠 Tích hợp LLM mạnh mẽ
- **Google Gemini 2.0 Flash**: Mô hình ngôn ngữ tiên tiến
- **Tối ưu hóa hiệu suất**: Temperature=0, Top-p=0.2, Top-k=40
- **Xử lý lỗi thông minh**: Retry mechanism và error handling

### 📊 Logging và Monitoring
- **Real-time logging**: Theo dõi hoạt động của agent
- **Performance metrics**: Đo lường thời gian phản hồi
- **Error tracking**: Ghi lại và xử lý lỗi

## 🚀 Cài đặt và sử dụng

### Yêu cầu hệ thống
- Python 3.8+
- Google API Key cho Gemini
- Các thư viện trong requirements.txt

### Cài đặt

1. **Clone repository**
```bash
git clone <repository-url>
cd agent_education
```

2. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

3. **Cấu hình environment**
```bash
# Tạo file .env
echo "GOOGLE_API_KEY=your_google_api_key_here" > .env
```

### Chạy ứng dụng

```bash
python main.py
```

## 💡 Ví dụ sử dụng

```python
from src.agents.agent import AgentConversation

# Khởi tạo agent
agent = AgentConversation()

# Đặt câu hỏi
result = agent.run(input="Hãy cho tôi biết nếu bị lở chân tay thì sẽ ăn cái gì?")
print(result)
```

## 🔧 Cấu hình

### Agent Configuration
- **MAX_ITERATIONS**: 5 (Số lần thử tối đa)
- **MAX_EXECUTION_TIME**: 1.5 giây
- **EARLY_STOPPING_METHOD**: "generate"
- **VERBOSE**: True (Hiển thị chi tiết)

### Memory Configuration
- **ConversationBufferMemory**: Lưu trữ toàn bộ lịch sử
- **ConversationSummaryBufferMemory**: Tóm tắt khi vượt quá giới hạn token

## 📈 Roadmap phát triển

- [ ] **Enhanced Split-Task Agent**: Phát triển agent chia nhỏ nhiệm vụ
- [ ] **Context-Aware Split Task**: Agent hiểu ngữ cảnh cho việc chia task
- [ ] **Tool Integration**: Tích hợp các công cụ hỗ trợ giáo dục
- [ ] **Multi-Agent System**: Hệ thống đa agent chuyên biệt
- [ ] **Web Interface**: Giao diện web thân thiện
- [ ] **Database Integration**: Lưu trữ dữ liệu bền vững

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:
1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Push và tạo Pull Request

## 📄 License

Dự án này được phát hành dưới [MIT License](LICENSE).

## 📞 Liên hệ

- **Email**: [your-email@example.com]
- **GitHub**: [your-github-profile]

---

*Được phát triển với ❤️ bởi đội ngũ Agent Education*