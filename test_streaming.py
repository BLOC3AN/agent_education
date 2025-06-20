#!/usr/bin/env python3
"""
Test script để so sánh invoke vs streaming mode
"""

from dotenv import load_dotenv
import os
import time
load_dotenv()

from src.agents.agent import AgentConversation

def test_invoke_mode():
    """Test invoke mode (truyền thống)"""
    print("🔄 Testing INVOKE mode...")
    print("=" * 50)
    
    agent = AgentConversation()
    
    start_time = time.time()
    result = agent.run(input="Hãy giải thích về tầm quan trọng của việc học toán cho học sinh tiểu học")
    end_time = time.time()
    
    print(f"⏱️ Thời gian thực hiện: {end_time - start_time:.2f} giây")
    print(f"📝 Phản hồi: {result.get('output', 'Không có phản hồi')}")
    print("\n")

def test_streaming_mode():
    """Test streaming mode"""
    print("🌊 Testing STREAMING mode...")
    print("=" * 50)
    
    agent = AgentConversation()
    
    start_time = time.time()
    full_response = ""
    
    print("📝 Phản hồi streaming:")
    for chunk in agent.stream(input="Hãy giải thích về tầm quan trọng của việc học toán cho học sinh tiểu học"):
        if chunk["type"] == "output":
            # In ra từng chunk
            new_content = chunk["content"]
            print(new_content, end="", flush=True)
            full_response = chunk["full_response"]
            
        elif chunk["type"] == "action":
            print(f"\n🔧 [ACTION]: {chunk['content']}")
            
        elif chunk["type"] == "intermediate_step":
            print(f"\n🔧 [STEP]: {chunk['content']}")
            
        elif chunk["type"] == "final":
            end_time = time.time()
            print(f"\n\n⏱️ Thời gian thực hiện: {end_time - start_time:.2f} giây")
            print(f"📊 Độ dài phản hồi: {len(chunk['full_response'])} ký tự")
            break
            
        elif chunk["type"] == "error":
            print(f"\n❌ Lỗi: {chunk['content']}")
            break

def main():
    """Chạy cả hai test"""
    print("🎓 Agent Education - Test Invoke vs Streaming")
    print("=" * 60)
    
    # Test invoke mode
    test_invoke_mode()
    
    print("\n" + "=" * 60 + "\n")
    
    # Test streaming mode  
    test_streaming_mode()
    
    print("\n" + "=" * 60)
    print("✅ Hoàn thành test!")

if __name__ == "__main__":
    main()
