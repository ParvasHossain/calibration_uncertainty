import sys
import numpy as np
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional


class Distribution(Enum):
    NORMAL = "normal"
    RECTANGULAR = "rectangular"
    U_SHAPED = "u_shaped"
    TRIANGULAR = "triangular"


@dataclass
class UncertaintyComponent:
    """Represents an individual source of uncertainty."""
    name: str
    value: float
    distribution: Distribution = Distribution.RECTANGULAR
    k_factor: Optional[float] = None
    sensitivity_coefficient: float = 1.0

    @property
    def standard_uncertainty(self) -> float:
        """Calculates standard uncertainty (u_i) based on probability distribution."""
        if self.distribution == Distribution.NORMAL:
            if not self.k_factor or self.k_factor <= 0:
                raise ValueError(f"Normal distribution for '{self.name}' requires a positive k_factor.")
            base_u = self.value / self.k_factor
        elif self.distribution == Distribution.RECTANGULAR:
            base_u = self.value / np.sqrt(3)
        elif self.distribution == Distribution.U_SHAPED:
            base_u = self.value / np.sqrt(2)
        elif self.distribution == Distribution.TRIANGULAR:
            base_u = self.value / np.sqrt(6)
        else:
            raise ValueError(f"Unsupported distribution type: {self.distribution}")

        return abs(self.sensitivity_coefficient) * base_u


class UniversalCalibrationEngine:
    """Universal Calibration Uncertainty Calculator compliant with GUM (ISO/IEC Guide 98-3)."""

    def __init__(self, parameter_name: str, unit: str):
        self.parameter_name = parameter_name
        self.unit = unit
        self.components: List[UncertaintyComponent] = []
        self.mean_error: float = 0.0

    def add_component(self, component: UncertaintyComponent) -> None:
        self.components.append(component)

    def process_repeatability_type_a(
        self, 
        uut_readings: List[float], 
        ref_readings: List[float]
    ) -> Dict[str, float]:
        """Calculates Type A uncertainty from repeated measurement pairs."""
        uut = np.array(uut_readings, dtype=float)
        ref = np.array(ref_readings, dtype=float)

        if len(uut) != len(ref):
            raise ValueError("UUT and Reference reading counts must match.")
        if len(uut) < 2:
            raise ValueError("At least 2 readings are required to calculate standard deviation.")

        errors = uut - ref
        n = len(errors)
        self.mean_error = float(np.mean(errors))
        sample_std = float(np.std(errors, ddof=1))
        type_a_std_u = sample_std / np.sqrt(n)

        type_a_comp = UncertaintyComponent(
            name="Repeatability (Type A)",
            value=type_a_std_u,
            distribution=Distribution.NORMAL,
            k_factor=1.0
        )
        self.components.append(type_a_comp)

        return {
            "mean_error": self.mean_error,
            "sample_std": sample_std,
            "type_a_uncertainty": type_a_std_u,
            "n_samples": n
        }

    def calculate_budget(self, coverage_factor: float = 2.0) -> Dict[str, float]:
        if not self.components:
            raise ValueError("No uncertainty components provided.")

        variance_sum = sum(comp.standard_uncertainty ** 2 for comp in self.components)
        combined_u = np.sqrt(variance_sum)
        expanded_u = coverage_factor * combined_u

        return {
            "combined_standard_uncertainty": combined_u,
            "coverage_factor": coverage_factor,
            "expanded_uncertainty": expanded_u
        }

    def print_budget_table(self, coverage_factor: float = 2.0) -> None:
        results = self.calculate_budget(coverage_factor=coverage_factor)

        print(f"\n" + "=" * 75)
        print(f" UNCERTAINTY BUDGET: {self.parameter_name.upper()} ({self.unit})")
        print("=" * 75)
        print(f"{'Source':<30} | {'Distribution':<12} | {'Divisor':<8} | {'Std Unc (' + self.unit + ')':<12}")
        print("-" * 75)

        for c in self.components:
            if c.distribution == Distribution.NORMAL:
                divisor_str = f"k={c.k_factor:g}"
            elif c.distribution == Distribution.RECTANGULAR:
                divisor_str = "√12 (res)" if "Resolution" in c.name else "√3"
            elif c.distribution == Distribution.U_SHAPED:
                divisor_str = "√2"
            elif c.distribution == Distribution.TRIANGULAR:
                divisor_str = "√6"
            else:
                divisor_str = "-"

            print(f"{c.name:<30} | {c.distribution.value:<12} | {divisor_str:<8} | {c.standard_uncertainty:.6f}")

        print("-" * 75)
        print(f"Mean Error (E):                      {self.mean_error:+.4f} {self.unit}")
        print(f"Combined Standard Uncertainty (u_c): {results['combined_standard_uncertainty']:.6f} {self.unit}")
        print(f"Expanded Uncertainty (U, k={coverage_factor:g}):      ±{results['expanded_uncertainty']:.4f} {self.unit}")
        print("-" * 75)
        print(f"FINAL REPORTED ERROR: {self.mean_error:+.2f} {self.unit} ± {results['expanded_uncertainty']:.2f} {self.unit} (k={coverage_factor:g})")
        print("=" * 75 + "\n")


