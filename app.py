import math
import streamlit as st

st.set_page_config(
    page_title="FloodGuard AI — Flood Risk Prediction & Early Warning System",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRESETS = {
    "Chennai High-Risk Example": {
        "location": "Chennai",
        "rain_24h": 180.0,
        "rain_forecast_24h": 120.0,
        "river_level": 8.5,
        "river_danger": 10.0,
        "soil_saturation": 85,
        "drainage": "Poor",
        "elevation": "Low-lying",
        "river_distance": 500.0,
    },
    "Moderate Monsoon Alert": {
        "location": "Bengaluru",
        "rain_24h": 65.0,
        "rain_forecast_24h": 55.0,
        "river_level": 5.2,
        "river_danger": 8.0,
        "soil_saturation": 62,
        "drainage": "Moderate",
        "elevation": "Moderate",
        "river_distance": 1800.0,
    },
    "Low-Risk Clear Basin": {
        "location": "Mysuru",
        "rain_24h": 12.0,
        "rain_forecast_24h": 8.0,
        "river_level": 2.4,
        "river_danger": 9.0,
        "soil_saturation": 28,
        "drainage": "Good",
        "elevation": "Elevated",
        "river_distance": 4500.0,
    },
}

DEFAULT_STATE = {
    "location": "Chennai",
    "rain_24h": 180.0,
    "rain_forecast_24h": 120.0,
    "river_level": 8.5,
    "river_danger": 10.0,
    "soil_saturation": 85,
    "drainage": "Poor",
    "elevation": "Low-lying",
    "river_distance": 500.0,
    "submitted_inputs": None,
    "analysis_count": 0,
}

for k, v in DEFAULT_STATE.items():
    if k not in st.session_state:
        st.session_state[k] = v


def apply_preset(preset_name: str):
    p = PRESETS[preset_name]
    st.session_state["location"] = p["location"]
    st.session_state["rain_24h"] = p["rain_24h"]
    st.session_state["rain_forecast_24h"] = p["rain_forecast_24h"]
    st.session_state["river_level"] = p["river_level"]
    st.session_state["river_danger"] = p["river_danger"]
    st.session_state["soil_saturation"] = p["soil_saturation"]
    st.session_state["drainage"] = p["drainage"]
    st.session_state["elevation"] = p["elevation"]
    st.session_state["river_distance"] = p["river_distance"]
    st.session_state["submitted_inputs"] = {
        "location": p["location"],
        "rain_24h": p["rain_24h"],
        "rain_forecast_24h": p["rain_forecast_24h"],
        "river_level": p["river_level"],
        "river_danger": p["river_danger"],
        "soil_saturation": p["soil_saturation"],
        "drainage": p["drainage"],
        "elevation": p["elevation"],
        "river_distance": p["river_distance"],
    }
    st.session_state["analysis_count"] += 1


if st.session_state["submitted_inputs"] is None:
    st.session_state["submitted_inputs"] = {
        "location": st.session_state["location"],
        "rain_24h": st.session_state["rain_24h"],
        "rain_forecast_24h": st.session_state["rain_forecast_24h"],
        "river_level": st.session_state["river_level"],
        "river_danger": st.session_state["river_danger"],
        "soil_saturation": st.session_state["soil_saturation"],
        "drainage": st.session_state["drainage"],
        "elevation": st.session_state["elevation"],
        "river_distance": st.session_state["river_distance"],
    }
    st.session_state["analysis_count"] = 1


def compute_flood_assessment(data: dict) -> dict:
    rain_24h = float(data["rain_24h"])
    rain_fc = float(data["rain_forecast_24h"])
    river_lvl = float(data["river_level"])
    river_danger = max(float(data["river_danger"]), 0.1)
    soil_sat = float(data["soil_saturation"])
    drainage = data["drainage"]
    elevation = data["elevation"]
    river_dist = float(data["river_distance"])

    combined_48h = rain_24h + rain_fc
    river_ratio = river_lvl / river_danger
    clearance_m = river_danger - river_lvl

    # Individual normalized risk scores (0..100)
    rain_score = min(100.0, (rain_24h * 0.22) + (rain_fc * 0.25) + (combined_48h * 0.14))
    river_score = min(100.0, max(0.0, (river_ratio ** 1.45) * 82.0 + (15.0 if river_lvl >= river_danger else 0.0)))
    soil_score = min(100.0, max(0.0, soil_sat * 1.05))

    drainage_map = {"Good": 20.0, "Moderate": 58.0, "Poor": 92.0}
    elevation_map = {"Elevated": 22.0, "Moderate": 55.0, "Low-lying": 90.0}

    drainage_score = drainage_map.get(drainage, 55.0)
    elevation_score = elevation_map.get(elevation, 55.0)

    # Closer to river = higher proximity exposure (0..100)
    proximity_score = min(100.0, max(5.0, 100.0 * math.exp(-river_dist / 2200.0)))

    total_score = (
        0.26 * rain_score
        + 0.24 * river_score
        + 0.15 * soil_score
        + 0.13 * drainage_score
        + 0.11 * elevation_score
        + 0.11 * proximity_score
    )
    risk_score = round(min(99.0, max(2.0, total_score)), 1)

    if risk_score >= 75:
        tier = "CRITICAL FLOOD RISK"
        badge_color = "#dc2626"
        lead_time = "Less than 6 hours"
        summary = (
            f"Severe multi-factor flood hazard detected in {data['location']}. "
            f"Combined 48-hour rainfall is {combined_48h:.0f} mm and river water level is "
            f"{river_lvl:.1f} m against a {river_danger:.1f} m danger threshold."
        )
    elif risk_score >= 52:
        tier = "HIGH FLOOD RISK"
        badge_color = "#ea580c"
        lead_time = "6 to 12 hours"
        summary = (
            f"Elevated flood danger in {data['location']} driven by rainfall accumulation, "
            f"ground saturation, and local drainage or river-stage conditions."
        )
    elif risk_score >= 28:
        tier = "MODERATE FLOOD RISK"
        badge_color = "#d97706"
        lead_time = "12 to 24 hours"
        summary = (
            f"Moderate localized waterlogging or stream-rise potential in {data['location']}. "
            f"Ongoing monitoring is advised as rainfall and runoff evolve."
        )
    else:
        tier = "LOW FLOOD RISK"
        badge_color = "#16a34a"
        lead_time = "24+ hours (Routine Watch)"
        summary = (
            f"Current hydrological and terrain indicators for {data['location']} indicate low "
            f"immediate flood risk under present conditions."
        )

    factors = {
        "Rainfall (24h + Forecast)": round(rain_score, 1),
        "River Stage vs. Danger": round(river_score, 1),
        "Soil Saturation": round(soil_score, 1),
        "Drainage Condition": round(drainage_score, 1),
        "Area Elevation": round(elevation_score, 1),
        "Distance from River": round(proximity_score, 1),
    }

    # 72-hour projected risk trajectory (every 12 hours: 0h to 72h)
    horizons = [0, 12, 24, 36, 48, 60, 72]
    forecast_wave = [1.00, 1.06, 1.09, 1.03, 0.92, 0.80, 0.68]
    projected_scores = [
        round(min(99.0, max(2.0, risk_score * w)), 1) for w in forecast_wave
    ]
    trend_rows = [
        {"Hour": f"+{h}h", "Projected Flood Risk (%)": s}
        for h, s in zip(horizons, projected_scores)
    ]

    if risk_score >= 52:
        citizen_steps = [
            "Avoid low-lying roads, underpasses, and areas near riverbanks or canals.",
            "Move vehicles, valuables, and emergency kits to upper floors or higher ground.",
            "Monitor official municipal and meteorological alerts continuously.",
        ]
        response_steps = [
            "Pre-position rescue boats, dewatering pumps, and emergency shelters in high-risk wards.",
            "Alert ward officers where river clearance is narrow or soil saturation exceeds 75%.",
            "Coordinate traffic diversions away from flooded low-lying corridors.",
        ]
        infra_steps = [
            "Clear drainage inlets, trash screens, and storm culverts ahead of peak runoff.",
            "Run high-capacity stormwater pumping stations at full readiness.",
            "Inspect embankments and floodgates along nearby river stretches.",
        ]
    else:
        citizen_steps = [
            "Keep emergency contact numbers and basic supplies ready during rainy weather.",
            "Avoid parking or walking near storm drains during heavy downpours.",
            "Check local weather updates before travelling through low-lying areas.",
        ]
        response_steps = [
            "Track rainfall forecasts and river gauge readings at regular intervals.",
            "Verify standby equipment and shelter readiness across vulnerable zones.",
            "Maintain coordination channels with local drainage and irrigation teams.",
        ]
        infra_steps = [
            "Carry out routine desilting and inspection of drains and outfalls.",
            "Monitor water levels at retention basins, sluices, and river gauges.",
            "Ensure backup power for critical pumping and monitoring stations.",
        ]

    return {
        "risk_score": risk_score,
        "tier": tier,
        "badge_color": badge_color,
        "lead_time": lead_time,
        "summary": summary,
        "combined_48h": combined_48h,
        "river_ratio_pct": round(river_ratio * 100.0, 1),
        "clearance_m": round(clearance_m, 2),
        "factors": factors,
        "trend_rows": trend_rows,
        "citizen_steps": citizen_steps,
        "response_steps": response_steps,
        "infra_steps": infra_steps,
    }


st.title("🌊 FloodGuard AI — AI-Based Flood Risk Prediction & Early Warning System")
st.caption(
    "Enter location and hydrological criteria on the left, then click **Analyze Flood Risk** "
    "to generate or update the risk assessment on the right."
)

preset_cols = st.columns(3)
with preset_cols[0]:
    if st.button("Load Preset: Chennai High-Risk", use_container_width=True):
        apply_preset("Chennai High-Risk Example")
        st.rerun()
with preset_cols[1]:
    if st.button("Load Preset: Moderate Alert", use_container_width=True):
        apply_preset("Moderate Monsoon Alert")
        st.rerun()
with preset_cols[2]:
    if st.button("Load Preset: Low-Risk Basin", use_container_width=True):
        apply_preset("Low-Risk Clear Basin")
        st.rerun()

left_col, right_col = st.columns([1.05, 1.35], gap="large")

with left_col:
    st.subheader("Input Criteria")
    with st.form("flood_risk_form", clear_on_submit=False):
        location_val = st.text_input("Location", key="location")
        rain_24h_val = st.number_input(
            "Rainfall in last 24 hours (mm)",
            min_value=0.0,
            max_value=1500.0,
            step=5.0,
            key="rain_24h",
        )
        rain_fc_val = st.number_input(
            "Rainfall forecast next 24 hours (mm)",
            min_value=0.0,
            max_value=1500.0,
            step=5.0,
            key="rain_forecast_24h",
        )
        river_lvl_val = st.number_input(
            "River water level (metres)",
            min_value=0.0,
            max_value=100.0,
            step=0.1,
            key="river_level",
        )
        river_danger_val = st.number_input(
            "River danger level (metres)",
            min_value=0.5,
            max_value=100.0,
            step=0.5,
            key="river_danger",
        )
        soil_sat_val = st.slider(
            "Soil saturation (%)",
            min_value=0,
            max_value=100,
            step=1,
            key="soil_saturation",
        )
        drainage_val = st.selectbox(
            "Drainage condition",
            options=["Good", "Moderate", "Poor"],
            key="drainage",
        )
        elevation_val = st.selectbox(
            "Area elevation",
            options=["Low-lying", "Moderate", "Elevated"],
            key="elevation",
        )
        river_dist_val = st.number_input(
            "Distance from river (metres)",
            min_value=0.0,
            max_value=100000.0,
            step=50.0,
            key="river_distance",
        )

        submitted = st.form_submit_button(
            "Analyze Flood Risk",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        cleaned_loc = location_val.strip()
        if not cleaned_loc:
            st.error("Please enter a Location before analyzing. Previous result is kept.")
        else:
            st.session_state["submitted_inputs"] = {
                "location": cleaned_loc,
                "rain_24h": rain_24h_val,
                "rain_forecast_24h": rain_fc_val,
                "river_level": river_lvl_val,
                "river_danger": river_danger_val,
                "soil_saturation": soil_sat_val,
                "drainage": drainage_val,
                "elevation": elevation_val,
                "river_distance": river_dist_val,
            }
            st.session_state["analysis_count"] += 1

    # Check if current draft differs from last analyzed submission
    active = st.session_state["submitted_inputs"]
    has_pending_edits = (
        location_val.strip() != active["location"]
        or float(rain_24h_val) != float(active["rain_24h"])
        or float(rain_fc_val) != float(active["rain_forecast_24h"])
        or float(river_lvl_val) != float(active["river_level"])
        or float(river_danger_val) != float(active["river_danger"])
        or int(soil_sat_val) != int(active["soil_saturation"])
        or drainage_val != active["drainage"]
        or elevation_val != active["elevation"]
        or float(river_dist_val) != float(active["river_distance"])
    )
    if has_pending_edits:
        st.info(
            "Inputs modified — the result on the right stays unchanged until you click **Analyze Flood Risk**."
        )

result = compute_flood_assessment(st.session_state["submitted_inputs"])
analyzed_data = st.session_state["submitted_inputs"]

with right_col:
    st.subheader(f"Risk Assessment — {analyzed_data['location']}")
    st.caption(f"Assessment Run #{st.session_state['analysis_count']}")

    st.markdown(
        f"<div style='padding:14px 18px;border-radius:10px;border-left:6px solid {result['badge_color']};"
        f"background-color:#f8fafc;margin-bottom:12px;'>"
        f"<div style='font-size:13px;font-weight:700;color:{result['badge_color']};'>{result['tier']}</div>"
        f"<div style='font-size:28px;font-weight:800;color:#0f172a;margin:2px 0;'>{result['risk_score']}%</div>"
        f"<div style='font-size:13px;color:#334155;'>{result['summary']}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    m1, m2, m3 = st.columns(3)
    m1.metric("Warning Lead Time", result["lead_time"])
    m2.metric("48h Combined Rain", f"{result['combined_48h']:.0f} mm")
    m3.metric("River Danger Ratio", f"{result['river_ratio_pct']}%")

    tab_overview, tab_trend, tab_case = st.tabs(
        ["Factor Breakdown & Advisories", "72-Hour Trend", "Cloud Case Study"]
    )

    with tab_overview:
        st.markdown("**Contributing Flood Risk Factors (0–100 scale)**")
        st.bar_chart(result["factors"])

        st.markdown("**Actionable Guidance**")
        g1, g2, g3 = st.columns(3)
        with g1:
            st.markdown("**Citizens**")
            for item in result["citizen_steps"]:
                st.markdown(f"- {item}")
        with g2:
            st.markdown("**Disaster Response**")
            for item in result["response_steps"]:
                st.markdown(f"- {item}")
        with g3:
            st.markdown("**Infrastructure**")
            for item in result["infra_steps"]:
                st.markdown(f"- {item}")

    with tab_trend:
        st.markdown("**Projected Flood Risk Trajectory (Next 72 Hours)**")
        chart_df = {row["Hour"]: row["Projected Flood Risk (%)"] for row in result["trend_rows"]}
        st.line_chart(chart_df)
        st.table(result["trend_rows"])

    with tab_case:
        st.markdown("### CAT-03 Case Study Summary")
        st.markdown(
            "**1. Problem Statement:** Evaluating rainfall, river water levels, soil saturation, "
            "drainage, elevation, and distance from the river manually during heavy rain delays early warnings."
        )
        st.markdown(
            st.markdown("**2. Design / Diagram:**").
            
            " User Input Criteria` → `Cloud Web Platform (Streamlit) → "
            " AI Multi-Criteria Flood Risk Engine → Risk Score, 72h Trend & Early Warning Dashboard "
        )
        st.markdown(
            "**3. Flow of the Tool:** Enter the 9 location and hydrological parameters → "
            "click **Analyze Flood Risk** → validate inputs and compute weighted risk score, "
            "lead time, 72-hour trend, and advisories → display results on the dashboard."
        )
        st.markdown(
            "**4. Outcome:** Helps residents, disaster response teams, and infrastructure operators "
            "identify high-risk zones earlier as a decision-support tool alongside human judgment."
        )
