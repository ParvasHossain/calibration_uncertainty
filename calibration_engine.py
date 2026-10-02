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
        """Adds a Type B or custom uncertainty component to the budget."""
        self.components.append(component)

    def process_repeatability_type_a(
        self, 
        uut_readings: List[float], 
        ref_readings: List[float]
    ) -> Dict[str, float]:
        """Calculates Type A repeatability uncertainty from paired readings."""
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
        """Calculates combined standard uncertainty (u_c) and expanded uncertainty (U)."""
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