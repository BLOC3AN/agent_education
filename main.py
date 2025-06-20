from dotenv import load_dotenv
from src.utils.logger import Logger
logger = Logger(__name__)
import os
load_dotenv()
from gui.gui import run_gui
if __name__ == "__main__":
    run_gui()


