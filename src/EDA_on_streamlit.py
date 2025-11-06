"""
--------------------------------------------------------------
EDA APP - MULTI-STEP GUIDED EXPLORER WITH SIDEBAR INPUTS
--------------------------------------------------------------
Each step only appears after clicking “Proceed to next step”.
Inputs in the sidebar are reactive and refresh visible steps.
"""

import streamlit as st
import pandas as pd
import io, os, sys


# ==============================================================
# Utility to read dataset path from CLI
# ==============================================================
def _get_data_path_from_cli() -> str:
    if "--data-path" in sys.argv:
        i = sys.argv.index("--data-path")
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return ""


# ==============================================================
# Centralized state initialization
# ==============================================================
def _init_session_state():
    defaults = {
        "df": None,
        "step1_done": False,
        "step2_done": False,
        "step3_done": False,
        "show_step2": False,
        "show_step3": False,
        "sidebar_remove_dupes": True,
        "last_used_separator": ",",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ==============================================================
# STEP 1️⃣ - LOAD & EXPLORE DATAFRAME
# ==============================================================
def step_1_explore_dataframe():
    st.header("STEP 1️⃣ - EXPLORE RAW DATAFRAME")

    data_path = _get_data_path_from_cli()
    if not data_path:
        st.error("❌ No data path provided. Please run this app via main.py.")
        st.stop()
    if not os.path.exists(data_path):
        st.error(f"❌ File not found: `{data_path}`")
        st.stop()

    # --- Load or reload dataset whenever separator changes ---
    current_sep = st.session_state.get("data_separator", ",")
    last_sep = st.session_state.get("last_used_separator")

    if st.session_state.df is None or last_sep != current_sep:
        try:
            st.session_state.df = pd.read_csv(data_path, sep=current_sep)
            st.session_state.last_used_separator = current_sep
            st.info(f"📁 Dataset loaded from: `{data_path}` (separator: '{current_sep}')")
        except Exception as e:
            st.error(f"❌ Could not load dataset: {e}")
            st.stop()

    df = st.session_state.df

    # --- Basic info ---
    info_df = pd.DataFrame({
        "Column": df.columns,
        "Non-Null Count": df.notnull().sum(),
        "Dtype": df.dtypes.astype(str)
    })

    st.write("###### 📏 Raw DataFrame SHAPE:", df.shape)
    with st.expander("👀 Raw DataFrame PREVIEW"):
        st.dataframe(df.head(st.session_state.get("step1_num_rows_preview", 5)))
    with st.expander("ℹ️ Raw DataFrame INFO"):
        st.dataframe(info_df)
    with st.expander("📊 Descriptive statistics"):
        st.dataframe(df.describe())

    # Step complete + next step button
    st.session_state.step1_done = True
    st.session_state.step2_done = False
    st.session_state.step3_done = False
    st.success("✅ Step 1 completed.")
    if st.button("➡️ Proceed to Step 2"):
        st.session_state.show_step2 = True
    


# ==============================================================
# STEP 2️⃣ - FIND DUPLICATES
# ==============================================================
def step_2_find_duplicates():
    st.header("STEP 2️⃣ - Find Duplicates")
    st.info("Check and optionally remove duplicate rows.")

    df = st.session_state.df.copy()
    num_duplicates = df.duplicated().sum()

    if num_duplicates == 0:
        st.success("✅ No duplicate rows found.")
    else:
        st.warning(f"⚠️ Found {num_duplicates} duplicate rows.")
        if st.session_state.sidebar_remove_dupes:
            df = df.drop_duplicates()
            st.info("Duplicates removed.")

    st.session_state.df = df.copy()
    st.session_state.step2_done = True
    st.session_state.step3_done = False

    if st.button("➡️ Proceed to Step 3"):
        st.session_state.show_step3 = True
    st.success("✅ Step 2 completed.")


# ==============================================================
# STEP 3️⃣ - SELECT & RENAME ATTRIBUTES
# ==============================================================
def step_3_select_attributes():
    st.header("STEP 3️⃣ - Select and Rename Attributes")
    st.info("Choose which columns to keep, rename them, and pick the target variable.")

    df = st.session_state.df.copy()
    columns = df.columns.tolist()

    st.write("### ✏️ Column Configuration")
    st.caption("Decide which columns to keep, rename, and select the target variable.")

    keep_flags, new_names, target_choice = {}, {}, None
    col1, col2, col3 = st.columns([2, 3, 2])
    col1.write("**Keep?**"); col2.write("**New Name**"); col3.write("**Target?**")

    for col in columns:
        c1, c2, c3 = st.columns([2, 3, 2])
        keep_flags[col] = c1.checkbox("", value=True, key=f"keep_{col}")
        new_names[col] = c2.text_input("", value=col, key=f"name_{col}")
        if c3.radio("", ["No", "Yes"], index=0, key=f"target_{col}") == "Yes":
            target_choice = col

    if st.button("💾 Apply column configuration"):
        kept_cols = [c for c in columns if keep_flags[c]]
        df = df[kept_cols].rename(columns=new_names)
        st.session_state.df = df.copy()
        st.session_state.target_col = target_choice
        st.session_state.step3_done = True
        st.success(f"✅ Step 3 completed. Selected target variable: `{target_choice}`")
        st.subheader("🧾 Resulting DataFrame")
        st.dataframe(df.head())


# ==============================================================
# SIDEBAR CONFIGURATION PANEL (dynamic, unified reactivity)
# ==============================================================
def sidebar_inputs():
    st.sidebar.title("⚙️ Input Panel")

    # Always visible
    st.sidebar.subheader("Step 1️⃣ - EXPLORE RAW DATASET")
    st.sidebar.selectbox(
        "Dataset separator",
        options=[",", ";"],
        index=1,
        key="data_separator",
        help="Character that separates data."
    )
    st.sidebar.number_input(
        "Number of rows to show",
        key="step1_num_rows_preview",
        value=10,
        min_value=1,
        step=1
    )
    st.sidebar.caption("The dataset is preloaded from main.py")

    # Step 2 inputs appear only when Step 2 is unlocked
    if st.session_state.show_step2:
        st.sidebar.subheader("Step 2️⃣ - Duplicate Handling")
        data_path = _get_data_path_from_cli()
        st.sidebar.text_input("Dataset Path (read-only)", data_path, disabled=True)
        st.session_state.sidebar_remove_dupes = st.sidebar.checkbox(
            "Remove duplicate rows automatically",
            value=st.session_state.sidebar_remove_dupes
        )

    # Step 3 inputs appear only when Step 3 is unlocked
    if st.session_state.show_step3:
        st.sidebar.subheader("Step 3️⃣ - Column Settings")
        st.sidebar.selectbox(
            "Default rename prefix (optional)",
            options=["", "col_", "feature_"],
            key="rename_prefix"
        )
        st.sidebar.text_input(
            "Custom note for Step 3",
            key="step3_note",
            placeholder="(Optional) Add notes here..."
        )

    st.sidebar.markdown("---")
    st.sidebar.caption("Changes in sidebar inputs automatically refresh visible steps.")


# ==============================================================
# MAIN APP LAYOUT
# ==============================================================
def main():
    st.set_page_config(page_title="EDA - Guided Analysis", page_icon="📊")
    _init_session_state()

    # Sidebar always on left
    sidebar_inputs()

    # Main content
    st.markdown("## 🧩 Guided EDA Workflow")
    st.caption("Complete each step and click 'Proceed to next step' to unlock the next one.")

    st.divider()
    step_1_explore_dataframe()

    # Show Step 2 only after Step 1 complete and user clicked Proceed
    if st.session_state.show_step2:
        st.divider()
        step_2_find_duplicates()

    # Show Step 3 only after Step 2 complete and user clicked Proceed
    if st.session_state.show_step3:
        st.divider()
        step_3_select_attributes()

    st.markdown("---")
    st.caption("Dynamic EDA app with contextual inputs and sequential steps.")


# Run Streamlit app
main()
