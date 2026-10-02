import { useEffect, useState, useCallback } from "react";
import axios from "axios";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import {
  Building2,
  Users,
  Thermometer,
  Wind,
  Zap,
  AlertTriangle,
  TrendingDown,
  ShieldCheck,
  RefreshCw,
  Wifi,
} from "lucide-react";


const API = "http://127.0.0.1:8000";


const ENDPOINTS = {
  summary: "/building/summary",
  status: "/building/status",
  anomalies: "/anomalies",
  prediction: "/energy/prediction",
  optimization: "/optimization",
  verification: "/verification",
  rooms: "/rooms",
};


const fmt = (v, d = 1, unit = "") =>
  v === undefined ||
  v === null ||
  Number.isNaN(Number(v))
    ? "—"
    : `${Number(v).toFixed(d)}${unit}`;


const modeClass = (m) =>
  (m || "unknown").toLowerCase().replace(/\s+/g, "-");


function Kpi({ icon: Icon, label, value, sub }) {
  return (
    <div className="card kpi">

      <div className="kpi-icon">
        <Icon size={22} />
      </div>

      <div>
        <div className="label">{label}</div>

        <div className="value">{value}</div>

        {sub && (
          <div className="sub">
            {sub}
          </div>
        )}
      </div>

    </div>
  );
}


function Stat({ label, value }) {
  return (
    <div className="stat">

      <div className="label">
        {label}
      </div>

      <div className="stat-value">
        {value}
      </div>

    </div>
  );
}


