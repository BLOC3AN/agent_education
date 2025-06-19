from dotenv import load_dotenv
import os
load_dotenv()

from src.agents.agent import AgentConversation

if __name__ == "__main__":
    agent = AgentConversation()
    result = agent.run(input="Hãy cho tôi biết nếu bị lở chân tay thì sẽ ăn cái gì?")
    print(result)

