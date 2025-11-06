# --------------------------------------------------------------
# Imports
# --------------------------------------------------------------
from dotenv import load_dotenv
from sqlalchemy import create_engine
import os
import importlib   # To dynamically check if modules are installed
import subprocess  # To run shell commands (pip install / streamlit run)
import sys         # To get the Python executable path
import time        # To wait for Streamlit server startup
import webbrowser  # To open the Streamlit app in the default browser

# load the .env file variables
load_dotenv()


# --------------------------------------------------------------
# Functions
# --------------------------------------------------------------
def db_connect(): #  DDBB conection
    engine = create_engine(os.getenv('DATABASE_URL'))
    engine.connect()
    return engine

def ensure_package(package_name: str): #  Ensures dependencies are installed
    try:
        importlib.import_module(package_name)
    except ImportError:
        print(f"🔧 Installing missing package: {package_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", package_name])

def run_streamlit_app(app_path: str, wait_secs: int, port: int = 8501, extra_args=None):
    """Lanza Streamlit; extra_args permite pasar flags personalizados tras '--'."""
    extra_args = extra_args or []
    cmd = [
        sys.executable, "-m", "streamlit", "run", app_path,
        "--server.port", str(port),
        "--",  # todo lo que vaya después son args para tu script Streamlit
        *extra_args
    ]
    subprocess.Popen(cmd, env=os.environ.copy())
    time.sleep(sec)
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Streamlit stopped by user.")
        process.terminate()

def open_web_browser(url: str): # Try opening in the default browser, otherwise print a fallback message
    if not webbrowser.open(url):
        print(f"⚠️ Unable to open browser automatically.\n🔗 Please open manually:" + url)