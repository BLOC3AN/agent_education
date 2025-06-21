# 🎓 Agent Education - Hệ thống AI Giáo dục Thông minh

Một hệ thống AI Agent tiên tiến được xây dựng bằng LangChain, Google Gemini và RAG (Retrieval-Augmented Generation), chuyên biệt cho lĩnh vực giáo dục và tư vấn học tập.

## 📋 Mô tả dự án

Agent Education là một hệ thống AI đa tác vụ được thiết kế để hoạt động như một giáo sư thông thái, có khả năng:

### 🎯 Tính năng chính
- **Trả lời câu hỏi giáo dục**: Sử dụng RAG để tìm kiếm thông tin từ tài liệu giáo dục
- **Tư vấn học tập và sức khỏe**: Agent chuyên biệt cho từng lĩnh vực
- **Chia nhỏ nhiệm vụ phức tạp**: Split-task agent với khả năng hiểu ngữ cảnh
- **Quản lý lịch sử hội thoại**: Lưu trữ và tìm kiếm conversation history
- **Embedding tài liệu**: Xử lý và vector hóa tài liệu giáo dục (.docx)
- **Vector search**: Tìm kiếm ngữ nghĩa với Qdrant vector database

## 🏗️ Kiến trúc hệ thống

```
agent_education/
├── src/
│   ├── agents/                    # AI Agent
│   │   └── agent.py              # Agent hội thoại chính
│   ├── llms/                     # Tích hợp mô hình ngôn ngữ
│   │   └── gemini.py            # Google Gemini LLM
│   ├── RAG/                     # Retrieval-Augmented Generation
│   │   ├── embedded_data.py     # Xử lý embedding tài liệu
│   │   └── qdrant_vectordb.py   # Qdrant vector database
│   ├── memory/                  # Quản lý bộ nhớ hội thoại
│   │   ├── memortConverSasion.py # Memory conversation
│   │   ├── redis_memory.py      # Redis memory integration
│   │   └── redis_summaryMemory.py # Redis summary memory
│   ├── prompts/                 # Template prompt cho agent
│   │   └── conversation_agent.md
│   ├── tools/                   # Công cụ hỗ trợ
│   │   └── retrieve.py          # Tool tìm kiếm thông tin
│   ├── utils/                   # Tiện ích hỗ trợ
│   │   ├── logger.py           # Hệ thống logging
│   │   └── redis_client.py     # Redis client cho caching
│   ├── config/                  # Cấu hình hệ thống (trống)
│   └── MCP/                    # Model Context Protocol (trống)
├── data/                       # Dữ liệu và storage
│   ├── RAG/                   # Tài liệu giáo dục (.docx)
│   ├── qdrant/                # Qdrant vector storage
│   └── redis/                 # Redis cache storage
├── deployment/                 # Docker deployment
│   ├── docker-compose.yml     # Multi-service orchestration
│   ├── Dockerfile.agent       # Main application container
│   ├── Dockerfile.emmbed      # Embedding service container
│   └── requirements.txt       # Python dependencies
├── gui/                       # Streamlit web interface
│   └── gui.py                # Web GUI implementation
├── notebook/                  # Jupyter notebooks cho R&D
├── docs/                      # Tài liệu dự án
├── emmbed_data.py            # Script embedding tài liệu
└── main.py                   # Entry point chính
```

## ✨ Tính năng chính

### 🤖 AI Agent System
- **Conversation Agent**: Agent hội thoại chính với khả năng hiểu ngữ cảnh
- **Memory Management**: Lưu trữ và quản lý lịch sử hội thoại với Redis
- **Redis Integration**: Multiple memory types (buffer, summary)
- **Retrieve Tool**: Công cụ tìm kiếm thông tin hỗ trợ agent

### 🔍 RAG (Retrieval-Augmented Generation)
- **Document Processing**: Xử lý tài liệu .docx và chia nhỏ thành chunks
- **Vector Embedding**: Sử dụng ColBERT model cho embedding chất lượng cao
- **Qdrant Vector DB**: Lưu trữ và tìm kiếm vector với hiệu suất cao
- **Semantic Search**: Tìm kiếm ngữ nghĩa thông minh trong tài liệu giáo dục
- **Multi-vector Support**: Hỗ trợ đa vector cho độ chính xác cao

### 🧠 Tích hợp LLM mạnh mẽ
- **Google Gemini 2.0 Flash**: Mô hình ngôn ngữ tiên tiến
- **Streaming Response**: Phản hồi theo thời gian thực
- **Tối ưu hóa hiệu suất**: Temperature=0, Top-p=0.2, Top-k=40
- **Xử lý lỗi thông minh**: Retry mechanism và error handling

### 🐳 Docker Deployment
- **Multi-service Architecture**: Agent, Qdrant, Redis, Embedding service
- **Container Orchestration**: Docker Compose với health checks
- **Scalable Design**: Có thể mở rộng theo nhu cầu
- **Production Ready**: Cấu hình bảo mật và tối ưu hiệu suất

