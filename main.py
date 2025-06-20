from dotenv import load_dotenv
import os
load_dotenv()

from src.agents.agent import AgentConversation
from gui.gui import run_gui

if __name__ == "__main__":
    run_gui()
