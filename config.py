import os
from dotenv import load_dotenv

def setup_env():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ENV_PATH = os.path.join(BASE_DIR, "..", ".env")
    load_dotenv(ENV_PATH)