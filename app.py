import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px

# Import calculation engine from your renamed calibration_engine.py
from calibration_engine import UniversalCalibrationEngine, UncertaintyComponent, Distribution

# --- Page Setup ---
st.set_page_config(page_title="Measurement Uncertainty Dashboard", page_icon="⚖️️", layout="wide")
st.title("⚖️ Universal Measurement Uncertainty Dashboard")
st.caption("Powered by calibration_engine.py (GUM / ISO/IEC Guide 98-3 Compliant)")

# --- Sidebar Inputs ---
st.sidebar.header("1. Calibration Setup")

param_options = ["Temperature", "Pressure", "Mass / Weight", "Voltage / Electrical", "Custom Parameter"]
selected_param = st.sidebar.selectbox("Select Parameter", param_options)

default_units = {
    "Temperature": "°C",
    "Pressure": "bar",
    "Mass / Weight": "kg",
    "Voltage / Electrical": "V",
    "Custom Parameter": "units"
}

unit = st.sidebar.text_input("Measurement Unit", value=default_units[selected_param])
coverage_factor_k = st.sidebar.number_input("Coverage Factor (k)", min_value=1.0, max_value=5.0, value=2.0, step=0.1)

# Preset Button: Load 100°C Example from Handwritten Notes
if st.sidebar.button("📋 Load Handwritten Notes Example (100 °C)"):
    st.session_state["ref_readings"] = [100.1, 100.0, 100.2, 100.1, 100.1]
    st.session_state["uut_readings"] = [101.0, 101.0, 101.1, 101.0, 101.0]
    st.session_state["type_b_preset"] = True
    st.rerun()

# --- Main Dashboard ---
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("2. Type A Repeatability Data")
    
    default_ref = st.session_state.get("ref_readings", [100.1, 100.0, 100.2, 100.1, 100.1])
    default_uut = st.session_state.get("uut_readings", [101.0, 101.0, 101.1, 101.0, 101.0])

    df_input = st.data_editor(
        pd.DataFrame({"Reference Standard": default_ref, "Unit Under Test (UUT)": default_uut}),
        num_rows="dynamic",
        use_container_width=True
    )

    ref_vals = df_input["Reference Standard"].dropna().tolist()
    uut_vals = df_input["Unit Under Test (UUT)"].dropna().tolist()

with col_right:
    st.subheader("3. Type B Uncertainty Sources")

    is_preset = st.session_state.get("type_b_preset", False)
    
    ref_std_val = st.number_input(f"Reference Standard Unc ({unit})", value=0.05 if is_preset else 0.01, format="%.4f")
    ref_std_k = st.number_input("Ref Standard k-factor", value=2.0)
    uut_res_val = st.number_input(f"UUT Resolution ({unit})", value=0.1 if is_preset else 0.01, format="%.4f")
    stab_val = st.number_input(f"Stability Limit ({unit})", value=0.05 if is_preset else 0.00, format="%.4f")
    uni_val = st.number_input(f"Uniformity / Drift ({unit})", value=0.10 if is_preset else 0.00, format="%.4f")

# --- Execute Calculations via Python Engine ---
if len(ref_vals) >= 2 and len(ref_vals) == len(uut_vals):
    # Initialize engine from calibration_engine.py
    engine = UniversalCalibrationEngine(parameter_name=selected_param, unit=unit)

    # 1. Process Type A
    stats = engine.process_repeatability_type_a(uut_readings=uut_vals, ref_readings=ref_vals)

    # 2. Process Type B
    engine.add_component(UncertaintyComponent("Reference Standard", ref_std_val, Distribution.NORMAL, k_factor=ref_std_k))
    engine.add_component(UncertaintyComponent("UUT Resolution", uut_res_val / np.sqrt(4), Distribution.RECTANGULAR))
    
    if stab_val > 0:
        engine.add_component(UncertaintyComponent("Stability", stab_val, Distribution.RECTANGULAR))
    if uni_val > 0:
        engine.add_component(UncertaintyComponent("Uniformity", uni_val, Distribution.RECTANGULAR))

    # 3. Calculate Budget
    budget_results = engine.calculate_budget(coverage_factor=coverage_factor_k)

    # --- Display Summary Table & Visuals ---
    st.markdown("---")
    st.subheader("4. Combined Uncertainty Budget Table")

    table_rows = []
    for comp in engine.components:
        table_rows.append({
            "Source": comp.name,
            "Distribution": comp.distribution.value,
            "Standard Uncertainty (u_i)": comp.standard_uncertainty,
            "Variance (u_i²)": comp.standard_uncertainty ** 2
        })

    df_budget = pd.DataFrame(table_rows)
    st.dataframe(df_budget.style.format({
        "Standard Uncertainty (u_i)": "{:.6f}",
        "Variance (u_i²)": "{:.8f}"
    }), use_container_width=True)

    # Key Performance Metric Cards
    c1, c2, c3 = st.columns(3)
    c1.metric(f"Mean Error ({unit})", f"{engine.mean_error:+.4f}")
    c2.metric(f"Combined Std Unc u_c ({unit})", f"{budget_results['combined_standard_uncertainty']:.6f}")
    c3.metric(f"Expanded Uncertainty U (k={coverage_factor_k:g})", f"±{budget_results['expanded_uncertainty']:.4f}")

    # Pareto Chart
    fig = px.pie(
        df_budget, 
        values="Variance (u_i²)", 
        names="Source", 
        title=f"Uncertainty Component Contribution ({selected_param})",
        hole=0.4
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("Please enter at least 2 complete pairs of Reference Standard and UUT readings.")