# Helper Functions for CLI Input Handling

def prompt_float(prompt_text: str) -> float:
    while True:
        try:
            return float(input(prompt_text))
        except ValueError:
            print("Invalid input! Please enter a valid numerical value.")


def prompt_int(prompt_text: str) -> int:
    while True:
        try:
            return int(input(prompt_text))
        except ValueError:
            print("Invalid input! Please enter a valid integer.")


def choose_distribution() -> Distribution:
    print("\nSelect Distribution Type:")
    print("  1. Normal (Gaussian / Expanded Uncertainty)")
    print("  2. Rectangular (Uniform)")
    print("  3. U-Shaped (e.g., Sine wave / RF ripple)")
    print("  4. Triangular")
    
    choice = input("Enter choice (1-4, default=2): ").strip()
    mapping = {
        "1": Distribution.NORMAL,
        "2": Distribution.RECTANGULAR,
        "3": Distribution.U_SHAPED,
        "4": Distribution.TRIANGULAR
    }
    return mapping.get(choice, Distribution.RECTANGULAR)


def main():
    print("=========================================================")
    print("   UNIVERSAL MEASUREMENT UNCERTAINTY CALCULATOR (GUM)   ")
    print("=========================================================\n")

    # 1. Parameter Selection
    print("Select Calibration Parameter:")
    print("  1. Temperature (°C)")
    print("  2. Pressure (bar / psi / kPa)")
    print("  3. Mass / Weight (kg / g)")
    print("  4. Voltage (V / mV)")
    print("  5. Custom Parameter")
    
    param_choice = input("Choice (1-5): ").strip()
    
    if param_choice == "1":
        param_name, unit = "Temperature", "°C"
    elif param_choice == "2":
        param_name = "Pressure"
        unit = input("Enter Pressure Unit (e.g., bar, psi, kPa): ").strip() or "bar"
    elif param_choice == "3":
        param_name = "Mass"
        unit = input("Enter Mass Unit (e.g., kg, g): ").strip() or "kg"
    elif param_choice == "4":
        param_name = "Voltage"
        unit = input("Enter Voltage Unit (e.g., V, mV): ").strip() or "V"
    else:
        param_name = input("Enter Parameter Name: ").strip() or "Parameter"
        unit = input("Enter Measurement Unit: ").strip() or "units"

    engine = UniversalCalibrationEngine(parameter_name=param_name, unit=unit)

    # 2. Type A Calibration Readings
    print(f"\n--- 1. Enter Calibration Readings ({unit}) ---")
    num_readings = prompt_int("How many repeated readings/samples? ")
    
    ref_readings = []
    uut_readings = []
    
    print("\nEnter individual paired values:")
    for i in range(1, num_readings + 1):
        print(f"\nReading {i}:")
        ref_val = prompt_float(f"  Reference Standard ({unit}): ")
        uut_val = prompt_float(f"  Unit Under Test (UUT) ({unit}): ")
        ref_readings.append(ref_val)
        uut_readings.append(uut_val)

    stats = engine.process_repeatability_type_a(uut_readings, ref_readings)
    print(f"\nCalculated Mean Error: {stats['mean_error']:+.4f} {unit}")
    print(f"Calculated Type A Uncertainty (u_A): {stats['type_a_uncertainty']:.6f} {unit}")

    # 3. Type B Uncertainty Components
    print(f"\n--- 2. Enter Type B Uncertainty Sources ---")
    
    # Standard Reference
    ref_unc_val = prompt_float(f"Reference Standard Expanded Uncertainty ({unit}): ")
    ref_k = prompt_float("Reference Standard Coverage Factor k (e.g., 2.0): ")
    engine.add_component(UncertaintyComponent(
        name="Reference Standard",
        value=ref_unc_val,
        distribution=Distribution.NORMAL,
        k_factor=ref_k
    ))

    # Resolution
    resolution = prompt_float(f"UUT Digital Resolution/Least Count ({unit}): ")
    engine.add_component(UncertaintyComponent(
        name="UUT Resolution",
        value=resolution / np.sqrt(4),  # Standardized for d / sqrt(12)
        distribution=Distribution.RECTANGULAR
    ))

    # Additional Custom Components (e.g., Stability, Uniformity, Drift)
    while True:
        add_more = input("\nAdd additional Type B component (e.g., Stability, Drift, Environmental)? (y/n): ").strip().lower()
        if add_more != 'y':
            break

        comp_name = input("  Component Name: ").strip() or "Other Source"
        comp_val = prompt_float(f"  Uncertainty Value ({unit}): ")
        dist = choose_distribution()
        
        k_fact = None
        if dist == Distribution.NORMAL:
            k_fact = prompt_float("  Coverage factor k (e.g., 2.0): ")

        engine.add_component(UncertaintyComponent(
            name=comp_name,
            value=comp_val,
            distribution=dist,
            k_factor=k_fact
        ))

    # 4. Final Expanded Uncertainty Calculation
    cov_factor = prompt_float("\nTarget Coverage Factor k for Expanded Uncertainty (default = 2.0): ") or 2.0
    engine.print_budget_table(coverage_factor=cov_factor)


if __name__ == "__main__":
    main()