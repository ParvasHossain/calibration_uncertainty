# ⚖️ Universal Measurement Uncertainty Dashboard

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B?logo=streamlit&logoColor=white)
![Compliance](https://img.shields.io/badge/Standard-ISO%2FIEC%2017025-green)
![GUM Compliant](https://img.shields.io/badge/Math-ISO%2FIEC%20Guide%2098--3-orange)

An **ISO/IEC 17025** and **ISO/IEC Guide 98-3 (GUM)** compliant measurement uncertainty engine and interactive calibration dashboard built with Python, Streamlit, and Plotly.

---

## 📌 Project Overview

This application provides a universal, parameter-agnostic engine for evaluating measurement uncertainty across **Temperature, Pressure, Mass, Voltage, Flow Rate**, or any custom industrial calibration parameter. It automates:
* **Type A Uncertainty Evaluation:** Sample standard deviation & standard error from repeated readings.
* **Type B Uncertainty Evaluation:** Probability distributions (Normal, Rectangular, U-Shaped, Triangular).
* **Root-Sum-of-Squares (RSS) Engine:** Combined standard uncertainty ($u_c$) and expanded uncertainty ($U$).
* **Pareto Variance Breakdown:** Interactive visualization of uncertainty source contributions.

---

## 📊 Mathematical Foundations (GUM Standards)

### 1. Mean Measurement Error ($\bar{E}$)
$$\bar{E} = \frac{1}{n} \sum_{i=1}^{n} (x_{\text{UUT},i} - x_{\text{Ref},i})$$

### 2. Type A Standard Uncertainty ($u_A$)
$$u_A = \frac{S}{\sqrt{n}}$$

### 3. Combined Standard Uncertainty ($u_c$)
$$u_c = \sqrt{u_A^2 + u_{\text{ref}}^2 + u_{\text{res}}^2 + u_{\text{stab}}^2 + u_{\text{uni}}^2}$$

### 4. Expanded Uncertainty ($U$)
$$U = k \times u_c \quad (k = 2.0 \text{ for } \approx 95\% \text{ confidence})$$

---

## 📁 Repository Structure

```text
calibration_uncertainty/
│
├── calibration_engine.py   # Core GUM calculation logic
├── app.py                 # Streamlit interactive UI dashboard
├── README.md              # Project documentation
└── requirements.txt        # Dependencies