# SmartBuild AI

> **AI-Powered Smart Building Energy Management System (BEMS)**\
> A virtual building-management prototype that combines simulated IoT
> sensor data, machine learning, anomaly detection, energy prediction,
> optimization, automated control, and verification in a closed loop.

## Overview

**SmartBuild AI** is a software-based Building Energy Management System
designed to demonstrate how AI and automation can be used to monitor and
optimize energy consumption in a commercial building while maintaining
occupant comfort and indoor air quality.

The system follows a continuous closed-loop workflow:

**Sense → Analyze → Predict → Optimize → Control → Verify**

Instead of treating energy prediction, optimization, and control as
separate demonstrations, SmartBuild AI connects them into one live
simulation cycle.

> **Important:** This repository is a **virtual BEMS prototype using
> simulated IoT sensor streams**. It is not a deployed building-control
> system and does not directly control physical HVAC or lighting
> equipment.

------------------------------------------------------------------------

## Problem Statement

Commercial buildings consume significant energy through HVAC, lighting,
and equipment. A conventional monitoring system may show energy
consumption but does not necessarily provide an intelligent feedback
loop that can:

-   monitor building conditions continuously,
-   identify abnormal energy or environmental conditions,
-   predict future energy demand,
-   optimize energy-consuming systems,
-   generate control actions,
-   and verify whether optimization actually reduced energy use without
    violating comfort or IAQ constraints.

SmartBuild AI demonstrates this complete workflow in a reproducible
software environment.

------------------------------------------------------------------------

## Proposed Solution

SmartBuild AI creates a virtual commercial building with **15 rooms
across 3 floors** and generates time-series sensor data at **15-minute
intervals**.

The platform processes the simulated data through several intelligence
layers:

1.  **Sensing** --- generates occupancy, temperature, humidity, CO₂,
    lighting, HVAC, equipment, and total-power data.
2.  **Analysis** --- evaluates room and building conditions.
3.  **Prediction** --- estimates building energy demand using the energy
    prediction model.
4.  **Anomaly Detection** --- identifies conditions such as high CO₂,
    high temperature, high power consumption, and energy use in
    unoccupied rooms.
5.  **Optimization** --- calculates lower-energy HVAC and lighting
    settings while considering comfort and IAQ constraints.
6.  **Control** --- converts optimized conditions into room-level
    control commands.
7.  **Verification** --- compares current and optimized power and checks
    comfort/IAQ compliance.
8.  **Performance Metrics** --- tracks power savings, cumulative energy
    savings, compliance, optimized rooms, anomalies, and control
    actions.

------------------------------------------------------------------------

## System Architecture

``` text
                 ┌─────────────────────────┐
                 │   Virtual Building      │
                 │  3 Floors / 15 Rooms    │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │   Simulated IoT Data    │
                 │ Occupancy / Temp / CO₂  │
                 │ Humidity / HVAC / Light │
                 │ Equipment / Power       │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │     AI Analysis         │
                 │ Energy Prediction       │
                 │ Anomaly Detection       │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      Optimization       │
                 │ HVAC + Lighting         │
                 │ Comfort + IAQ Constraints│
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │       Control           │
                 │ Room-level Commands     │
                 └────────────┬────────────┘
                              │
                              ▼
                 ┌─────────────────────────┐
                 │      Verification       │
                 │ Power / Savings /       │
                 │ Comfort / CO₂ Compliance│
                 └────────────┬────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │ Live Dashboard   │
                    │ Monitoring + KPIs │
                    └──────────────────┘
                              │
                              └──────► Next Cycle
```

------------------------------------------------------------------------

## Virtual Building

The simulator represents a commercial office building with:

  Parameter              Configuration
  ---------------------- -------------------
  Floors                 3
  Rooms per floor        5
  Total rooms            15
  Area per room          200 m²
  Total simulated area   3000 m²
  Simulation interval    15 minutes
  Building type          Commercial office

### Room Types

Each floor contains:

-   R1 --- Office
-   R2 --- Office
-   R3 --- Meeting Room
-   R4 --- Laboratory
-   R5 --- Office

Different room types have different occupancy characteristics and
capacities.

------------------------------------------------------------------------

## Simulated Sensor Data

The virtual IoT layer generates room-level time-series data including:

