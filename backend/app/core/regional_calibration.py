"""
Antigravity – Regional Calibration System
Country-specific economic parameters for realistic simulation grounding.
Uses open data from World Bank, OECD, BLS, etc.
"""

import numpy as np
from pydantic import BaseModel, Field
from typing import Optional


class TaxModel(BaseModel):
    """Simplified progressive tax brackets."""
    brackets: list[tuple[float, float]]  # (income_threshold, rate)
    
    def effective_rate(self, income: float) -> float:
        """Compute effective tax rate for given income."""
        tax = 0.0
        prev = 0.0
        for threshold, rate in self.brackets:
            taxable = min(income, threshold) - prev
            if taxable > 0:
                tax += taxable * rate
            prev = threshold
            if income <= threshold:
                break
        if income > self.brackets[-1][0]:
            tax += (income - self.brackets[-1][0]) * self.brackets[-1][1]
        return tax / max(income, 1)


class HealthcareModel(BaseModel):
    """Healthcare cost and access model."""
    out_of_pocket_ratio: float         # Fraction of healthcare costs paid OOP
    insurance_coverage: float          # Population coverage rate (0–1)
    cost_income_ratio: float           # Annual healthcare cost / median income
    quality_index: float               # 0–1 quality score


class EducationROI(BaseModel):
    """Return on education investment by level."""
    bachelors_premium: float           # Salary premium vs high school
    masters_premium: float             # vs bachelors
    phd_premium: float                 # vs masters
    avg_student_debt: float            # In local currency
    years_to_roi: float                # Years until education pays for itself


class LaborMarket(BaseModel):
    """Labor market characteristics."""
    unemployment_rate: float
    median_income: float               # Annual, local currency
    income_gini: float                 # Inequality coefficient (0–1)
    startup_success_rate: float        # 5-year survival rate
    job_switch_frequency: float        # Average switches per decade
    remote_work_rate: float


class CostOfLiving(BaseModel):
    """Cost of living parameters."""
    housing_income_ratio: float        # Median housing cost / median income
    food_income_ratio: float
    transport_income_ratio: float
    ppp_factor: float                  # Purchasing power parity vs USD


class QualityOfLife(BaseModel):
    """Quality of life indices."""
    safety_index: float                # 0–1
    work_life_balance: float           # 0–1
    social_mobility: float             # 0–1
    healthcare_access: float           # 0–1
    environmental_quality: float       # 0–1


class RegionalProfile(BaseModel):
    """Complete regional calibration profile for a country."""
    country_code: str
    country_name: str
    currency: str
    tax: TaxModel
    healthcare: HealthcareModel
    education: EducationROI
    labor: LaborMarket
    cost_of_living: CostOfLiving
    quality_of_life: QualityOfLife
    
    # Simulation adjustments
    income_volatility_multiplier: float = 1.0
    stress_baseline_adjustment: float = 0.0
    health_decay_multiplier: float = 1.0
    relationship_stability_factor: float = 1.0


# ── Regional Profiles Database ───────────────────────────────

