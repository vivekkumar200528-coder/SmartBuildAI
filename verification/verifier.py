import pandas as pd


INPUT_FILE = "data/control_results.csv"

OUTPUT_FILE = "data/verification_results.csv"


# ==========================================================
# BUILDING LIMITS
# ==========================================================

MIN_COMFORT_TEMP = 22.0
MAX_COMFORT_TEMP = 26.0

MAX_CO2 = 1000


# ==========================================================
# LOAD DATA
# ==========================================================

print("Loading control results...")

df = pd.read_csv(INPUT_FILE)

print(
    f"Records loaded: {len(df)}"
)


# ==========================================================
# 1. TEMPERATURE VERIFICATION
# ==========================================================

df["temperature_ok"] = (
    (df["temperature_c"] >= MIN_COMFORT_TEMP)
    &
    (df["temperature_c"] <= MAX_COMFORT_TEMP)
)


# ==========================================================
# 2. CO2 / IAQ VERIFICATION
# ==========================================================

df["co2_ok"] = (
    df["co2_ppm"] <= MAX_CO2
)


# ==========================================================
# 3. OVERALL COMFORT / IAQ STATUS
# ==========================================================

df["comfort_iaq_ok"] = (
    df["temperature_ok"]
    &
    df["co2_ok"]
)


# ==========================================================
# 4. POWER SAVING VERIFICATION
# ==========================================================

df["power_saving_kw"] = (
    df["total_power_kw"]
    -
    df["optimized_total_power_kw"]
)


df["energy_reduced"] = (
    df["power_saving_kw"] > 0
)


# ==========================================================
# 5. CALCULATE TOTALS
# ==========================================================

baseline_power = (
    df["total_power_kw"].sum()
)

optimized_power = (
    df["optimized_total_power_kw"].sum()
)

power_saved = (
    baseline_power
    -
    optimized_power
)


savings_percentage = (
    power_saved
    / baseline_power
) * 100


# ==========================================================
# 6. COMFORT / IAQ STATISTICS
# ==========================================================

comfort_violations = (
    (~df["temperature_ok"]).sum()
)

co2_violations = (
    (~df["co2_ok"]).sum()
)

total_violations = (
    (~df["comfort_iaq_ok"]).sum()
)


comfort_compliance = (
    df["temperature_ok"].mean()
) * 100


co2_compliance = (
    df["co2_ok"].mean()
) * 100


overall_compliance = (
    df["comfort_iaq_ok"].mean()
) * 100


# ==========================================================
# 7. VERIFICATION STATUS
# ==========================================================

if overall_compliance >= 95:

    verification_status = "PASS"

else:

    verification_status = "REVIEW REQUIRED"


# ==========================================================
# 8. SAVE RESULTS
# ==========================================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================================
# 9. DISPLAY REPORT
# ==========================================================

print("\n")
print("=" * 50)
print("       SMARTBUILD AI VERIFICATION REPORT")
print("=" * 50)


print("\nENERGY")
print("------")

print(
    f"Baseline power total: "
    f"{baseline_power:.2f} kW"
)

print(
    f"Optimized power total: "
    f"{optimized_power:.2f} kW"
)

print(
    f"Power saved: "
    f"{power_saved:.2f} kW"
)

print(
    f"Energy reduction: "
    f"{savings_percentage:.2f}%"
)


print("\nCOMFORT")
print("-------")

print(
    f"Temperature compliance: "
    f"{comfort_compliance:.2f}%"
)

print(
    f"Temperature violations: "
    f"{comfort_violations}"
)


print("\nIAQ")
print("---")

print(
    f"CO2 compliance: "
    f"{co2_compliance:.2f}%"
)

print(
    f"CO2 violations: "
    f"{co2_violations}"
)


print("\nOVERALL")
print("-------")

print(
    f"Total constraint violations: "
    f"{total_violations}"
)

print(
    f"Overall compliance: "
    f"{overall_compliance:.2f}%"
)

print(
    f"Verification status: "
    f"{verification_status}"
)


print(
    f"\nResults saved to: "
    f"{OUTPUT_FILE}"
)

print("=" * 50)