-   Occupancy
-   Temperature
-   Humidity
-   CO₂ concentration
-   Lighting power
-   HVAC power
-   Equipment power
-   Total power consumption

The project can also generate a historical CSV dataset for analysis and
model development.

------------------------------------------------------------------------

## AI & Intelligence Layer

### Energy Prediction

The energy prediction module estimates building energy demand from
building/environmental inputs.

The prediction is exposed through the backend API and displayed on the
dashboard alongside live energy measurements.

### Anomaly Detection

The live anomaly detector checks room conditions against defined
operating thresholds.

Examples include:

-   High CO₂
-   High temperature
-   High energy consumption
-   Energy consumption while a room is unoccupied
-   High HVAC demand

Each room receives an anomaly status and, when applicable, a list of
detected reasons.

### Energy Optimization

The optimizer evaluates current room conditions and calculates optimized
HVAC and lighting operation.

The optimization logic considers:

-   Occupancy
-   Temperature
-   CO₂
-   Current HVAC demand
-   Current lighting demand
-   Comfort limits
-   Unoccupied-room energy reduction

The system separates **prediction/anomaly intelligence** from
**rule-based optimization and control**, making the control path
explicit and verifiable.

------------------------------------------------------------------------

## Comfort & IAQ Constraints

The prototype verifies operating conditions using:

-   Temperature comfort range: **22--26 °C**
-   CO₂ limit: **≤ 1000 ppm**

Energy reduction is therefore evaluated together with environmental
compliance rather than as an isolated power-saving number.

------------------------------------------------------------------------

## Live Closed-Loop Operation

The main live endpoint is:

``` text
GET /ml/live-loop
```

A single live cycle performs the following sequence:

``` text
Generate sensor data
       ↓
Generate building summary
       ↓
Predict energy
       ↓
Detect anomalies
       ↓
Optimize HVAC + lighting
       ↓
Generate control commands
       ↓
Verify optimized operation
       ↓
Update performance metrics
```

The dashboard automatically refreshes the live cycle and displays the
resulting KPIs.

------------------------------------------------------------------------

## Dashboard

The React dashboard provides live visibility into:

-   Building occupancy
-   Temperature
-   Humidity
-   CO₂
-   Current energy
-   Predicted energy
-   Anomalies
-   Optimization results
-   Power savings
-   Control commands
-   Verification results
-   Comfort compliance
-   CO₂ compliance
-   Cumulative energy savings
-   Room-level status

------------------------------------------------------------------------

## Example Live Cycle

A successful live simulation cycle produced the following example:

  Metric                      Example Result
  ------------------------- ----------------
  Occupancy                               78
  Average temperature                23.7 °C
  Average humidity                    53.68%
  Average CO₂                     563.61 ppm
  Current power                     39.83 kW
  Optimized power                   37.50 kW
  Power saved                        2.33 kW
  Instantaneous saving                 5.85%
  Optimized rooms                    15 / 15
  Control actions                         45
  Anomalies                                0
  Comfort compliance                    100%
  CO₂ compliance                        100%
  Overall compliance                    100%
  Cumulative energy saved          0.582 kWh

These values represent **one simulated cycle**, not a guaranteed
real-building energy-saving rate.

------------------------------------------------------------------------

## Technology Stack

### Backend

-   Python
-   FastAPI
-   Uvicorn
-   Pandas

### AI / ML

-   Python-based prediction pipeline
-   Energy prediction model
-   Live anomaly detection
-   Rule-based energy optimization
-   Performance verification

### Frontend

-   React
-   Vite
-   Axios
-   Recharts
-   Lucide React

### Simulation

-   Python
-   Synthetic / simulated IoT time-series data

### Development

-   Git
-   GitHub
-   VS Code
-   npm

------------------------------------------------------------------------

## Project Structure