REGIONAL_PROFILES: dict[str, RegionalProfile] = {
    "US": RegionalProfile(
        country_code="US",
        country_name="United States",
        currency="USD",
        tax=TaxModel(brackets=[
            (11000, 0.10), (44725, 0.12), (95375, 0.22),
            (182100, 0.24), (231250, 0.32), (578125, 0.35), (1e9, 0.37),
        ]),
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.28, insurance_coverage=0.91,
            cost_income_ratio=0.18, quality_index=0.75,
        ),
        education=EducationROI(
            bachelors_premium=0.65, masters_premium=0.20,
            phd_premium=0.15, avg_student_debt=37000, years_to_roi=8,
        ),
        labor=LaborMarket(
            unemployment_rate=0.038, median_income=59400,
            income_gini=0.39, startup_success_rate=0.10,
            job_switch_frequency=4.0, remote_work_rate=0.28,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.33, food_income_ratio=0.10,
            transport_income_ratio=0.16, ppp_factor=1.0,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.55, work_life_balance=0.45,
            social_mobility=0.50, healthcare_access=0.70,
            environmental_quality=0.65,
        ),
        income_volatility_multiplier=1.15,
        stress_baseline_adjustment=0.05,
    ),
    
    "IN": RegionalProfile(
        country_code="IN",
        country_name="India",
        currency="INR",
        tax=TaxModel(brackets=[
            (300000, 0.0), (600000, 0.05), (900000, 0.10),
            (1200000, 0.15), (1500000, 0.20), (1e9, 0.30),
        ]),
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.55, insurance_coverage=0.40,
            cost_income_ratio=0.04, quality_index=0.45,
        ),
        education=EducationROI(
            bachelors_premium=0.80, masters_premium=0.35,
            phd_premium=0.20, avg_student_debt=500000, years_to_roi=5,
        ),
        labor=LaborMarket(
            unemployment_rate=0.075, median_income=600000,
            income_gini=0.35, startup_success_rate=0.05,
            job_switch_frequency=3.5, remote_work_rate=0.15,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.25, food_income_ratio=0.30,
            transport_income_ratio=0.10, ppp_factor=0.25,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.40, work_life_balance=0.35,
            social_mobility=0.35, healthcare_access=0.40,
            environmental_quality=0.35,
        ),
        income_volatility_multiplier=1.3,
        stress_baseline_adjustment=0.08,
        health_decay_multiplier=1.1,
        relationship_stability_factor=1.15,
    ),
    
    "DE": RegionalProfile(
        country_code="DE",
        country_name="Germany",
        currency="EUR",
        tax=TaxModel(brackets=[
            (10908, 0.0), (15999, 0.14), (62809, 0.24),
            (277825, 0.42), (1e9, 0.45),
        ]),
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.12, insurance_coverage=0.99,
            cost_income_ratio=0.11, quality_index=0.85,
        ),
        education=EducationROI(
            bachelors_premium=0.50, masters_premium=0.25,
            phd_premium=0.20, avg_student_debt=5000, years_to_roi=3,
        ),
        labor=LaborMarket(
            unemployment_rate=0.032, median_income=44000,
            income_gini=0.30, startup_success_rate=0.08,
            job_switch_frequency=2.5, remote_work_rate=0.22,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.28, food_income_ratio=0.12,
            transport_income_ratio=0.12, ppp_factor=0.85,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.80, work_life_balance=0.70,
            social_mobility=0.55, healthcare_access=0.95,
            environmental_quality=0.80,
        ),
        stress_baseline_adjustment=-0.05,
        health_decay_multiplier=0.85,
    ),
    
    "GB": RegionalProfile(
        country_code="GB",
        country_name="United Kingdom",
        currency="GBP",
        tax=TaxModel(brackets=[
            (12570, 0.0), (50270, 0.20), (125140, 0.40), (1e9, 0.45),
        ]),
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.09, insurance_coverage=0.99,
            cost_income_ratio=0.10, quality_index=0.78,
        ),
        education=EducationROI(
            bachelors_premium=0.55, masters_premium=0.18,
            phd_premium=0.12, avg_student_debt=45000, years_to_roi=10,
        ),
        labor=LaborMarket(
            unemployment_rate=0.042, median_income=34000,
            income_gini=0.35, startup_success_rate=0.09,
            job_switch_frequency=3.5, remote_work_rate=0.25,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.35, food_income_ratio=0.11,
            transport_income_ratio=0.14, ppp_factor=1.1,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.70, work_life_balance=0.55,
            social_mobility=0.45, healthcare_access=0.90,
            environmental_quality=0.75,
        ),
    ),
    
    "CA": RegionalProfile(
        country_code="CA",
        country_name="Canada",
        currency="CAD",
        tax=TaxModel(brackets=[
            (55867, 0.15), (111733, 0.205), (154906, 0.26),
            (220000, 0.29), (1e9, 0.33),
        ]),
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.14, insurance_coverage=0.99,
            cost_income_ratio=0.11, quality_index=0.80,
        ),
        education=EducationROI(
            bachelors_premium=0.55, masters_premium=0.22,
            phd_premium=0.15, avg_student_debt=28000, years_to_roi=7,
        ),
        labor=LaborMarket(
            unemployment_rate=0.055, median_income=54600,
            income_gini=0.32, startup_success_rate=0.09,
            job_switch_frequency=3.0, remote_work_rate=0.24,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.30, food_income_ratio=0.11,
            transport_income_ratio=0.14, ppp_factor=0.78,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.78, work_life_balance=0.65,
            social_mobility=0.55, healthcare_access=0.92,
            environmental_quality=0.85,
        ),
        stress_baseline_adjustment=-0.03,
    ),
    
    "AU": RegionalProfile(
        country_code="AU",
        country_name="Australia",
        currency="AUD",
        tax=TaxModel(brackets=[
            (18200, 0.0), (45000, 0.19), (120000, 0.325),
            (180000, 0.37), (1e9, 0.45),
        ]),
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.18, insurance_coverage=0.97,
            cost_income_ratio=0.10, quality_index=0.82,
        ),
        education=EducationROI(
            bachelors_premium=0.50, masters_premium=0.18,
            phd_premium=0.12, avg_student_debt=25000, years_to_roi=6,
        ),
        labor=LaborMarket(
            unemployment_rate=0.037, median_income=65000,
            income_gini=0.33, startup_success_rate=0.08,
            job_switch_frequency=3.0, remote_work_rate=0.30,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.32, food_income_ratio=0.10,
            transport_income_ratio=0.13, ppp_factor=0.72,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.82, work_life_balance=0.70,
            social_mobility=0.55, healthcare_access=0.90,
            environmental_quality=0.80,
        ),
        stress_baseline_adjustment=-0.04,
        health_decay_multiplier=0.90,
    ),
    
    "AE": RegionalProfile(
        country_code="AE",
        country_name="United Arab Emirates",
        currency="AED",
        tax=TaxModel(brackets=[(1e9, 0.0)]),  # No income tax
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.20, insurance_coverage=0.95,
            cost_income_ratio=0.08, quality_index=0.75,
        ),
        education=EducationROI(
            bachelors_premium=0.60, masters_premium=0.25,
            phd_premium=0.15, avg_student_debt=0, years_to_roi=4,
        ),
        labor=LaborMarket(
            unemployment_rate=0.025, median_income=180000,
            income_gini=0.36, startup_success_rate=0.07,
            job_switch_frequency=4.0, remote_work_rate=0.18,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.30, food_income_ratio=0.12,
            transport_income_ratio=0.10, ppp_factor=0.50,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.90, work_life_balance=0.45,
            social_mobility=0.40, healthcare_access=0.80,
            environmental_quality=0.55,
        ),
        income_volatility_multiplier=1.2,
        stress_baseline_adjustment=0.05,
        relationship_stability_factor=0.85,
    ),
    
    "SG": RegionalProfile(
        country_code="SG",
        country_name="Singapore",
        currency="SGD",
        tax=TaxModel(brackets=[
            (20000, 0.0), (30000, 0.02), (40000, 0.035),
            (80000, 0.07), (120000, 0.115), (160000, 0.15),
            (200000, 0.18), (240000, 0.19), (280000, 0.195),
            (320000, 0.20), (1e9, 0.22),
        ]),
        healthcare=HealthcareModel(
            out_of_pocket_ratio=0.31, insurance_coverage=0.97,
            cost_income_ratio=0.05, quality_index=0.88,
        ),
        education=EducationROI(
            bachelors_premium=0.70, masters_premium=0.25,
            phd_premium=0.15, avg_student_debt=15000, years_to_roi=4,
        ),
        labor=LaborMarket(
            unemployment_rate=0.020, median_income=67000,
            income_gini=0.37, startup_success_rate=0.12,
            job_switch_frequency=3.5, remote_work_rate=0.20,
        ),
        cost_of_living=CostOfLiving(
            housing_income_ratio=0.28, food_income_ratio=0.09,
            transport_income_ratio=0.08, ppp_factor=0.70,
        ),
        quality_of_life=QualityOfLife(
            safety_index=0.95, work_life_balance=0.40,
            social_mobility=0.50, healthcare_access=0.92,
            environmental_quality=0.70,
        ),
        stress_baseline_adjustment=0.08,
    ),
}