### 🌐 Web Interface
- **Streamlit GUI**: Giao diện web thân thiện và responsive
- **Real-time Chat**: Chat interface với streaming responses
- **File Upload**: Upload và xử lý tài liệu giáo dục
- **History Management**: Quản lý lịch sử hội thoại

### 📊 Monitoring và Logging
- **Comprehensive Logging**: Theo dõi chi tiết hoạt động của hệ thống
- **Performance Metrics**: Đo lường thời gian phản hồi và throughput
- **Error Tracking**: Ghi lại và xử lý lỗi một cách thông minh
- **Health Checks**: Kiểm tra sức khỏe các services

## 🚀 Cài đặt và triển khai

### Yêu cầu hệ thống
- **Docker & Docker Compose**: Để chạy multi-service architecture
- **Python 3.10+**: Cho development
- **Google API Key**: Cho Gemini LLM
- **Tối thiểu 8GB RAM**: Cho Qdrant và embedding processes

### 🐳 Triển khai với Docker (Khuyến nghị)

1. **Clone repository**
```bash
git clone <repository-url>
cd agent_education
```

2. **Cấu hình environment**
```bash
# Tạo file .env
cat > .env << EOF
GOOGLE_API_KEY=your_google_api_key_here
QDRANT_URL=http://qdrant:6333
REDIS_HOST=redis
REDIS_PORT=6379
FOLDER_PATH=../data/RAG
COLLECTION_NAME=document
EOF
```

3. **Chuẩn bị dữ liệu**
```bash
# Tạo thư mục data và copy tài liệu .docx vào data/RAG/
mkdir -p data/RAG
# Copy các file .docx giáo dục vào data/RAG/
```

4. **Khởi động hệ thống**
```bash
cd deployment
docker-compose up -d
```

5. **Kiểm tra trạng thái services**
```bash
docker-compose ps
docker-compose logs -f
```

6. **Truy cập ứng dụng**
- **Web Interface**: http://localhost:8501
- **Qdrant Dashboard**: http://localhost:6333/dashboard
- **Redis**: localhost:6379

### 💻 Development Setup

1. **Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

2. **Chạy local development**
```bash
# Chạy chỉ Qdrant và Redis
docker-compose up qdrant redis -d

# Chạy embedding process
python emmbed_data.py

# Chạy main application
python main.py
```

### 📁 Quản lý dữ liệu

**Embedding tài liệu mới:**
```bash
# Copy file .docx vào data/RAG/
cp your_document.docx data/RAG/

# Chạy embedding process
docker-compose restart emmeded
# hoặc
python emmbed_data.py
```

**Kiểm tra Qdrant collections:**
```bash
curl http://localhost:6333/collections
```

## 💡 Ví dụ sử dụng

### 🗣️ Conversation Agent
```python
from src.agents.agent import AgentConversation

# Khởi tạo agent
agent = AgentConversation()

# Đặt câu hỏi giáo dục
result = agent.run(input="Hãy cho tôi biết nếu bị lở chân tay thì sẽ ăn cái gì?")
print(result)
```

### 🔧 Memory Management
```python
from src.memory.redis_memory import RedisMemory
from src.memory.redis_summaryMemory import RedisSummaryMemory

# Sử dụng Redis memory
redis_memory = RedisMemory(session_id="user_123")
summary_memory = RedisSummaryMemory(session_id="user_123")

# Lưu và lấy conversation history
redis_memory.save_context({"input": "Câu hỏi"}, {"output": "Trả lời"})
history = redis_memory.load_memory_variables({})
```

### 🔍 RAG với Qdrant
```python
from src.RAG.qdrant_vectordb import QdrantVectorDB

# Khởi tạo Qdrant client
qdrant = QdrantVectorDB()

# Tìm kiếm thông tin trong tài liệu
query = "phương pháp dạy toán cho trẻ em"
results = qdrant.query("document", query, limit=5)

for point in results.points:
    print(f"Score: {point.score}")
    print(f"Content: {point.payload['text']}")
```

### 🌐 Web Interface Usage
1. Truy cập http://localhost:8501
2. Nhập câu hỏi trong chat interface
3. Xem phản hồi streaming real-time
4. Upload tài liệu mới để mở rộng knowledge base

## 🔧 Cấu hình chi tiết

### 🤖 Agent Configuration
```python
# Conversation Agent
MAX_ITERATIONS = 5
MAX_EXECUTION_TIME = 1.5  # seconds
EARLY_STOPPING_METHOD = "generate"
VERBOSE = True

# Split-Task Agents
TASK_COMPLEXITY_THRESHOLD = 3
MAX_SUBTASKS = 10
CONTEXT_WINDOW_SIZE = 4000
```

### 🧠 Memory & Caching
```python
# Redis Configuration
REDIS_HOST = "redis"
REDIS_PORT = 6379
CACHE_TTL = 3600  # 1 hour

# Memory Types
ConversationBufferMemory      # Lưu trữ toàn bộ lịch sử
ConversationSummaryBufferMemory  # Tóm tắt khi vượt quá token limit
```

