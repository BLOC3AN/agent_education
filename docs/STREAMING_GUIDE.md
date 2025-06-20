# 🌊 Hướng dẫn Streaming trong Agent Education

## 📋 Tổng quan

Agent Education hiện hỗ trợ hai mode hoạt động:
- **Invoke Mode**: Phản hồi một lần (truyền thống)
- **Streaming Mode**: Phản hồi theo thời gian thực

## 🔄 So sánh Invoke vs Streaming

### Invoke Mode (Truyền thống)
```python
agent = AgentConversation()
result = agent.run(input="Câu hỏi của bạn")
print(result["output"])
```

**Ưu điểm:**
- ✅ Đơn giản, dễ sử dụng
- ✅ Phản hồi hoàn chỉnh một lần
- ✅ Phù hợp cho batch processing

**Nhược điểm:**
- ❌ Người dùng phải chờ đến khi hoàn thành
- ❌ Không có feedback trong quá trình xử lý
- ❌ Trải nghiệm người dùng kém hơn

### Streaming Mode (Thời gian thực)
```python
agent = AgentConversation()
for chunk in agent.stream(input="Câu hỏi của bạn"):
    if chunk["type"] == "output":
        print(chunk["content"], end="", flush=True)
    elif chunk["type"] == "final":
        break
```

**Ưu điểm:**
- ✅ Phản hồi theo thời gian thực
- ✅ Trải nghiệm người dùng tốt hơn
- ✅ Có thể theo dõi quá trình xử lý
- ✅ Giảm cảm giác chờ đợi

**Nhược điểm:**
- ❌ Phức tạp hơn trong implementation
- ❌ Cần xử lý nhiều loại chunk khác nhau

## 🛠️ Cách sử dụng Streaming

### 1. Trong Code Python

```python
from src.agents.agent import AgentConversation

agent = AgentConversation()

for chunk in agent.stream(input="Hãy giải thích về AI"):
    if chunk["type"] == "output":
        # Nội dung phản hồi từng phần
        print(chunk["content"], end="", flush=True)
        
    elif chunk["type"] == "action":
        # Thông tin về action đang thực hiện
        print(f"\n🔧 Đang thực hiện: {chunk['content']}")
        
    elif chunk["type"] == "intermediate_step":
        # Các bước trung gian
        print(f"\n📋 Bước: {chunk['content']}")
        
    elif chunk["type"] == "final":
        # Kết thúc streaming
        print(f"\n✅ Hoàn thành!")
        print(f"📊 Thời gian: {chunk['execution_time']:.2f}s")
        break
        
    elif chunk["type"] == "error":
        # Xử lý lỗi
        print(f"\n❌ Lỗi: {chunk['content']}")
        break
```

### 2. Trong Streamlit GUI

Trong giao diện Streamlit, bạn có thể:
- Bật/tắt Streaming Mode trong sidebar
- Xem phản hồi xuất hiện từng từ
- Theo dõi các action đang thực hiện

## 📊 Cấu trúc Chunk Response

Mỗi chunk trong streaming có cấu trúc:

```python
{
    "type": "output|action|intermediate_step|final|error",
    "content": "Nội dung của chunk",
    "full_response": "Toàn bộ phản hồi đến thời điểm hiện tại"
}
```

### Các loại chunk:

- **`output`**: Nội dung phản hồi từng phần
- **`action`**: Thông tin về tool/action đang thực hiện
- **`intermediate_step`**: Các bước xử lý trung gian
- **`final`**: Chunk cuối cùng với thông tin tổng kết
- **`error`**: Thông báo lỗi nếu có

## 🧪 Test Streaming

Chạy file test để so sánh:

```bash
python test_streaming.py
```

## ⚙️ Cấu hình

Streaming sử dụng cùng cấu hình với invoke mode:
- `MAX_ITERATIONS`: 5
- `MAX_EXECUTION_TIME`: 1.5 giây
- `EARLY_STOPPING_METHOD`: "generate"

## 🔧 Troubleshooting

### Lỗi thường gặp:

1. **Streaming bị dừng giữa chừng**
   - Kiểm tra timeout settings
   - Xem log để tìm lỗi

2. **Không có output chunks**
   - Agent có thể không có tools
   - Kiểm tra prompt và input

3. **Performance chậm**
   - Streaming có thể chậm hơn invoke một chút
   - Điều chỉnh `MAX_EXECUTION_TIME` nếu cần

## 🚀 Best Practices

1. **Sử dụng streaming khi:**
   - Phản hồi dài (>100 từ)
   - Cần trải nghiệm người dùng tốt
   - Có thể có tools/actions

2. **Sử dụng invoke khi:**
   - Phản hồi ngắn
   - Batch processing
   - Không cần real-time feedback

3. **Xử lý lỗi:**
   - Luôn handle chunk type "error"
   - Có fallback cho trường hợp streaming fail

## 📈 Roadmap

- [ ] Hỗ trợ pause/resume streaming
- [ ] Streaming với multiple agents
- [ ] WebSocket support cho real-time
- [ ] Caching cho streaming responses
