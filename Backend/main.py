import json
import sys
from pathlib import Path
from model.live_anomaly_detector import LiveAnomalyDetector
from model.live_optimizer import LiveOptimizer
from Control.live_controller import LiveController
from verification.live_verifier import LiveVerifier
from verification.live_metrics import LivePerformanceMetrics
from live_loop import LiveBuildingLoop
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware


# =========================================================
# PROJECT PATHS
# =========================================================

# Always resolve paths from the project root,
# no matter where the terminal is.
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


CONTROL_FILE = DATA_DIR / "control_results.csv"
VERIFICATION_FILE = DATA_DIR / "verification_results.csv"
ANOMALY_FILE = DATA_DIR / "anomaly_detection_results.csv"
PREDICTION_FILE = DATA_DIR / "energy_prediction_results.csv"


# =========================================================
# LIVE SIMULATION
# =========================================================

# Location of simulator folder
SIMULATOR_DIR = BASE_DIR / "simulator"

# Add simulator folder to Python's import path
if str(SIMULATOR_DIR) not in sys.path:
    sys.path.insert(0, str(SIMULATOR_DIR))


# Import our live simulator
from live_simulator import LiveSimulator


# =========================================================
# LIVE ENERGY PREDICTION MODEL
# =========================================================

# Add project root to Python path
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


from model.energy_model import EnergyPredictionModel


# =========================================================
# CREATE MODEL + SIMULATOR
# =========================================================

# Create ONE simulator instance.
# This is important because the simulation time must continue
# advancing between API requests.
live_simulator = LiveSimulator()


# Create ONE energy prediction model instance.
# The model is trained when the backend starts.
energy_model = EnergyPredictionModel()

live_anomaly_detector = LiveAnomalyDetector()
live_optimizer = LiveOptimizer()
live_verifier = LiveVerifier()
live_building_loop = LiveBuildingLoop()


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="SmartBuild AI API"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def load_csv(path: Path) -> pd.DataFrame:

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail={
                "error": "Required data file not found",
                "file": str(path),
            },
        )

    try:

        return pd.read_csv(path)

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "Could not read data file",
                "file": str(path),
                "reason": str(exc),
            },
        )


def to_records(df: pd.DataFrame) -> list:
    """
    DataFrame -> JSON-safe list of dictionaries.
    NaN becomes null.
    """

    return json.loads(
        df.to_json(
            orient="records",
            date_format="iso",
        )
    )


def latest_rows(df: pd.DataFrame) -> pd.DataFrame:

    latest = df["timestamp"].max()

    return df[
        df["timestamp"] == latest
    ]


def r(value, digits=2):

    return round(
        float(value),
        digits,
    )


# =========================================================
# BASIC API
# =========================================================