# ── Calibration Engine ───────────────────────────────────────

class RegionalCalibrator:
    """
    Adjusts simulation parameters based on country-specific data.
    Grounds simulations in real-world economic statistics.
    """
    
    def get_profile(self, country_code: str) -> RegionalProfile:
        """Get calibration profile for a country, defaulting to US."""
        return REGIONAL_PROFILES.get(country_code.upper(), REGIONAL_PROFILES["US"])
    
    def adjust_volatility(self, base_vol: np.ndarray, country: str) -> np.ndarray:
        """Adjust simulation volatility by regional multiplier."""
        profile = self.get_profile(country)
        adjusted = base_vol.copy()
        # Income-related dimensions get country volatility multiplier
        adjusted[0] *= profile.income_volatility_multiplier  # liquid_assets
        adjusted[3] *= profile.income_volatility_multiplier  # income_growth_rate
        adjusted[4] *= profile.income_volatility_multiplier  # expense_ratio
        return adjusted
    
    def adjust_stress_baseline(self, base_stress: float, country: str) -> float:
        """Adjust baseline stress by country work culture."""
        profile = self.get_profile(country)
        return np.clip(base_stress + profile.stress_baseline_adjustment, 0.0, 1.0)
    
    def adjust_health_decay(self, base_decay: float, country: str) -> float:
        """Adjust health decay rate by country healthcare quality."""
        profile = self.get_profile(country)
        return base_decay * profile.health_decay_multiplier
    
    def get_startup_success_rate(self, country: str) -> float:
        """Get country-specific startup survival rate."""
        return self.get_profile(country).labor.startup_success_rate
    
    def get_education_roi(self, country: str, level: str) -> float:
        """Get education ROI for country and education level."""
        profile = self.get_profile(country)
        premiums = {
            "bachelors": profile.education.bachelors_premium,
            "masters": profile.education.masters_premium,
            "phd": profile.education.phd_premium,
        }
        return premiums.get(level, 0.0)
    
    def get_effective_tax_rate(self, country: str, income: float) -> float:
        """Get effective tax rate for income in country."""
        return self.get_profile(country).tax.effective_rate(income)
    
    def enrich_decision_delta(self, delta: dict, country: str) -> dict:
        """
        Enrich a decision delta with country-specific adjustments.
        E.g., startup decision uses country startup success rate.
        """
        profile = self.get_profile(country)
        
        if delta.get("decision_type") == "career_transition":
            # Adjust by country startup success rate
            base_rate = 0.10
            country_rate = profile.labor.startup_success_rate
            adjustment = country_rate / base_rate
            if "income_stability" in delta:
                delta["income_stability"] *= adjustment
                
        elif delta.get("decision_type") == "education":
            # Adjust by country education ROI
            delta["_education_roi"] = profile.education.masters_premium
            delta["_student_debt"] = profile.education.avg_student_debt
            
        elif delta.get("decision_type") == "relocation":
            # Adjust stress by destination work-life balance
            wlb = profile.quality_of_life.work_life_balance
            delta["stress_load"] = delta.get("stress_load", 0) * (1.3 - wlb)
        
        return delta
