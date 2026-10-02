# ⚖️ Universal Measurement Uncertainty Dashboard

An **ISO/IEC 17025** and **ISO/IEC Guide 98-3 (GUM)** compliant measurement uncertainty calculator and calibration dashboard. Built using **Python**, **Streamlit**, and **Plotly**.

## 📌 Features

* **Universal Parameter Support**: Performs calibration calculations for Temperature, Pressure, Mass, Voltage, Flow Rate, or any custom unit.

* **Type A Evaluation**: Automatically processes repeated measurement series to evaluate standard error of the mean ($u_A$) and sample standard deviation ($S$).

* **Type B Budget Manager**: Supports Normal, Rectangular ($\sqrt{3}$), Digital Resolution ($\sqrt{12}$), U-Shaped ($\sqrt{2}$), and Triangular ($\sqrt{6}$) probability distributions.

* **Root-Sum-of-Squares (RSS) Engine**: Computes combined standard uncertainty ($u_c$) and expanded uncertainty ($U$) using customizable coverage factors ($k = 1.0, 2.0, 3.0$).

* **Visual Pareto Analysis**: Interactive Plotly variance contribution donut charts.

* **Theme Switching**: Built-in Dark Mode 🌙 and Light Mode ☀️ toggle with dynamic styling.

* **Handwritten Notes Preset**: One-click preset loader to reproduce sample calibration worksheets.

## 📁 Repository Structure

```
calibration_uncertainty/
├── calibration_engine.py   # Core GUM calculation engine & dataclasses
├── app.py                  # Streamlit UI Dashboard & visualization script
├── README.md               # Project documentation
└── requirements.txt        # Python package dependencies

```

## 🚀 Quick Start & Installation

### 1. Prerequisites

Ensure you have **Python 3.8+** installed on your system.

### 2. Clone the Repository

```
git clone https://github.com/your-username/calibration-uncertainty-dashboard.git
cd calibration-uncertainty-dashboard

```

### 3. Install Dependencies

```
pip install -r requirements.txt

```

*(Or manually install: `pip install streamlit numpy pandas plotly`)*

### 4. Run the Streamlit Dashboard

```
python -m streamlit run app.py

```

## 📊 Standard Uncertainty Formulas (GUM Standards)

1. **Mean Measurement Error (**$\bar{E}$**):**
   

   $$
   \bar{E} = \frac{1}{n} \sum_{i=1}^{n} (x_{\text{UUT}, i} - x_{\text{Ref}, i})
   $$

2. **Type A Uncertainty (**$u_A$**):**
   

   $$
   u_A = \frac{S}{\sqrt{n}}
   $$

3. **Combined Standard Uncertainty (**$u_c$**):**
   

   $$
   u_c = \sqrt{u_A^2 + u_{\text{ref}}^2 + u_{\text{res}}^2 + u_{\text{stab}}^2 + u_{\text{uni}}^2}
   $$

4. **Expanded Uncertainty (**$U$**):**
   

   $$
   U = k \times u_c \quad (k = 2.0 \text{ for } \approx 95\% \text{ confidence})
   $$

## 📜 License

Distributed under the **MIT License**. Free for academic, personal, and commercial calibration laboratory use.