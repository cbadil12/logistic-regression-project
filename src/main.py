"""
--------------------------------------------------------------
MAIN ENTRY POINT
--------------------------------------------------------------
1. Reads inputs from config/settings.py
2. Launches the Streamlit EDA App using the launcher module
"""

import os
from utils import db_connect, ensure_package, run_streamlit_app, open_web_browser

# --------------------------------------------------------------
# Inputs
# --------------------------------------------------------------
port = 8501
app_path = "src/EDA_on_streamlit.py"
url = "http://localhost:" + str(port)
waiting_secs = 5
engine = db_connect()


data_path  = "/workspaces/logistic-regression-project/data/raw/bank-marketing-campaign-data.csv"
os.environ["DATA_PATH"] = data_path

if __name__ == "__main__": # only run the code below if this file is being executed directly — not when it’s imported
    
    ensure_package("streamlit")
    print("🚀 Launching Streamlit EDA app...")
    # Pasamos la ruta como argumento CLI
    run_streamlit_app(app_path, waiting_secs, port, extra_args=["--data-path", data_path])
    print(f"🌐 Opening Streamlit interface at " + url)
    open_web_browser(url)