@app.get("/")
def root():

    return {
        "system": "SmartBuild AI",
        "status": "running",
        "message": "Smart Building Energy Management API",
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health")
def health():

    files = {
        f.name: f.exists()
        for f in [
            CONTROL_FILE,
            VERIFICATION_FILE,
            ANOMALY_FILE,
            PREDICTION_FILE,
        ]
    }

    return {
        "status": "healthy",
        "data_dir": str(DATA_DIR),
        "data_files_found": files,
        "all_files_present": all(
            files.values()
        ),
    }


# =========================================================
# BUILDING SUMMARY
# =========================================================

@app.get("/building/summary")
def building_summary():

    df = load_csv(
        CONTROL_FILE
    )

    building_power = (
        df.groupby("timestamp")[
            "total_power_kw"
        ].sum()
    )

    return {

        "number_of_rooms":
            int(
                df["room_id"].nunique()
            ),

        "total_records":
            int(
                len(df)
            ),

        "average_occupancy":
            r(
                df["occupancy"].mean()
            ),

        "average_temperature":
            r(
                df["temperature_c"].mean()
            ),

        "average_co2":
            r(
                df["co2_ppm"].mean()
            ),

        "average_power_kw":
            r(
                building_power.mean()
            ),
    }


# =========================================================
# CURRENT BUILDING STATUS
# =========================================================

@app.get("/building/status")
def building_status():

    df = load_csv(
        CONTROL_FILE
    )

    now = latest_rows(df)

    return {

        "timestamp":
            str(
                now["timestamp"].iloc[0]
            ),

        "occupancy":
            int(
                now["occupancy"].sum()
            ),

        "temperature_c":
            r(
                now["temperature_c"].mean()
            ),

        "co2_ppm":
            r(
                now["co2_ppm"].mean()
            ),

        "current_power_kw":
            r(
                now["total_power_kw"].sum()
            ),

        "optimized_power_kw":
            r(
                now[
                    "optimized_total_power_kw"
                ].sum()
            ),
    }


# =========================================================
# ANOMALIES
# =========================================================

@app.get("/anomalies")
def anomalies():

    df = load_csv(
        ANOMALY_FILE
    )

    bad = (
        df[
            df["status"] == "Anomaly"
        ]
        .sort_values(
            "timestamp",
            ascending=False,
        )
    )

    cols = [

        "timestamp",
        "room_id",
        "occupancy",
        "temperature_c",
        "co2_ppm",
        "hvac_kw",
        "equipment_kw",
        "total_power_kw",
        "anomaly_score",

    ]

    cols = [
        c
        for c in cols
        if c in bad.columns
    ]

    return {

        "total_anomalies":
            int(
                len(bad)
            ),

        "total_records":
            int(
                len(df)
            ),

        "recent_anomalies":
            to_records(
                bad[
                    cols
                ].head(10)
            ),
    }


# =========================================================
# ENERGY PREDICTION
# =========================================================

@app.get("/energy/prediction")
def energy_prediction():

    df = load_csv(
        PREDICTION_FILE
    ).tail(50)

    cols = [

        "timestamp",
        "total_power_kw",
        "future_power_kw",
        "predicted_power_kw",

    ]

    return {

        "count":
            int(
                len(df)
            ),

        "records":
            to_records(
                df[cols]
            ),
    }


# =========================================================
# OPTIMIZATION
# =========================================================

@app.get("/optimization")
def optimization():

    df = load_csv(
        CONTROL_FILE
    )

    baseline = (
        df["total_power_kw"].sum()
    )

    optimized = (
        df[
            "optimized_total_power_kw"
        ].sum()
    )

    saved = (
        baseline - optimized
    )

    return {

        "baseline_power_kw":
            r(
                baseline
            ),

        "optimized_power_kw":
            r(
                optimized
            ),

        "power_saved_kw":
            r(
                saved
            ),

        "saving_percentage":
            r(
                saved / baseline * 100
            )
            if baseline
            else 0,
    }


# =========================================================
# VERIFICATION
# =========================================================

@app.get("/verification")
def verification():

    df = load_csv(
        VERIFICATION_FILE
    )

    return {

        "temperature_compliance":
            r(
                df[
                    "temperature_ok"
                ].mean()
                * 100
            ),

        "co2_compliance":
            r(
                df[
                    "co2_ok"
                ].mean()
                * 100
            ),

        "overall_compliance":
            r(
                df[
                    "comfort_iaq_ok"
                ].mean()
                * 100
            ),
    }


# =========================================================
# ROOM MONITORING
# =========================================================

@app.get("/rooms")
def rooms():

    df = load_csv(
        CONTROL_FILE
    )

    now = (
        latest_rows(df)
        .sort_values("room_id")
    )

    out = pd.DataFrame({

        "room_id":
            now["room_id"],

        "floor":
            now["floor"],

        "room_type":
            now["room_type"],

        "occupancy":
            now["occupancy"],

        "temperature_c":
            now["temperature_c"],

        "co2_ppm":
            now["co2_ppm"],

        "power_kw":
            now["total_power_kw"],

        "optimized_power_kw":
            now[
                "optimized_total_power_kw"
            ],

        "control_mode":
            now["control_mode"],

        "control_message":
            now["control_message"],
    })

    return {

        "timestamp":
            str(
                now[
                    "timestamp"
                ].iloc[0]
            ),

        "rooms":
            to_records(out),
    }


# =========================================================
# LIVE SIMULATION
# =========================================================

@app.get("/simulation/step")
def simulation_step():

    # Generate the next 15-minute
    # virtual building state.
    records = live_simulator.step()

    # Calculate building-level summary.
    summary = (
        live_simulator
        .get_building_summary()
    )

    return {

        "status": "success",

        "timestamp":
            summary[
                "timestamp"
            ],

        "summary":
            summary,

        "rooms":
            records,
    }


# =========================================================
# LIVE BUILDING STATUS
# =========================================================

@app.get("/building/live-status")
def live_building_status():

    if not live_simulator.latest_records:
        live_simulator.step()

    summary = (
        live_simulator
        .get_building_summary()
    )

    return {
        "status": "success",
        "data": summary,
    }


# =========================================================
# LIVE ML INPUT
# =========================================================

@app.get("/ml/live-input")
def ml_live_input():

    # Make sure we have live sensor data.
    if not live_simulator.latest_records:
        live_simulator.step()

    # Convert the latest room readings into
    # a DataFrame for feature aggregation.
    df = live_simulator.get_dataframe()

    # ---------------------------------------------------------
    # BUILDING-LEVEL FEATURES
    # ---------------------------------------------------------

    total_occupancy = int(
        df["occupancy"].sum()
    )

    average_temperature = round(
        df["temperature_c"].mean(),
        2,
    )

    average_humidity = round(
        df["humidity_percent"].mean(),
        2,
    )

    average_co2 = round(
        df["co2_ppm"].mean(),
        2,
    )

    total_hvac_power = round(
        df["hvac_kw"].sum(),
        2,
    )

    total_lighting_power = round(
        df["lighting_kw"].sum(),
        2,
    )

    total_equipment_power = round(
        df["equipment_kw"].sum(),
        2,
    )

    total_power = round(
        df["total_power_kw"].sum(),
        2,
    )

    # ---------------------------------------------------------
    # RETURN ML FEATURE VECTOR
    # ---------------------------------------------------------

    return {

        "status": "success",

        "timestamp":
            str(
                df["timestamp"].iloc[0]
            ),

        "features": {

            "occupancy":
                total_occupancy,

            "temperature_c":
                average_temperature,

            "humidity_percent":
                average_humidity,

            "co2_ppm":
                average_co2,

            "hvac_kw":
                total_hvac_power,

            "lighting_kw":
                total_lighting_power,

            "equipment_kw":
                total_equipment_power,

            "current_power_kw":
                total_power,
        },
    }


# =========================================================
# LIVE ENERGY PREDICTION
# =========================================================

@app.get("/ml/live-prediction")
def ml_live_prediction():

    # Make sure live sensor data exists.
    if not live_simulator.latest_records:
        live_simulator.step()

    # Get latest live room data.
    df = live_simulator.get_dataframe()

    # ---------------------------------------------------------
    # BUILDING-LEVEL FEATURES
    # ---------------------------------------------------------

    total_occupancy = int(
        df["occupancy"].sum()
    )

    average_temperature = round(
        df["temperature_c"].mean(),
        2,
    )

    average_humidity = round(
        df["humidity_percent"].mean(),
        2,
    )

    average_co2 = round(
        df["co2_ppm"].mean(),
        2,
    )

    total_hvac_power = round(
        df["hvac_kw"].sum(),
        2,
    )

    total_lighting_power = round(
        df["lighting_kw"].sum(),
        2,
    )

    total_equipment_power = round(
        df["equipment_kw"].sum(),
        2,
    )

    total_power = round(
        df["total_power_kw"].sum(),
        2,
    )

    # ---------------------------------------------------------
    # TIME FEATURES
    # ---------------------------------------------------------

    timestamp = pd.to_datetime(
        df["timestamp"].iloc[0]
    )

    hour = int(
        timestamp.hour
    )

    day_of_week = int(
        timestamp.dayofweek
    )

    # ---------------------------------------------------------
    # CREATE LIVE FEATURE VECTOR
    # ---------------------------------------------------------

    live_features = {

        "occupancy":
            total_occupancy,

        "temperature_c":
            average_temperature,

        "humidity_percent":
            average_humidity,

        "co2_ppm":
            average_co2,

        "hvac_kw":
            total_hvac_power,

        "lighting_kw":
            total_lighting_power,

        "equipment_kw":
            total_equipment_power,

        "total_power_kw":
            total_power,

        "hour":
            hour,

        "day_of_week":
            day_of_week,
    }

    # ---------------------------------------------------------
    # PREDICT NEXT 15-MINUTE POWER
    # ---------------------------------------------------------

    predicted_power = (
        energy_model.predict(
            live_features
        )
    )

    # ---------------------------------------------------------
    # RETURN LIVE PREDICTION
    # ---------------------------------------------------------

    return {

        "status": "success",

        "timestamp":
            str(timestamp),

        "prediction_horizon":
            "15 minutes",

        "current_power_kw":
            total_power,

        "predicted_power_kw":
            predicted_power,

        "features":
            live_features,
    }
# =========================================================
# LIVE ANOMALY DETECTION
# =========================================================

@app.get("/ml/live-anomalies")
def ml_live_anomalies():

    # Make sure live sensor data exists.
    if not live_simulator.latest_records:
        live_simulator.step()


    # Get latest room readings.
    rooms = live_simulator.get_rooms()


    # Detect anomalies.
    result = (
        live_anomaly_detector
        .detect_building_anomalies(
            rooms
        )
    )


    return {

        "status": "success",

        "timestamp":
            str(
                live_simulator
                .get_building_summary()
                ["timestamp"]
            ),

        "total_rooms":
            result["total_rooms"],

        "total_anomalies":
            result["total_anomalies"],

        "normal_rooms":
            result["normal_rooms"],

        "anomalies":
            result["anomalies"],

    }
# =========================================================
# LIVE OPTIMIZATION
# =========================================================

@app.get("/ml/live-optimization")
def ml_live_optimization():

    # Make sure live sensor data exists.
    if not live_simulator.latest_records:
        live_simulator.step()


    # Get latest room readings.
    rooms = live_simulator.get_rooms()


    # Optimize the current building state.
    result = (
        live_optimizer
        .optimize_building(
            rooms
        )
    )


    return {

        "status": "success",

        "timestamp":
            str(
                live_simulator
                .get_building_summary()
                ["timestamp"]
            ),

        "total_rooms":
            result["total_rooms"],

        "current_power_kw":
            result["current_power_kw"],

        "optimized_power_kw":
            result["optimized_power_kw"],

        "power_saved_kw":
            result["power_saved_kw"],

        "saving_percentage":
            result["saving_percentage"],

        "rooms":
            result["rooms"]
    }
@app.get("/ml/live-control")
def ml_live_control():

    if not live_simulator.latest_records:
        live_simulator.step()

    rooms = live_simulator.get_rooms()

    result = live_controller.control_building(
        rooms
    )

    return {
        "status": "success",

        "timestamp": str(
            live_simulator
            .get_building_summary()["timestamp"]
        ),

        "total_rooms":
            result["total_rooms"],

        "controlled_rooms":
            result["controlled_rooms"],

        "rooms":
            result["rooms"],
    }
@app.get("/ml/live-verification")
def ml_live_verification():

    if not live_simulator.latest_records:
        live_simulator.step()

    rooms = live_simulator.get_rooms()

    # Generate control decisions
    control_result = live_controller.control_building(rooms)

    # Verify the effect of those decisions
    verification_result = live_verifier.verify_building(
        rooms,
        control_result["rooms"]
    )

    return {
        "status": "success",
        "timestamp": str(
            live_simulator.get_building_summary()["timestamp"]
        ),
        "total_rooms": verification_result["total_rooms"],
        "improved_rooms": verification_result["improved_rooms"],
        "current_power_kw": verification_result["current_power_kw"],
        "optimized_power_kw": verification_result["optimized_power_kw"],
        "power_saved_kw": verification_result["power_saved_kw"],
        "saving_percentage": verification_result["saving_percentage"],
        "rooms": verification_result["rooms"]
    }
@app.get("/ml/live-loop")
def ml_live_loop():
    result = live_building_loop.step()

    return result

# =========================================================
# LIVE SYSTEM PERFORMANCE METRICS
# =========================================================

@app.get("/ml/live-metrics")
def ml_live_metrics():
    """
    Run one complete live cycle and return system-level
    performance metrics derived from the simulation.
    """
    result = live_building_loop.step()

    return {
        "status": "success",
        "timestamp": result["timestamp"],
        "metrics": result["metrics"],
    }