``` text
SmartBuildAI/
│
├── Backend/
│   ├── main.py
│   └── live_loop.py
│
├── Control/
│   └── live_controller.py
│
├── Data/
│
├── Frontend/
│   ├── src/
│   ├── package.json
│   └── ...
│
├── model/
│   ├── live_anomaly_detector.py
│   ├── live_optimizer.py
│   └── ...
│
├── optimization/
│
├── simulator/
│   ├── building.py
│   ├── sensors.py
│   ├── generate_data.py
│   └── live_simulator.py
│
├── verification/
│   ├── live_verifier.py
│   └── live_metrics.py
│
├── package.json
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

## Installation

### Prerequisites

Install:

-   Python 3.x
-   Node.js and npm
-   Git

### 1. Clone the repository

``` bash
git clone https://github.com/vivekkumar200528-coder/SmartBuildAI.git
cd SmartBuildAI
```

### 2. Install Python dependencies

If a `requirements.txt` file is present:

``` bash
pip install -r requirements.txt
```

Otherwise install the backend dependencies required by the project
environment, including FastAPI, Uvicorn, and Pandas.

### 3. Install frontend dependencies

``` bash
cd Frontend
npm install
cd ..
```

------------------------------------------------------------------------

## Running the Project

From the project root:

### Start the backend

``` bash
npm run backend
```

The FastAPI server runs at:

``` text
http://127.0.0.1:8000
```

### Start the frontend

Open another terminal in the project root:

``` bash
npm run frontend
```

The Vite development server normally runs at:

``` text
http://localhost:5173
```

### Run both together

The root project includes a development script:

``` bash
npm run dev
```

This starts the backend and frontend together.

------------------------------------------------------------------------

## API Endpoints

Important backend endpoints include:

  Endpoint                  Purpose
  ------------------------- ----------------------------------------
  `/`                       Backend status
  `/health`                 Health check
  `/building/summary`       Building summary
  `/building/status`        Building status
  `/rooms`                  Room-level information
  `/anomalies`              Historical/current anomaly information
  `/energy/prediction`      Energy prediction
  `/optimization`           Energy optimization
  `/verification`           Verification results
  `/simulation/step`        Advance simulation
  `/building/live-status`   Live building status
  `/ml/live-input`          Live ML input
  `/ml/live-prediction`     Live energy prediction
  `/ml/live-anomalies`      Live anomaly detection
  `/ml/live-optimization`   Live optimization
  `/ml/live-control`        Live control
  `/ml/live-verification`   Live verification
  `/ml/live-loop`           Complete closed-loop cycle

------------------------------------------------------------------------

## Design Principles

### 1. Closed-loop automation

The system does not stop at monitoring. It connects sensing,
intelligence, optimization, control, and verification.

### 2. Separation of intelligence and control

Energy prediction and anomaly detection provide analytical intelligence,
while optimization and control apply explicit operating rules.

### 3. Constraint-aware optimization

Energy savings are evaluated together with temperature and CO₂
compliance.

### 4. Measurable results

Optimization performance is calculated from current versus optimized
simulated power rather than relying on a fixed savings claim.

### 5. Room-level visibility

The system can inspect individual rooms instead of showing only a single
building-level energy value.

------------------------------------------------------------------------

## Future Scope

The virtual prototype can be extended toward a physical or production
BEMS by integrating:

-   Real IoT sensors
-   BACnet / Modbus building-control interfaces
-   Real HVAC and lighting controllers
-   Edge computing
-   Real-time databases
-   Advanced forecasting models
-   Reinforcement-learning-based optimization
-   Digital-twin models
-   Cloud deployment
-   Multi-building energy management
-   Automated demand-response integration

------------------------------------------------------------------------

## Current Limitations

This prototype uses simulated building data. Therefore:

-   Sensor values are not measurements from a real building.
-   Control commands are software representations rather than commands
    sent to physical equipment.
-   Energy savings shown by the simulator should not be interpreted as
    guaranteed savings in a real facility.
-   Real deployment would require sensor calibration, equipment
    integration, safety validation, and building-specific control
    policies.

------------------------------------------------------------------------

## Use Case

SmartBuild AI can serve as a prototype architecture for:

-   Commercial office buildings
-   Smart campuses
-   Laboratories
-   Institutional buildings
-   Energy-management demonstrations
-   AI/IoT research
-   Building digital-twin experimentation

------------------------------------------------------------------------

## Project Goal

The long-term goal of SmartBuild AI is to demonstrate a practical
software architecture where building data is continuously converted
into:

**Observations → Predictions → Decisions → Control Actions → Verified
Outcomes**

This creates a foundation for intelligent, data-driven building energy
management.

------------------------------------------------------------------------

## Author

**Vivek Kumar**

Robotics & Artificial Intelligence Engineering

Ramdeobaba University

------------------------------------------------------------------------

## License

This project is intended for educational, research, prototype, and
demonstration purposes.