### 🔍 RAG Configuration
```python
# Qdrant Settings
QDRANT_URL = "http://qdrant:6333"
COLLECTION_NAME = "document"
VECTOR_SIZE = 128
DISTANCE_METRIC = "COSINE"

# Text Processing
CHUNK_SIZE = 500
CHUNK_OVERLAP = 100
EMBEDDING_MODEL = "colbert-ir/colbertv2.0"
```

### 🐳 Docker Services
```yaml
# Resource Limits
agent-education:
  memory: 10G
  cpus: '2.5'

qdrant:
  ports: [6333, 6334]
  storage: ../data/qdrant

redis:
  ports: [6379]
  persistence: enabled
```

## 🚨 Troubleshooting

### Vấn đề thường gặp

**1. Container embedding restart liên tục**
```bash
# Kiểm tra logs
docker logs agent-education-emmbed

# Kiểm tra network connectivity
docker exec agent-education-emmbed ping qdrant

# Restart services theo thứ tự
docker-compose restart qdrant
docker-compose restart emmeded
```

**2. Qdrant connection failed**
```bash
# Kiểm tra Qdrant service
curl http://localhost:6333/collections

# Kiểm tra network
docker network ls
docker network inspect deployment_agent-network
```

**3. Memory issues**
```bash
# Kiểm tra resource usage
docker stats

# Tăng memory limit trong docker-compose.yml
memory: 16G  # thay vì 10G
```

## 📈 Roadmap phát triển

### ✅ Đã hoàn thành
- [x] **Conversation Agent**: Agent hội thoại cơ bản
- [x] **RAG Integration**: Tích hợp Retrieval-Augmented Generation
- [x] **Vector Database**: Qdrant cho semantic search
- [x] **Docker Deployment**: Container orchestration
- [x] **Web Interface**: Streamlit GUI với streaming
- [x] **Memory Management**: Redis memory với multiple types
- [x] **Document Processing**: Embedding tài liệu .docx

### 🔄 Đang phát triển
- [ ] **Split-Task Agent**: Agent chia nhỏ nhiệm vụ phức tạp
- [ ] **Enhanced Split-Task**: Agent chia task nâng cao
- [ ] **Context-Aware Split**: Agent hiểu ngữ cảnh sâu
- [ ] **Tool Integration**: Mở rộng retrieve tool

### 🎯 Kế hoạch tương lai
- [ ] **Multi-modal Support**: Hỗ trợ hình ảnh, audio
- [ ] **Advanced Analytics**: Phân tích học tập và báo cáo
- [ ] **API Gateway**: RESTful API cho integration
- [ ] **Mobile App**: Ứng dụng di động
- [ ] **Kubernetes Deployment**: Triển khai production-scale
- [ ] **A/B Testing**: Framework để test các agent khác nhau

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng:

### 🔧 Development Workflow
1. **Fork repository** và clone về local
2. **Tạo feature branch**: `git checkout -b feature/amazing-feature`
3. **Setup development environment**:
   ```bash
   pip install -r requirements.txt
   docker-compose up qdrant redis -d
   ```
4. **Implement changes** và test thoroughly
5. **Commit changes**: `git commit -m 'Add amazing feature'`
6. **Push branch**: `git push origin feature/amazing-feature`
7. **Tạo Pull Request** với mô tả chi tiết

### 📝 Contribution Guidelines
- **Code Style**: Tuân thủ PEP 8 cho Python
- **Documentation**: Cập nhật README và docstrings
- **Testing**: Thêm tests cho features mới
- **Logging**: Sử dụng logger thống nhất
- **Docker**: Test với Docker environment

### 🎯 Areas for Contribution
- **New Agents**: Phát triển agents chuyên biệt mới
- **RAG Improvements**: Cải thiện retrieval và embedding
- **UI/UX**: Nâng cao giao diện Streamlit
- **Performance**: Tối ưu hóa hiệu suất
- **Documentation**: Viết tutorials và guides

## 📊 Performance Metrics

### 🚀 Benchmarks
- **Response Time**: < 2s cho câu hỏi đơn giản
- **RAG Retrieval**: < 500ms cho semantic search
- **Memory Usage**: < 8GB cho full deployment
- **Throughput**: 10+ concurrent users

### 📈 Monitoring
- **Logs**: Structured logging với timestamps
- **Metrics**: Response time, error rates, resource usage
- **Health Checks**: Automated service monitoring

## 📄 License

Dự án này được phát hành dưới [MIT License](LICENSE).

## 📞 Liên hệ & Hỗ trợ

- **Issues**: [GitHub Issues](https://github.com/your-repo/agent_education/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/agent_education/discussions)
- **Email**: agent.education.support@example.com

### 🆘 Hỗ trợ kỹ thuật
- **Documentation**: Xem `/docs` folder
- **Examples**: Xem `/notebook` folder
- **Troubleshooting**: Xem section Troubleshooting ở trên

---

## 🏆 Acknowledgments

- **LangChain**: Framework cho AI agents
- **Google Gemini**: LLM provider
- **Qdrant**: Vector database
- **Streamlit**: Web interface framework
- **Docker**: Containerization platform

*Được phát triển với ❤️ bởi đội ngũ Agent Education*

---

**⭐ Nếu project này hữu ích, hãy cho chúng tôi một star trên GitHub!**