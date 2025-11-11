# ===============================================================
# 📊 AUTOMATED EDA WEB APPLICATION
# ===============================================================
# Author: Carlos Luis Badillo
# Created on: December 2025
# Description:
#     This application provides an interactive, web-based environment
#     for performing an Exploratory Data Analysis (EDA) automatically.
#     Users can upload datasets, visualize summary statistics,
#     explore variable distributions, detect missing values, and
#     generate plots dynamically — all within a simple Streamlit interface.

# -------------------------------
# IMPORTS
# -------------------------------

# Main libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import math

# Scaling
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import MinMaxScaler

# Encoding
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

# Selection
from sklearn.feature_selection import SelectKBest, f_classif

# Split
from sklearn.model_selection import train_test_split

# Models
from sklearn.linear_model import LogisticRegression

# Models optimization
from sklearn.model_selection import ParameterGrid
from sklearn.model_selection import GridSearchCV

# Metrics for CLASSIFICATION models
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report

# Metrics for REGRESSION models
from sklearn.metrics import mean_squared_error, r2_score

# Web  application
import streamlit as st
import io, os, sys

# -------------------------------
# FUNCTIONS
# -------------------------------

# Reads the dataset path passed as a command-line argument
def get_data_path_from_command_line() -> str: 
    if "--data-path" in sys.argv: # Check if the '--data-path' argument exists
        index = sys.argv.index("--data-path") # Find its position
        if index + 1 < len(sys.argv): # Ensure there is a value after it (the actual path)
            return sys.argv[index + 1]
    return "" # Default: no path was provided

