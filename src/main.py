"""
--------------------------------------------------------------
MAIN ENTRY POINT
--------------------------------------------------------------
1. Reads inputs from config/settings.py
2. Launches the Streamlit EDA App using the launcher module
"""

import os
import socket
from utils import db_connect, ensure_package, run_streamlit_app, open_web_browser

# --------------------------------------------------------------
# Inputs
# --------------------------------------------------------------
starting_port = 8000
tries_to_find_port = 10
app_path = "src/EDA_on_streamlit.py"
waiting_secs = 5
engine = db_connect()

data_path = "/workspaces/logistic-regression-project/data/raw/bank-marketing-campaign-data.csv"
os.environ["DATA_PATH"] = data_path


# --------------------------------------------------------------
# Utility: Find a free TCP port if current one is in use
# --------------------------------------------------------------
def get_available_port(start_port: int, max_tries: int = 5) -> int:
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port  # free
            port += 1
    raise RuntimeError(f"No free port found after trying {max_tries} ports starting from {start_port}.")


# --------------------------------------------------------------
# Main
# --------------------------------------------------------------
if __name__ == "__main__":  # only run the code below if this file is being executed directly — not when it’s imported
    
    ensure_package("streamlit")
    print("🚀 Launching Streamlit EDA app...")

    # Get first available port
    port = get_available_port(starting_port,tries_to_find_port)
    url = f"http://localhost:{port}"

    # Pass the path as a CLI argument
    run_streamlit_app(app_path, waiting_secs, port, extra_args=["--data-path", data_path])
    print(f"🌐 Opening Streamlit interface at {url}")
    open_web_browser(url)

