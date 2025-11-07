# ==============================================================
# 🧩 EDA APP - MULTI-STEP GUIDED EXPLORER WITH SIDEBAR INPUTS
# ==============================================================
# Each step only appears after clicking “Proceed to next step”.
# Buttons are centered and disabled until the step is complete.
# ==============================================================

import streamlit as st
import pandas as pd
import io, os, sys

def get_data_path_from_command_line() -> str: # Reads the dataset path passed as a command-line argument.
    if "--data-path" in sys.argv: # Check if the '--data-path' argument exists
        index = sys.argv.index("--data-path") # Find its position
        if index + 1 < len(sys.argv): # Ensure there is a value after it (the actual path)
            return sys.argv[index + 1]
    return "" # Default: no path was provided

# --------------------------------------------------------------
# Centralized state initialization
# --------------------------------------------------------------
def set_default_inputs_for_init_session_state():
    defaults = {
        "df": None,
        "step1_done": False,
        "step2_done": False,
        "step3_done": False,
        "step4_done": False,
        "step5_done": False,
        "step6_done": False,
        "step7_done": False,
        "step8_done": False,
        "step9_done": False,
        "step10_done": False,
        "last_used_separator": ",",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# Updates the completion status of steps in st.session_state
def update_completion_state(step: int):
    total_steps = 10  # adjust if you have more or fewer steps

    for i in range(1, total_steps + 1):
        st.session_state[f"step{i}_done"] = (i <= step)

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

def sticky_banner():
    """Fixed top banner showing progress."""
    # Dummy progress info for demo
    steps = [("✅" if st.session_state.get(f"step{i}_done", False) else "⏳") + f" Step {i}" for i in range(1, 11)]
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


# --------------------------------------------------------------
# STEP 1️⃣ - LOAD & EXPLORE DATAFRAME
# --------------------------------------------------------------
def show_content_step_1():
    # Title
    st.subheader("STEP 1 - LOAD RAW DATA")

    # Read DataFrame
    data_path = get_data_path_from_command_line()
    if not data_path or not os.path.exists(data_path):
        st.error("❌ Here I should include an automatic loader.")
        st.stop()
    st.session_state.df = pd.read_csv(data_path, sep=st.session_state.get("data_separator", ","))

    # Copy current DataFrame
    df_S1 = st.session_state.df.copy()

    # Display info
    st.write("###### 📏 Raw DataFrame SHAPE:", df_S1.shape)
    with st.expander("👀 Raw DataFrame PREVIEW"):
        st.dataframe(df_S1.head(10))
        st.dataframe(df_S1.tail(10))

    # Completion button
    st.button(
        "✅ STEP 1 COMPLETED!" if st.session_state.step1_done else "COMPLETE STEP 1 ➡️ PROCEED TO STEP 2",
        use_container_width=True,
        disabled=st.session_state.step1_done,
        on_click=lambda: (update_df(df_S1), update_completion_state(1)))
# --------------------------------------------------------------
# STEP 2 - EXPLORE DATAFRAME
# --------------------------------------------------------------
def show_content_step_2():
    # Title
    st.subheader("STEP 2 - EXPLORE DATAFRAME")

    # Copy current DataFrame
    df_S2 = st.session_state.df.copy()

    # Display info
    st.write("###### 📏 DataFrame SHAPE:", df_S2.shape)
    with st.expander("👀 DataFrame PREVIEW"):
        st.dataframe(df_S2.head(st.session_state.get("num_rows_preview_step2", 5)))
    with st.expander("ℹ️ DataFrame INFO"):
        st.dataframe(pd.DataFrame({
        "Column": df_S2.columns,
        "Non-Null Count": df_S2.notnull().sum(),
        "Dtype": df_S2.dtypes.astype(str)
    }))
    with st.expander("📊 DataFrame STATISTICS"):
        st.dataframe(df_S2.describe())

    # Completion button
    st.button(
        "✅ STEP 2 COMPLETED!" if st.session_state.step2_done else "COMPLETE STEP 2 ➡️ PROCEED TO STEP 3",
        use_container_width=True,
        disabled=st.session_state.step2_done,
        on_click=lambda: (update_df(df_S2), update_completion_state(2)))
# --------------------------------------------------------------
# STEP 3 - REMOVE DUPLICATES
# --------------------------------------------------------------
def show_content_step_3():
    # Title
    st.subheader("STEP 3 - REMOVE DUPLICATES")

    # Copy current DataFrame
    df_S2 = st.session_state.df.copy()
    df_S3 = st.session_state.df.copy()

    # Calculate num of duplicates
    num_duplicates = df_S3.duplicated().sum()
    if num_duplicates == 0:
            st.success("✅ No duplicate rows found.")
    elif st.session_state.get("auto_remove_duplicates", "YES") == "YES":
        df_S3_duplicates = df_S3[df_S3.duplicated()]
        df_S3 = df_S3.drop_duplicates()
        st.warning(f"⚠️ Found {num_duplicates} duplicate rows that have been dropped.")

    # Display info
    col1, col2 = st.columns(2)
    with col1:
        st.write("###### 📏 Current DataFrame SHAPE:", df_S3.shape)
        with st.expander("👀 Current DataFrame PREVIEW"):
            st.dataframe(df_S3.head(st.session_state.get("num_rows_preview_step3", 5)))
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
            st.dataframe(df_S2.head(st.session_state.get("num_rows_preview_step3", 5)))
        with st.expander("ℹ️ Previous DataFrame INFO"):
            st.dataframe(pd.DataFrame({
            "Column": df_S2.columns,
            "Non-Null Count": df_S2.notnull().sum(),
            "Dtype": df_S2.dtypes.astype(str)
        }))
        with st.expander("📊 Previous DataFrame STATISTICS"):
            st.dataframe(df_S2.describe())
        
    # Completion button
    st.button(
        "✅ STEP 3 COMPLETED!" if st.session_state.step3_done else "COMPLETE STEP 3 ➡️ PROCEED TO STEP 4",
        use_container_width=True,
        disabled=st.session_state.step3_done,
        on_click=lambda: (update_df(df_S3), update_completion_state(3)))

# --------------------------------------------------------------
# STEP 4 - SELECT & RENAME ATTRIBUTES
# --------------------------------------------------------------
def show_content_step_4():
    # Title
    st.subheader("STEP 4 - SELECT RELEVANT AND TARGET ATTRIBUTES")

    # Copy current DataFrame
    df_S3 = st.session_state.df.copy()
    df_S4 = st.session_state.df.copy()
    
    # Drop non-relevant attributes
    with st.expander("✏️ Drop non-relevant attributes"):
        kept_cols = st.multiselect(
            "Select which attributes to keep:",
            options=df_S4.columns.tolist(),
            default=df_S4.columns.tolist(),  # start with all selected
            key="kept_cols_step4")
        if not kept_cols:
            st.warning("Please select at least one column to continue.")
            return

    # Prevent dropping the target variable
    target_col_selected = st.session_state.get("target_col_step4", None)
    if target_col_selected and target_col_selected not in kept_cols:
        st.error(f"❌ The target variable '{target_col_selected}' cannot be dropped. Please include it among kept columns.")
        return
 
     # Filter the DataFrame with selected columns
    df_S4 = df_S4[kept_cols]

    # Get current target from session_state (if already chosen)
    current_target = st.session_state.get("target_col_step4", "None selected")
    if current_target == "None selected":
        current_target = "None selected ❌"
        button_disabled = True
        button_label = "❌ TARGET VARIABLE MUST BE SELECTED!"
        
    else:
        current_target = current_target + " ✅"
        button_disabled = st.session_state.step4_done
        if st.session_state.step4_done:
            button_label = "✅ STEP 4 COMPLETED!"
        else:
            button_label = "COMPLETE STEP 4 ➡️ PROCEED TO STEP 5"
    
    # Select target variable
    with st.expander(f"✏️ Select target variable: **{current_target}**"):
        target_col = st.selectbox(
            "Select the target column:",
            options=kept_cols,
            key="target_col_step4")

    # Display info
    col1, col2 = st.columns(2)
    with col1:
        st.write("###### 📏 Current DataFrame SHAPE:", df_S4.shape)
        with st.expander("👀 Current DataFrame PREVIEW"):
            if "target_col_step4" in st.session_state:
                target_col = st.session_state["target_col_step4"]
                # Apply background color to the target column
                def highlight_target(col):
                    color = "background-color: rgba(0,255,0,0.15)"
                    return [color if col.name == target_col else "" for _ in col]

                styled_df = df_S4.head(
                    st.session_state.get("num_rows_preview_step4", 5)
                ).style.apply(highlight_target, axis=0)
                st.dataframe(styled_df, use_container_width=True)
            else:
                st.dataframe(df_S4.head(st.session_state.get("num_rows_preview_step4", 5)))
        with st.expander("ℹ️ Current DataFrame INFO"):
            st.dataframe(pd.DataFrame({
            "Column": df_S4.columns,
            "Non-Null Count": df_S4.notnull().sum(),
            "Dtype": df_S4.dtypes.astype(str)
        }))
        with st.expander("📊 Current DataFrame STATISTICS"):
            st.dataframe(df_S4.describe())
    with col2:
        st.write("###### 📏 Previous DataFrame SHAPE:", df_S3.shape)
        with st.expander("👀 Previous DataFrame PREVIEW"):
            st.dataframe(df_S3.head(st.session_state.get("num_rows_preview_step4", 5)))
        with st.expander("ℹ️ Previous DataFrame INFO"):
            st.dataframe(pd.DataFrame({
            "Column": df_S3.columns,
            "Non-Null Count": df_S3.notnull().sum(),
            "Dtype": df_S3.dtypes.astype(str)
        }))
        with st.expander("📊 Previous DataFrame STATISTICS"):
            st.dataframe(df_S3.describe())

    # Completion button
    st.button(
        label = button_label,
        use_container_width=True,
        disabled=button_disabled,
        on_click=lambda: (update_df(df_S4), update_completion_state(4)))

def show_content_step_5():
    # Title
    st.subheader("STEP 5 - SELECT DATATYPES FOR ATTRIBUTES")

    # Copy current DataFrame
    df_S4 = st.session_state.df.copy()
    df_S5 = st.session_state.df.copy()
# --------------------------------------------------------------
# SIDEBAR CONFIGURATION PANEL (dynamic, unified reactivity)
# --------------------------------------------------------------
def sidebar_inputs():
    # Step 1 inputs
    st.sidebar.subheader("STEP 1 - LOAD RAW DATA")
    st.sidebar.selectbox(
        "Dataset separator",
        options=[",", ";"],
        index=1,
        key="data_separator",
        help="Character that separates data.",
        on_change=lambda: update_completion_state(0))
    # Step 2 inputs
    if st.session_state.step1_done:
        st.sidebar.subheader("STEP 2 - EXPLORE DATAFRAME")
        st.sidebar.number_input(
            "Rows to show",
            key="num_rows_preview_step2",
            value=10,
            min_value=1,
            step=1)
    # Step 3 inputs
    if st.session_state.step2_done:
        st.sidebar.subheader("STEP 3 - REMOVE DUPLICATES")
        st.sidebar.selectbox(
        "Auto-removing duplicates",
        options=["YES", "NO"],
        index=0,
        key="auto_remove_duplicates",
        help="If YES, removes duplicated rows considering all colums",
        on_change=lambda: update_completion_state(2))
        st.sidebar.number_input(
            "Rows to show",
            key="num_rows_preview_step3",
            value=10,
            min_value=1,
            step=1)
    # Step 4 inputs
    if st.session_state.step3_done:
        st.sidebar.subheader("STEP 4 - SELECT RELEVANT AND TARGET ATTRIBUTES")
        st.sidebar.number_input(
            "Rows to show",
            key="num_rows_preview_step4",
            value=10,
            min_value=1,
            step=1)


# --------------------------------------------------------------
# MAIN APP LAYOUT
# --------------------------------------------------------------
def main():
    st.set_page_config(page_title="EDA - Guided Analysis", page_icon="📊", layout="wide")
    sticky_banner()
    set_default_inputs_for_init_session_state()
    
    sidebar_inputs()
    
    show_content_step_1()

    if st.session_state.step1_done:
        st.divider()
        show_content_step_2()

    if st.session_state.step2_done:
        st.divider()
        show_content_step_3()
    
    if st.session_state.step3_done:
        st.divider()
        show_content_step_4()

    st.markdown("---")
    st.caption("Dynamic EDA app with contextual inputs and sequential steps.")


# --------------------------------------------------------------
# RUN APP
# --------------------------------------------------------------
if __name__ == "__main__":
    main()