export default function App() {

  const [data, setData] = useState({});

  const [failed, setFailed] = useState([]);

  const [loading, setLoading] = useState(true);

  const [connectionError, setConnectionError] =
    useState(false);


  /*
   * =========================================================
   * LIVE ENERGY HISTORY
   * =========================================================
   *
   * Stores the latest live building power readings.
   *
   * One new point is added every time /simulation/step
   * is called.
   */

  const [liveEnergyHistory, setLiveEnergyHistory] =
    useState([]);


  /*
   * =========================================================
   * LIVE ENERGY PREDICTION
   * =========================================================
   *
   * Stores the latest Random Forest prediction.
   *
   * Prediction horizon:
   * +15 minutes
   */

  const [livePrediction, setLivePrediction] =
    useState(null);


  /*
   * =========================================================
   * LIVE PREDICTION HISTORY
   * =========================================================
   */

  const [livePredictionHistory, setLivePredictionHistory] =
    useState([]);


  /* =========================================================
   * LIVE OPTIMIZATION
   * ========================================================= */

  const [liveOptimization, setLiveOptimization] =
    useState(null);

  /* =========================================================
   * LIVE CONTROL
   * ========================================================= */

  const [liveControl, setLiveControl] =
    useState(null);

  /* =========================================================
   * LIVE VERIFICATION
   * ========================================================= */

  const [liveVerification, setLiveVerification] =
    useState(null);

  /* =========================================================
   * LIVE SYSTEM PERFORMANCE METRICS
   * ========================================================= */
  const [liveMetrics, setLiveMetrics] = useState(null);


  /*
   * =========================================================
   * LOAD DASHBOARD DATA
   * =========================================================
   */

  const load = useCallback(async () => {

    setLoading(true);


    const keys = Object.keys(ENDPOINTS);


    /*
     * =======================================================
     * LOAD ALL EXISTING BACKEND ENDPOINTS
     * =======================================================
     */

    const results = await Promise.allSettled(
      keys.map((k) =>
        axios.get(
          API + ENDPOINTS[k]
        )
      )
    );


    const next = {};

    const bad = [];

    let networkDown = 0;


    results.forEach((res, i) => {

      if (res.status === "fulfilled") {

        next[keys[i]] =
          res.value.data;

      } else {

        bad.push(keys[i]);

        if (!res.reason?.response) {
          networkDown += 1;
        }

      }

    });


    /*
     * =======================================================
     * LIVE CLOSED-LOOP BUILDING SIMULATION
     * =======================================================
     *
     * One backend request executes the complete cycle:
     * Sensors → Prediction → Anomaly Detection
     * → Optimization → Control → Verification
     */

    try {

      const loopResponse =
        await axios.get(
          API + "/ml/live-loop"
        );

      const loopData =
        loopResponse.data;

      /*
       * -----------------------------------------------------
       * LIVE BUILDING STATE
       * -----------------------------------------------------
       */

      next.live = {
        summary: loopData.summary,
        rooms: loopData.rooms,
      };

      /*
       * -----------------------------------------------------
       * LIVE ENERGY HISTORY
       * -----------------------------------------------------
       */

      const liveSummary =
        loopData.summary;

      if (liveSummary) {

        setLiveEnergyHistory(
          (previous) => {

            const newPoint = {
              timestamp:
                liveSummary.timestamp,

              power:
                liveSummary.current_power_kw,
            };

            return [
              ...previous,
              newPoint,
            ].slice(-30);

          }
        );

      }

      /*
       * -----------------------------------------------------
       * LIVE ENERGY PREDICTION
       * -----------------------------------------------------
       */

      if (loopData.prediction) {

        const predictionData = {
          ...loopData.prediction,
          timestamp:
            loopData.timestamp,
        };

        setLivePrediction(
          predictionData
        );

        if (
          predictionData.predicted_power_kw !==
          undefined
        ) {

          setLivePredictionHistory(
            (previous) => {

              const newPoint = {
                timestamp:
                  predictionData.timestamp,

                current:
                  predictionData.current_power_kw,

                predicted:
                  predictionData.predicted_power_kw,
              };

              return [
                ...previous,
                newPoint,
              ].slice(-30);

            }
          );

        }

      }

      /*
       * -----------------------------------------------------
       * LIVE OPTIMIZATION
       * -----------------------------------------------------
       */

      if (loopData.optimization) {

        setLiveOptimization({
          ...loopData.optimization,
          timestamp:
            loopData.timestamp,
        });

      }

      /*
       * -----------------------------------------------------
       * LIVE CONTROL
       * -----------------------------------------------------
       */

      if (loopData.control) {

        setLiveControl({
          ...loopData.control,
          timestamp:
            loopData.timestamp,
        });

      }

      /*
       * -----------------------------------------------------
       * LIVE VERIFICATION
       * -----------------------------------------------------
       */

      if (loopData.verification) {

        setLiveVerification({
          ...loopData.verification,
          timestamp:
            loopData.timestamp,
        });

      }

      /*
       * -----------------------------------------------------
       * LIVE ANOMALIES
       * -----------------------------------------------------
       */

      if (loopData.anomalies) {

        next.liveAnomalies =
          loopData.anomalies;

      }

      /* -----------------------------------------------------
       * LIVE SYSTEM PERFORMANCE METRICS
       * -----------------------------------------------------
       */
      if (loopData.metrics) {
        setLiveMetrics({
          ...loopData.metrics,
          timestamp: loopData.timestamp,
        });
      }

    } catch (loopError) {

      console.error(
        "Live closed-loop request failed:",
        loopError
      );

    }

    setData(next);

    setFailed(bad);


    setConnectionError(
      networkDown === keys.length
    );


    setLoading(false);

  }, []);


  /*
   * =========================================================
   * INITIAL LOAD + AUTO REFRESH
   * =========================================================
   *
   * Dashboard refreshes every 10 seconds.
   */

  useEffect(() => {

    load();


    const interval =
      setInterval(
        () => {
          load();
        },
        10000
      );


    return () =>
      clearInterval(interval);

  }, [load]);


  /*
   * =========================================================
   * DATA
   * =========================================================
   */

  const {
    summary,
    status,
    anomalies,
    prediction,
    optimization,
    verification,
    rooms,
    live,
  } = data;


  /*
   * =========================================================
   * LIVE BUILDING SUMMARY
   * =========================================================
   */

  const liveSummary =
    live?.summary;


  /*
   * =========================================================
   * ENERGY PREDICTION CHART DATA
   * =========================================================
   *
   * Historical model prediction.
   */

  const chartData =
    (prediction?.records ?? []).map(
      (p) => ({

        time:
          String(
            p.timestamp ?? ""
          )
            .slice(5, 16)
            .replace("T", " "),

        actual:
          p.future_power_kw,

        predicted:
          p.predicted_power_kw,

      })
    );


  /*
   * =========================================================
   * LIVE ENERGY CHART DATA
   * =========================================================
   */

  const liveEnergyChartData =
    liveEnergyHistory.map(
      (item) => ({

        time:
          String(
            item.timestamp ?? ""
          ).slice(11, 16),

        power:
          item.power,

      })
    );


  /*
   * =========================================================
   * LIVE PREDICTION CHART DATA
   * =========================================================
   */

  const livePredictionChartData =
    livePredictionHistory.map(
      (item) => ({

        time:
          String(
            item.timestamp ?? ""
          ).slice(11, 16),

        current:
          item.current,

        predicted:
          item.predicted,

      })
    );


  /*
   * =========================================================
   * LIVE PREDICTION VALUES
   * =========================================================
   */

  const currentPredictionPower =
    livePrediction?.current_power_kw;


  const predictedPower =
    livePrediction?.predicted_power_kw;


  const predictionDifference =
    currentPredictionPower !== undefined &&
    predictedPower !== undefined
      ? predictedPower -
        currentPredictionPower
      : null;


  /*
   * =========================================================
   * LIVE OPTIMIZATION VALUES
   * =========================================================
   */

  const liveCurrentPower =
    liveOptimization?.current_power_kw;

  const liveOptimizedPower =
    liveOptimization?.optimized_power_kw;

  const livePowerSaved =
    liveOptimization?.power_saved_kw;

  const liveSavingPercentage =
    liveOptimization?.saving_percentage;


  /*
   * =========================================================
   * ROOM DATA
   * =========================================================
   *
   * Prefer live room data.
   *
   * If live data unavailable,
   * fall back to /rooms.
   */

  const roomList =
    live?.rooms ??
    rooms?.rooms ??
    [];


  /*
   * =========================================================
   * UI
   * =========================================================
   */

  return (

    <div className="app">


      {/* =====================================================
          HEADER
          ===================================================== */}

      <header className="header">

        <div>

          <h1>

            <Building2 size={28} />

            SmartBuild AI

          </h1>


          <p>
            Intelligent Building Energy Management System
          </p>

        </div>


        <div className="header-right">

          <span
            className={`online ${
              connectionError
                ? "offline"
                : ""
            }`}
          >

            <Wifi size={16} />

            {connectionError
              ? "System Offline"
              : "System Online"}

          </span>


          <button
            className="refresh"
            onClick={load}
            disabled={loading}
          >

            <RefreshCw
              size={16}
              className={
                loading
                  ? "spin"
                  : ""
              }
            />

            Refresh

          </button>

        </div>

      </header>


      {/* =====================================================
          BACKEND CONNECTION ERROR
          ===================================================== */}

      {connectionError && (

        <div className="error">

          <strong>
            Backend connection failed.
          </strong>

          <br />

          Start the SmartBuild AI system from the project
          root folder using:

          <br />

          <code>
            npm run dev
          </code>

        </div>

      )}


      {/* =====================================================
          PARTIAL DATA ERROR
          ===================================================== */}

      {!connectionError &&
        failed.length > 0 && (

          <div className="error">

            <strong>
              Data unavailable
            </strong>

            {" "}for: {failed.join(", ")}.

            <br />

            Check that the required CSV files exist in the
            data folder.

            <br />

            Backend health:

            {" "}

            <code>
              {API}/health
            </code>

          </div>

        )}


      {/* =====================================================
          INITIAL LOADING
          ===================================================== */}

      {loading &&
        !Object.keys(data).length && (

          <div className="loading">
            Loading dashboard…
          </div>

        )}


      {!connectionError && (

        <>


          {/* =================================================
              LIVE BUILDING KPIs
              ================================================= */}

          <section className="grid four">


            <Kpi
              icon={Users}
              label="Current Occupancy"
              value={fmt(
                liveSummary?.occupancy,
                0
              )}
              sub="people in building"
            />


            <Kpi
              icon={Thermometer}
              label="Temperature"
              value={fmt(
                liveSummary?.temperature_c,
                1,
                " °C"
              )}
              sub="building average"
            />


            <Kpi
              icon={Wind}
              label="CO₂"
              value={fmt(
                liveSummary?.co2_ppm,
                0,
                " ppm"
              )}
              sub="building average"
            />


            <Kpi
              icon={Zap}
              label="Current Power"
              value={fmt(
                liveSummary?.current_power_kw,
                1,
                " kW"
              )}
              sub={
                liveSummary?.timestamp
                  ? `simulated at ${String(
                      liveSummary.timestamp
                    ).slice(0, 16)}`
                  : ""
              }
            />

          </section>


          {/* =================================================
              LIVE ENERGY PREDICTION
              ================================================= */}

          <h2>
            Live Energy Prediction
          </h2>


          <section className="grid three">


            <Kpi
              icon={Zap}
              label="Current Power"
              value={fmt(
                currentPredictionPower,
                2,
                " kW"
              )}
              sub="live virtual sensor"
            />


            <Kpi
              icon={TrendingDown}
              label="Predicted +15 min"
              value={fmt(
                predictedPower,
                2,
                " kW"
              )}
              sub="Random Forest forecast"
            />


            <Kpi
              icon={TrendingDown}
              label="Forecast Change"
              value={
                predictionDifference === null
                  ? "—"
                  : `${predictionDifference >= 0 ? "+" : ""}${predictionDifference.toFixed(2)} kW`
              }
              sub={
                predictionDifference === null
                  ? "waiting for prediction"
                  : predictionDifference >= 0
                    ? "expected increase"
                    : "expected decrease"
              }
            />

          </section>


          {/* =================================================
              AI INTELLIGENCE
              ================================================= */}

          <h2>
            AI Intelligence
          </h2>


          <section className="grid three">


            <Kpi
              icon={AlertTriangle}
              label="Anomalies Detected"
              value={fmt(
                anomalies?.total_anomalies,
                0
              )}
              sub={
                anomalies
                  ? `of ${anomalies.total_records} records`
                  : ""
              }
            />


            <Kpi
              icon={TrendingDown}
              label="Simulated Energy Reduction"
              value={fmt(
                optimization?.saving_percentage,
                2,
                " %"
              )}
              sub="optimized vs baseline"
            />


            <Kpi
              icon={ShieldCheck}
              label="Comfort / IAQ Compliance"
              value={fmt(
                verification?.overall_compliance,
                2,
                " %"
              )}
              sub="temperature + CO₂"
            />

          </section>


          {/* =================================================
              HISTORICAL ENERGY PREDICTION
              ================================================= */}

          <h2>
            Energy Prediction
          </h2>


          <section className="card chart">

            {chartData.length === 0 ? (

              <div className="empty">
                Data unavailable
              </div>

            ) : (

              <ResponsiveContainer
                width="100%"
                height={320}
              >

                <LineChart
                  data={chartData}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#e2e8f0"
                  />


                  <XAxis
                    dataKey="time"
                    tick={{
                      fontSize: 11,
                    }}
                    minTickGap={30}
                  />


                  <YAxis
                    tick={{
                      fontSize: 11,
                    }}
                    unit=" kW"
                    width={70}
                  />


                  <Tooltip />


                  <Legend />


                  <Line
                    type="monotone"
                    dataKey="actual"
                    name="Actual Power"
                    stroke="#2563eb"
                    strokeWidth={2}
                    dot={false}
                  />


                  <Line
                    type="monotone"
                    dataKey="predicted"
                    name="Predicted Power"
                    stroke="#f97316"
                    strokeWidth={2}
                    dot={false}
                  />

                </LineChart>

              </ResponsiveContainer>

            )}

          </section>


          {/* =================================================
              LIVE ENERGY MONITORING
              ================================================= */}

          <h2>
            Live Energy Monitoring
          </h2>


          <section className="card chart">

            {liveEnergyChartData.length === 0 ? (

              <div className="empty">
                Waiting for live energy data…
              </div>

            ) : (

              <ResponsiveContainer
                width="100%"
                height={320}
              >

                <LineChart
                  data={liveEnergyChartData}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#e2e8f0"
                  />


                  <XAxis
                    dataKey="time"
                    tick={{
                      fontSize: 11,
                    }}
                    minTickGap={30}
                  />


                  <YAxis
                    tick={{
                      fontSize: 11,
                    }}
                    unit=" kW"
                    width={70}
                  />


                  <Tooltip />


                  <Legend />


                  <Line
                    type="monotone"
                    dataKey="power"
                    name="Live Building Power"
                    stroke="#16a34a"
                    strokeWidth={2}
                    dot={false}
                  />

                </LineChart>

              </ResponsiveContainer>

            )}

          </section>


          {/* =================================================
              LIVE PREDICTION MONITORING
              ================================================= */}

          <h2>
            Live Prediction Monitoring
          </h2>


          <section className="card chart">

            {livePredictionChartData.length === 0 ? (

              <div className="empty">
                Waiting for live prediction data…
              </div>

            ) : (

              <ResponsiveContainer
                width="100%"
                height={320}
              >

                <LineChart
                  data={livePredictionChartData}
                >

                  <CartesianGrid
                    strokeDasharray="3 3"
                    stroke="#e2e8f0"
                  />


                  <XAxis
                    dataKey="time"
                    tick={{
                      fontSize: 11,
                    }}
                    minTickGap={30}
                  />


                  <YAxis
                    tick={{
                      fontSize: 11,
                    }}
                    unit=" kW"
                    width={70}
                  />


                  <Tooltip />


                  <Legend />


                  <Line
                    type="monotone"
                    dataKey="current"
                    name="Current Power"
                    stroke="#2563eb"
                    strokeWidth={2}
                    dot={false}
                  />


                  <Line
                    type="monotone"
                    dataKey="predicted"
                    name="Predicted +15 min"
                    stroke="#f97316"
                    strokeWidth={2}
                    dot={false}
                  />

                </LineChart>

              </ResponsiveContainer>

            )}

          </section>


          {/* =================================================
              LIVE ENERGY OPTIMIZATION
              ================================================= */}

          <h2>
            Live Energy Optimization
          </h2>


          <section className="grid four">

            <Kpi
              icon={Zap}
              label="Current Power"
              value={fmt(
                liveCurrentPower,
                2,
                " kW"
              )}
              sub="current simulated demand"
            />


            <Kpi
              icon={TrendingDown}
              label="Optimized Power"
              value={fmt(
                liveOptimizedPower,
                2,
                " kW"
              )}
              sub="after control optimization"
            />


            <Kpi
              icon={TrendingDown}
              label="Power Saved"
              value={fmt(
                livePowerSaved,
                2,
                " kW"
              )}
              sub="estimated live saving"
            />


            <Kpi
              icon={ShieldCheck}
              label="Energy Reduction"
              value={fmt(
                liveSavingPercentage,
                2,
                " %"
              )}
              sub="current vs optimized"
            />

          </section>


          <section className="card">

            <div className="label">
              Live Optimization Status
            </div>

            <div className="sub" style={{ marginTop: "8px" }}>
              The optimizer evaluates occupancy, temperature,
              CO₂, HVAC demand and lighting for each room.
            </div>

          </section>


          {/* =================================================
              BUILDING OVERVIEW
              ================================================= */}

          <h2>
            Building Overview
          </h2>


          <section className="card stats">


            <Stat
              label="Total Rooms"
              value={fmt(
                summary?.number_of_rooms,
                0
              )}
            />


            <Stat
              label="Average Power"
              value={fmt(
                summary?.average_power_kw,
                1,
                " kW"
              )}
            />


            <Stat
              label="Average Temperature"
              value={fmt(
                summary?.average_temperature,
                1,
                " °C"
              )}
            />


            <Stat
              label="Average CO₂"
              value={fmt(
                summary?.average_co2,
                0,
                " ppm"
              )}
            />

          </section>


          {/* =================================================
              LIVE ROOM MONITORING
              ================================================= */}

          <h2>
            Room Monitoring
          </h2>


          {roomList.length === 0 ? (

            <div className="card empty">
              Data unavailable
            </div>

          ) : (

            <section className="grid rooms">


              {roomList.map((room) => (

                <div
                  className="card room"
                  key={room.room_id}
                >


                  {/* Room Header */}

                  <div className="room-head">

                    <strong>
                      {room.room_id}
                    </strong>


                    <span
                      className={`badge ${modeClass(
                        room.control_mode ??
                        "Live"
                      )}`}
                    >

                      {room.control_mode ??
                        "Live"}

                    </span>

                  </div>


                  {/* Room Type */}

                  <div className="room-type">

                    Floor{" "}
                    {room.floor ?? "—"}

                    {" · "}

                    {room.room_type ?? "—"}

                  </div>


                  {/* LIVE ROOM SENSOR DATA */}

                  <div className="room-grid">


                    <span>
                      Occupancy
                    </span>

                    <b>
                      {fmt(
                        room.occupancy,
                        0
                      )}
                    </b>


                    <span>
                      Temperature
                    </span>

                    <b>
                      {fmt(
                        room.temperature_c,
                        1,
                        " °C"
                      )}
                    </b>


                    <span>
                      CO₂
                    </span>

                    <b>
                      {fmt(
                        room.co2_ppm,
                        0,
                        " ppm"
                      )}
                    </b>


                    <span>
                      Humidity
                    </span>

                    <b>
                      {fmt(
                        room.humidity_percent,
                        1,
                        " %"
                      )}
                    </b>


                    <span>
                      Current Power
                    </span>

                    <b>
                      {fmt(
                        room.total_power_kw ??
                          room.power_kw,
                        2,
                        " kW"
                      )}
                    </b>


                    <span>
                      HVAC
                    </span>

                    <b>
                      {fmt(
                        room.hvac_kw,
                        2,
                        " kW"
                      )}
                    </b>

                  </div>


                  {/* LIVE SENSOR MESSAGE */}

                  <div className="room-msg">

                    {room.control_message ??
                      "Live virtual sensor data"}

                  </div>


                </div>

              ))}

            </section>

          )}


          {/* =================================================
              OPTIMIZATION RESULTS
              ================================================= */}

          <h2>
            Optimization Results
          </h2>


          <section className="card stats">


            <Stat
              label="Baseline Power"
              value={fmt(
                optimization?.baseline_power_kw,
                1,
                " kW"
              )}
            />


            <Stat
              label="Optimized Power"
              value={fmt(
                optimization?.optimized_power_kw,
                1,
                " kW"
              )}
            />


            <Stat
              label="Power Saved"
              value={fmt(
                optimization?.power_saved_kw,
                1,
                " kW"
              )}
            />


            <Stat
              label="Reduction"
              value={fmt(
                optimization?.saving_percentage,
                2,
                " %"
              )}
            />

          </section>


          {/* =================================================
              LIVE OPTIMIZATION ACTIONS
              ================================================= */}

          <h2>
            Live Optimization Actions
          </h2>


          <section className="card">

            {!liveOptimization?.rooms?.length ? (

              <div className="empty">
                Waiting for live optimization data…
              </div>

            ) : (

              <div style={{ overflowX: "auto" }}>

                <table style={{
                  width: "100%",
                  borderCollapse: "collapse"
                }}>

                  <thead>
                    <tr>
                      <th style={{ textAlign: "left", padding: "10px" }}>
                        Room
                      </th>
                      <th style={{ textAlign: "left", padding: "10px" }}>
                        Mode
                      </th>
                      <th style={{ textAlign: "right", padding: "10px" }}>
                        Current
                      </th>
                      <th style={{ textAlign: "right", padding: "10px" }}>
                        Optimized
                      </th>
                      <th style={{ textAlign: "right", padding: "10px" }}>
                        Saved
                      </th>
                      <th style={{ textAlign: "left", padding: "10px" }}>
                        Action
                      </th>
                    </tr>
                  </thead>

                  <tbody>

                    {liveOptimization.rooms.map((room) => (

                      <tr key={room.room_id}>

                        <td style={{ padding: "10px" }}>
                          <strong>{room.room_id}</strong>
                        </td>

                        <td style={{ padding: "10px" }}>
                          <span className={`badge ${modeClass(
                            room.control_mode ?? "Optimized"
                          )}`}>
                            {room.control_mode ?? "Optimized"}
                          </span>
                        </td>

                        <td style={{
                          padding: "10px",
                          textAlign: "right"
                        }}>
                          {fmt(room.current_power_kw, 2, " kW")}
                        </td>

                        <td style={{
                          padding: "10px",
                          textAlign: "right"
                        }}>
                          {fmt(room.optimized_power_kw, 2, " kW")}
                        </td>

                        <td style={{
                          padding: "10px",
                          textAlign: "right"
                        }}>
                          {fmt(room.power_saved_kw, 2, " kW")}
                        </td>

                        <td style={{ padding: "10px" }}>
                          {(room.actions ?? []).join(", ") || "No action"}
                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            )}

          </section>


          {/* =================================================
              LIVE CONTROL COMMANDS
              ================================================= */}

          <h2>
            Live Control Commands
          </h2>


          <section className="card">

            {!liveControl?.rooms?.length ? (

              <div className="empty">
                Waiting for live control data…
              </div>

            ) : (

              <div style={{ overflowX: "auto" }}>

                <table
                  style={{
                    width: "100%",
                    borderCollapse: "collapse"
                  }}
                >

                  <thead>

                    <tr>

                      <th
                        style={{
                          textAlign: "left",
                          padding: "10px"
                        }}
                      >
                        Room
                      </th>

                      <th
                        style={{
                          textAlign: "left",
                          padding: "10px"
                        }}
                      >
                        Control Mode
                      </th>

                      <th
                        style={{
                          textAlign: "left",
                          padding: "10px"
                        }}
                      >
                        HVAC
                      </th>

                      <th
                        style={{
                          textAlign: "left",
                          padding: "10px"
                        }}
                      >
                        Lighting
                      </th>

                      <th
                        style={{
                          textAlign: "left",
                          padding: "10px"
                        }}
                      >
                        Ventilation
                      </th>

                    </tr>

                  </thead>


                  <tbody>

                    {liveControl.rooms.map((room) => (

                      <tr
                        key={room.room_id}
                      >

                        <td
                          style={{
                            padding: "10px"
                          }}
                        >
                          <strong>
                            {room.room_id}
                          </strong>
                        </td>


                        <td
                          style={{
                            padding: "10px"
                          }}
                        >

                          <span
                            className={`badge ${modeClass(
                              room.control_mode
                            )}`}
                          >
                            {room.control_mode}
                          </span>

                        </td>


                        <td
                          style={{
                            padding: "10px"
                          }}
                        >
                          {room.hvac_command}
                        </td>


                        <td
                          style={{
                            padding: "10px"
                          }}
                        >
                          {room.lighting_command}
                        </td>


                        <td
                          style={{
                            padding: "10px"
                          }}
                        >
                          {room.ventilation_command}
                        </td>

                      </tr>

                    ))}

                  </tbody>

                </table>

              </div>

            )}

          </section>


          {/* =================================================
              LIVE CONTROL VERIFICATION
              ================================================= */}

          <h2>
            Live Control Verification
          </h2>

          <section className="card">

            {!liveVerification ? (

              <div className="empty">
                Waiting for live verification data…
              </div>

            ) : (

              <>

                <div className="grid four">

                  <Kpi
                    icon={Zap}
                    label="Current Power"
                    value={fmt(
                      liveVerification.current_power_kw,
                      2,
                      " kW"
                    )}
                    sub="before live control"
                  />

                  <Kpi
                    icon={TrendingDown}
                    label="Optimized Power"
                    value={fmt(
                      liveVerification.optimized_power_kw,
                      2,
                      " kW"
                    )}
                    sub="after live control"
                  />

                  <Kpi
                    icon={TrendingDown}
                    label="Power Saved"
                    value={fmt(
                      liveVerification.power_saved_kw,
                      2,
                      " kW"
                    )}
                    sub="verified simulated saving"
                  />

                  <Kpi
                    icon={ShieldCheck}
                    label="Saving"
                    value={fmt(
                      liveVerification.saving_percentage,
                      2,
                      " %"
                    )}
                    sub={`${liveVerification.improved_rooms ?? 0} of ${liveVerification.total_rooms ?? 0} rooms improved`}
                  />

                </div>


                <div
                  style={{
                    overflowX: "auto",
                    marginTop: "24px"
                  }}
                >

                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse"
                    }}
                  >

                    <thead>

                      <tr>

                        <th
                          style={{
                            textAlign: "left",
                            padding: "10px"
                          }}
                        >
                          Room
                        </th>

                        <th
                          style={{
                            textAlign: "right",
                            padding: "10px"
                          }}
                        >
                          Current
                        </th>

                        <th
                          style={{
                            textAlign: "right",
                            padding: "10px"
                          }}
                        >
                          Optimized
                        </th>

                        <th
                          style={{
                            textAlign: "right",
                            padding: "10px"
                          }}
                        >
                          Saved
                        </th>

                        <th
                          style={{
                            textAlign: "right",
                            padding: "10px"
                          }}
                        >
                          Saving
                        </th>

                        <th
                          style={{
                            textAlign: "left",
                            padding: "10px"
                          }}
                        >
                          Status
                        </th>

                      </tr>

                    </thead>

                    <tbody>

                      {liveVerification.rooms?.map((room) => (

                        <tr key={room.room_id}>

                          <td
                            style={{
                              padding: "10px"
                            }}
                          >
                            <strong>
                              {room.room_id}
                            </strong>
                          </td>

                          <td
                            style={{
                              padding: "10px",
                              textAlign: "right"
                            }}
                          >
                            {fmt(
                              room.current_power_kw,
                              2,
                              " kW"
                            )}
                          </td>

                          <td
                            style={{
                              padding: "10px",
                              textAlign: "right"
                            }}
                          >
                            {fmt(
                              room.optimized_power_kw,
                              2,
                              " kW"
                            )}
                          </td>

                          <td
                            style={{
                              padding: "10px",
                              textAlign: "right"
                            }}
                          >
                            {fmt(
                              room.power_saved_kw,
                              2,
                              " kW"
                            )}
                          </td>

                          <td
                            style={{
                              padding: "10px",
                              textAlign: "right"
                            }}
                          >
                            {fmt(
                              room.saving_percentage,
                              2,
                              " %"
                            )}
                          </td>

                          <td
                            style={{
                              padding: "10px"
                            }}
                          >

                            <span
                              className={`badge ${modeClass(
                                room.verification_status
                              )}`}
                            >
                              {room.verification_status}
                            </span>

                          </td>

                        </tr>

                      ))}

                    </tbody>

                  </table>

                </div>

              </>

            )}

          </section>


          {/* =================================================
              SYSTEM PERFORMANCE METRICS
              ================================================= */}

          <h2>
            System Performance Metrics
          </h2>

          <section className="card" style={{ marginBottom: "20px" }}>
            <div style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              gap: "16px",
              flexWrap: "wrap"
            }}>
              <div>
                <div className="label">Closed-Loop Control Status</div>
                <div style={{ marginTop: "6px", fontWeight: 600 }}>
                  Sense → Predict → Analyze → Optimize → Control → Verify
                </div>
              </div>
              <span className={`badge ${liveMetrics ? "optimized" : "unknown"}`}>
                {liveMetrics ? "Live Metrics Active" : "Waiting for metrics"}
              </span>
            </div>
            {liveMetrics && (
              <div className="sub" style={{ marginTop: "10px" }}>
                Simulation cycle #{liveMetrics.cycles_completed ?? "—"} · Metrics update automatically every 10 seconds
              </div>
            )}
          </section>

          <section className="grid four">
            <Kpi
              icon={Zap}
              label="Current Power"
              value={fmt(liveMetrics?.current_power_kw, 2, " kW")}
              sub="live baseline demand"
            />

            <Kpi
              icon={TrendingDown}
              label="Optimized Power"
              value={fmt(liveMetrics?.optimized_power_kw, 2, " kW")}
              sub="after optimization"
            />

            <Kpi
              icon={TrendingDown}
              label="Power Saved"
              value={fmt(liveMetrics?.power_saved_kw, 2, " kW")}
              sub="verified live saving"
            />

            <Kpi
              icon={ShieldCheck}
              label="Energy Reduction"
              value={fmt(liveMetrics?.saving_percentage, 2, " %")}
              sub="current vs optimized"
            />
          </section>

          <section className="card stats">
            <Stat
              label="Peak Current Demand"
              value={fmt(liveMetrics?.peak_current_power_kw, 2, " kW")}
            />

            <Stat
              label="Peak Demand Reduction"
              value={fmt(liveMetrics?.peak_demand_reduction_kw, 2, " kW")}
            />

            <Stat
              label="Cumulative Energy Saved"
              value={fmt(liveMetrics?.cumulative_energy_saved_kwh, 3, " kWh")}
            />

            <Stat
              label="Optimized Rooms"
              value={fmt(liveMetrics?.optimized_rooms, 0)}
            />

            <Stat
              label="Control Actions"
              value={fmt(liveMetrics?.control_actions, 0)}
            />

            <Stat
              label="Live Anomalies"
              value={fmt(liveMetrics?.anomaly_count, 0)}
            />

            <Stat
              label="Comfort Compliance"
              value={fmt(liveMetrics?.comfort_compliance_percentage, 2, " %")}
            />

            <Stat
              label="CO₂ Compliance"
              value={fmt(liveMetrics?.co2_compliance_percentage, 2, " %")}
            />

            <Stat
              label="Overall Compliance"
              value={fmt(liveMetrics?.overall_compliance_percentage, 2, " %")}
            />

            <Stat
              label="Live Cycles"
              value={fmt(liveMetrics?.cycles_completed, 0)}
            />
          </section>

          {/* =================================================
              VERIFICATION
              ================================================= */}

          <h2>
            Verification
          </h2>


          <section className="card stats three-col">


            <Stat
              label="Temperature Compliance"
              value={fmt(
                verification?.temperature_compliance,
                2,
                " %"
              )}
            />


            <Stat
              label="CO₂ Compliance"
              value={fmt(
                verification?.co2_compliance,
                2,
                " %"
              )}
            />


            <Stat
              label="Overall Compliance"
              value={fmt(
                verification?.overall_compliance,
                2,
                " %"
              )}
            />

          </section>


        </>

      )}

    </div>
  );
}