# Centralized state initialization
def set_default_inputs_for_init_session_state():
    defaults = {
        "df": None,
        "step0_done": False,
        "step1_done": False,
        "step2_done": False,
        "step3_done": False,
        "step4_done": False,
        "step5_done": False,
        "step6_done": False,
        "step7_done": False,
        "step8_done": False,
        "step9_done": False,
        "step10_done": False
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# Dynamically changes step completion flags in st.session_state
def update_completion_state(step: int):
    for key in st.session_state.keys():
        if key.startswith("step") and key.endswith("_done"):
            try:
                step_number = int(key.replace("step", "").replace("_done", ""))
            except ValueError:
                continue  # skip malformed keys
            st.session_state[key] = (step_number <= step) # Update the flag: True if step_number <= current step

# Dynamically updates df saved in session_state according to the step
def update_df(df: pd.DataFrame):
    st.session_state.df  = df

# Set completion button
def set_completion_button(step_num: int, df: pd.DataFrame, error=None):
    key = f"step{step_num}_done"
    if st.session_state.get(key, False):
        label ="✅ STEP " + str(step_num) + " COMPLETED!"
    else:
        label = "COMPLETE STEP " + str(step_num) + " ➡️ PROCEED TO STEP " + str(step_num + 1)
    st.button(
        label=label if not error else error,
        use_container_width=True,
        disabled = st.session_state.get(key, False) or error is not None,
        on_click=lambda: (update_df(df), update_completion_state(step_num)))

# Fixed top banner showing progress
def sticky_banner():
    
    # Dummy progress info for demo
    steps = [("✅" if st.session_state.get(f"step{i}_done", False) else "⏳") + f" Step {i}" for i in range(0, 11)]
    progress_text = " | ".join(steps)

    # Inline HTML + CSS banner
    st.markdown(
        f"""
        <style>
        div[data-testid="stAppViewContainer"] {{
            padding-top: 2.5rem;
        }}
        div[data-testid="stHeader"] {{
            display: none;
        }}
        #fixedBanner {{
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            background-color: #0e1117;
            color: white;
            border-bottom: 1px solid #444;
            padding: 0.4rem 1rem;
            font-size: 0.9rem;
            z-index: 9999;
        }}
        </style>
        <div id="fixedBanner">
            🧭 <b>Progress:</b> {progress_text}
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# SIDEBAR INPUTS
# -------------------------------
def sidebar_inputs():
    # STEP 0
    st.sidebar.subheader("STEP 0) LOAD RAW DATAFRAME")
    st.sidebar.selectbox(
        "Dataset separator",
        options=[",", ";"],
        index=1,
        key="data_separator",
        help="Character that separates data.",
        on_change=lambda: update_completion_state(-1))
    # STEP 1
    if st.session_state.step0_done:
        st.sidebar.subheader("STEP 1 - EXPLORE DATAFRAME")
        st.sidebar.number_input(
            "Rows to show",
            key="num_rows_preview_step1",
            value=10,
            min_value=1,
            step=1)
    # STEP 2
    if st.session_state.step1_done:
        st.sidebar.subheader("STEP 2 - REMOVE DUPLICATES")
        st.sidebar.selectbox(
        "Auto-removing duplicates",
        options=["YES", "NO"],
        index=0,
        key="auto_remove_duplicates",
        help="If YES, removes duplicated rows considering all colums",
        on_change=lambda: update_completion_state(1))
        st.sidebar.number_input(
            "Rows to show",
            key="num_rows_preview_step2",
            value=10,
            min_value=1,
            step=1)
    # STEP 3
    if st.session_state.step2_done:
        st.sidebar.subheader("STEP 3 - SELECT RELEVANT ATTRIBUTES")
        st.sidebar.number_input(
            "Rows to show",
            key="num_rows_preview_step3",
            value=10,
            min_value=1,
            step=1)
        
# -------------------------------
# STEP 0) LOAD RAW DATAFRAME
# -------------------------------
def show_content_step_0():
    # Title
    st.subheader("STEP 0) LOAD RAW DATAFRAME")

    # Read DataFrame
    data_path = get_data_path_from_command_line()
    if not data_path or not os.path.exists(data_path):
        st.error("❌ Here I should include an automatic loader.")
        st.stop()
    st.session_state.df = pd.read_csv(data_path, sep=st.session_state.get("data_separator", ","))

    # Copy current DataFrame
    df_raw = st.session_state.df.copy()

    # Display info
    st.write("###### 📏 Raw DataFrame SHAPE:", df_raw.shape)
    with st.expander("👀 Raw DataFrame PREVIEW"):
        st.dataframe(df_raw.head(10))
        st.dataframe(df_raw.tail(10))

    # Completion button
    set_completion_button(step_num=0, df=df_raw)

# -------------------------------
# STEP 1) EXPLORE DATAFRAME
# -------------------------------
def show_content_step_1():
    # Title
    st.subheader("STEP 1) EXPLORE DATAFRAME")

    # Copy current DataFrame
    df_S1 = st.session_state.df.copy()

    # Display info
    st.write("###### 📏 DataFrame SHAPE:", df_S1.shape)
    with st.expander("👀 DataFrame PREVIEW"):
        st.dataframe(df_S1.head(st.session_state.get("num_rows_preview_step1", 5)))
    with st.expander("ℹ️ DataFrame INFO"):
        st.dataframe(pd.DataFrame({
        "Column": df_S1.columns,
        "Non-Null Count": df_S1.notnull().sum(),
        "Dtype": df_S1.dtypes.astype(str)
    }))
    with st.expander("📊 DataFrame STATISTICS"):
        st.dataframe(df_S1.describe())

    # Completion button
    set_completion_button(step_num=1, df=df_S1)

# -------------------------------
# STEP 2) REMOVE DUPLICATES
# -------------------------------
def show_content_step_2():
    # Title
    st.subheader("STEP 2 - REMOVE DUPLICATES")

    # Copy current DataFrame
    df_S1 = st.session_state.df.copy()
    df_S2 = st.session_state.df.copy()

    # Calculate num of duplicates
    num_duplicates = df_S2.duplicated().sum()
    if num_duplicates == 0:
            st.success("✅ No duplicate rows found.")
    elif st.session_state.get("auto_remove_duplicates", "YES") == "YES":
        df_S2_duplicates = df_S2[df_S2.duplicated()]
        df_S2 = df_S2.drop_duplicates()
        st.warning(f"⚠️ Found {num_duplicates} duplicate rows that have been dropped.")

    # Display info
    col1, col2 = st.columns(2)
    with col1:
        st.write("###### 📏 Current DataFrame SHAPE:", df_S2.shape)
        with st.expander("👀 Current DataFrame PREVIEW"):
            st.dataframe(df_S2.head(st.session_state.get("num_rows_preview_step2", 5)))
        with st.expander("ℹ️ Current DataFrame INFO"):
            st.dataframe(pd.DataFrame({
            "Column": df_S2.columns,
            "Non-Null Count": df_S2.notnull().sum(),
            "Dtype": df_S2.dtypes.astype(str)
        }))
        with st.expander("📊 Current DataFrame STATISTICS"):
            st.dataframe(df_S2.describe())
    with col2:
        st.write("###### 📏 Previous DataFrame SHAPE:", df_S1.shape)
        with st.expander("👀 Previous DataFrame PREVIEW"):
            st.dataframe(df_S1.head(st.session_state.get("num_rows_preview_step2", 5)))
        with st.expander("ℹ️ Previous DataFrame INFO"):
            st.dataframe(pd.DataFrame({
            "Column": df_S1.columns,
            "Non-Null Count": df_S1.notnull().sum(),
            "Dtype": df_S1.dtypes.astype(str)
        }))
        with st.expander("📊 Previous DataFrame STATISTICS"):
            st.dataframe(df_S1.describe())
        
    # Completion button
    set_completion_button(step_num=2, df=df_S2)

# -------------------------------
# STEP 3) SELECT RELEVANT ATTRIBUTES
# -------------------------------
def show_content_step_3():
    # Title
    st.subheader("STEP 3 - SELECT RELEVANT ATTRIBUTES")

    # Copy current DataFrame
    df_S2 = st.session_state.df.copy()
    df_S3 = st.session_state.df.copy()
    
    # Drop non-relevant attributes
    with st.expander("✏️ Drop non-relevant attributes"):
        kept_cols = st.multiselect(
            "Select which attributes to keep:",
            options=df_S3.columns.tolist(),
            default=df_S3.columns.tolist(),  # start with all selected
            key="kept_cols_step3",
            on_change=lambda: update_completion_state(2))
        if not kept_cols:
            st.warning("Please select at least one column to continue.")
            return
 
     # Filter the DataFrame with selected columns
    df_S3 = df_S3[kept_cols]

    # Display info
    col1, col2 = st.columns(2)
    with col1:
        st.write("###### 📏 Current DataFrame SHAPE:", df_S3.shape)
        with st.expander("👀 Current DataFrame PREVIEW"):
            st.dataframe(df_S3.head(st.session_state.get("num_rows_preview_step4", 5)))
        with st.expander("ℹ️ Current DataFrame INFO"):
            st.dataframe(pd.DataFrame({
            "Column": df_S3.columns,
            "Non-Null Count": df_S3.notnull().sum(),
            "Dtype": df_S3.dtypes.astype(str)
        }))
        with st.expander("📊 Current DataFrame STATISTICS"):
            st.dataframe(df_S3.describe())
    with col2:
        st.write("###### 📏 Previous DataFrame SHAPE:", df_S2.shape)
        with st.expander("👀 Previous DataFrame PREVIEW"):
            st.dataframe(df_S2.head(st.session_state.get("num_rows_preview_step4", 5)))
        with st.expander("ℹ️ Previous DataFrame INFO"):
            st.dataframe(pd.DataFrame({
            "Column": df_S2.columns,
            "Non-Null Count": df_S2.notnull().sum(),
            "Dtype": df_S2.dtypes.astype(str)
        }))
        with st.expander("📊 Previous DataFrame STATISTICS"):
            st.dataframe(df_S2.describe())

    # Completion button
    set_completion_button(step_num=3, df=df_S3)

def show_content_step_4():
    # Title
    st.subheader("STEP 4 - CLASSIFY ATTRIBUTES AND TARGET VARIABLE")

    # Copy current DataFrame
    df_S3 = st.session_state.df.copy()
    df_S4 = st.session_state.df.copy()

    target_col = st.session_state.get("target_col_step4", None)

    with st.expander("✏️ Confirm type of variable for each attribute:"):
        col1, col2, col3, col4 = st.columns(4)
        with col1: st.markdown("**COLUMN NO.**")
        with col2: st.markdown("**ATTRIBUTE**")
        with col3: st.markdown("**VARIABLE TYPE**")
        with col4: st.markdown("**TARGET**")

        selected_target = None

        for column_name in df_S4.columns:
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.write(df_S4.columns.get_loc(column_name))
            with c2:
                st.write(column_name)
            with c3:
                st.selectbox(
                    "",
                    options=["CATEGORY", "NUMERIC"],
                    key=f"type_col_{column_name}",
                    label_visibility="collapsed",
                    on_change=lambda: update_completion_state(3))
            with c4:
                checked = st.checkbox(
                    "",
                    key=f"target_checkbox_{column_name}",
                    value=(column_name == target_col))
                if checked:
                    selected_target = column_name

        # Update session_state after creating all widgets
        if selected_target and selected_target != target_col:
            for other_col in df_S4.columns:
                if f"target_checkbox_{other_col}" in st.session_state:
                    st.session_state[f"target_checkbox_{other_col}"] = (other_col == selected_target)
            st.session_state["target_col_step4"] = selected_target
            update_completion_state(3)

    # Completion button
    set_completion_button(step_num=4, df=df_S4)

def show_content_step_5():
    # Title
    st.subheader("STEP 5 - UNIVARIABLE ANALYSIS")

# --------------------------------------------------------------
# MAIN APP LAYOUT
# --------------------------------------------------------------
def main():
    st.set_page_config(page_title="EDA - Guided Analysis", page_icon="📊", layout="wide")
    sticky_banner()
    set_default_inputs_for_init_session_state()
    sidebar_inputs()

    # Lista de funciones en orden de pasos
    step_functions = [
        show_content_step_0,
        show_content_step_1,
        show_content_step_2,
        show_content_step_3,
        show_content_step_4,
        show_content_step_5,
    ]

    # Bucle compacto para mostrar pasos secuenciales
    for i, show_step in enumerate(step_functions):
        # El primer paso siempre se muestra
        if i == 0 or st.session_state.get(f"step{i-1}_done", False):
            if i > 0:
                st.divider()
            show_step()

    st.markdown("---")
    st.caption("Dynamic EDA app with contextual inputs and sequential steps.")


# --------------------------------------------------------------
# RUN APP
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
