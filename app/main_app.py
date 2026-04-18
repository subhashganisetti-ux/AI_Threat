import time

import cv2
import streamlit as st

from alert_service import send_alert
from vision_pipeline import process_frame

CAPTURE_COUNT = 3
CAPTURE_INTERVAL_SECONDS = 1
MAJORITY_THRESHOLD = 2


st.set_page_config(
    page_title="ForestEye Threat Console",
    page_icon=":deciduous_tree:",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles():
    st.markdown(
        """
        <style>
            .stApp {
                background:
                    radial-gradient(circle at top left, rgba(97, 142, 116, 0.18), transparent 30%),
                    radial-gradient(circle at top right, rgba(211, 151, 72, 0.14), transparent 32%),
                    linear-gradient(180deg, #f6f1e8 0%, #ece3d4 100%);
                color: #1f2a1f;
            }

            .block-container {
                padding-top: 2rem;
                padding-bottom: 2rem;
            }

            .hero-panel {
                background: linear-gradient(135deg, rgba(25, 54, 39, 0.96), rgba(58, 90, 64, 0.92));
                border: 1px solid rgba(235, 228, 214, 0.25);
                border-radius: 24px;
                padding: 2rem;
                color: #f7f3eb;
                box-shadow: 0 24px 60px rgba(28, 39, 29, 0.18);
            }

            .hero-kicker {
                letter-spacing: 0.18rem;
                font-size: 0.8rem;
                text-transform: uppercase;
                opacity: 0.72;
                margin-bottom: 0.6rem;
            }

            .hero-title {
                font-size: 2.5rem;
                line-height: 1.05;
                font-weight: 700;
                margin-bottom: 0.75rem;
            }

            .hero-subtitle {
                font-size: 1rem;
                line-height: 1.65;
                max-width: 48rem;
                opacity: 0.9;
            }

            .info-card {
                background: rgba(248, 244, 236, 0.88);
                border: 1px solid rgba(74, 95, 70, 0.14);
                border-radius: 20px;
                padding: 1.2rem 1.1rem;
                box-shadow: 0 14px 30px rgba(55, 69, 56, 0.08);
                min-height: 8.4rem;
            }

            .info-label {
                color: #5c6a57;
                font-size: 0.82rem;
                text-transform: uppercase;
                letter-spacing: 0.12rem;
                margin-bottom: 0.35rem;
            }

            .info-value {
                color: #1e2d1e;
                font-size: 1.6rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }

            .info-caption {
                color: #58655a;
                font-size: 0.95rem;
                line-height: 1.45;
            }

            .status-shell {
                border-radius: 18px;
                padding: 1rem 1.1rem;
                border: 1px solid transparent;
                font-weight: 600;
                margin-bottom: 0.75rem;
            }

            .status-neutral {
                background: rgba(241, 234, 220, 0.88);
                border-color: rgba(125, 106, 79, 0.18);
                color: #5c4a35;
            }

            .status-safe {
                background: rgba(220, 238, 224, 0.9);
                border-color: rgba(55, 124, 82, 0.18);
                color: #1f6a3c;
            }

            .status-threat {
                background: rgba(248, 221, 217, 0.92);
                border-color: rgba(162, 69, 59, 0.18);
                color: #9c2f22;
            }

            .frame-card {
                background: rgba(251, 248, 243, 0.92);
                border: 1px solid rgba(74, 95, 70, 0.14);
                border-radius: 20px;
                padding: 0.9rem;
                box-shadow: 0 16px 34px rgba(55, 69, 56, 0.08);
            }

            .frame-title {
                font-weight: 700;
                color: #213022;
                margin-bottom: 0.6rem;
                font-size: 1rem;
            }

            .frame-meta {
                margin-top: 0.75rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
                gap: 0.5rem;
                flex-wrap: wrap;
            }

            .badge {
                border-radius: 999px;
                padding: 0.28rem 0.75rem;
                font-size: 0.82rem;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 0.05rem;
            }

            .badge-safe {
                background: rgba(34, 139, 83, 0.13);
                color: #1f7d47;
            }

            .badge-threat {
                background: rgba(179, 51, 39, 0.14);
                color: #a12f23;
            }

            .badge-neutral {
                background: rgba(125, 106, 79, 0.12);
                color: #74583b;
            }

            .confidence-text {
                color: #536052;
                font-size: 0.92rem;
                font-weight: 600;
            }

            .sidebar-card {
                background: rgba(249, 245, 236, 0.92);
                border: 1px solid rgba(74, 95, 70, 0.12);
                border-radius: 18px;
                padding: 1rem;
                color: #2d3c2d;
            }

            @media (max-width: 900px) {
                .hero-title {
                    font-size: 2rem;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        """
        <div class="hero-panel">
            <div class="hero-kicker">ForestEye Monitoring</div>
            <div class="hero-title">Threat Detection Console</div>
            <div class="hero-subtitle">
                A cleaner live dashboard for running the existing pose-based pipeline,
                reviewing frame-level decisions, and surfacing alert delivery status in one place.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_overview():
    cards = st.columns(4)
    card_data = [
        ("Capture Window", str(CAPTURE_COUNT), "Frames collected before the final decision is made."),
        ("Capture Interval", f"{CAPTURE_INTERVAL_SECONDS}s", "Small pause between frames to sample movement."),
        ("Decision Rule", "Majority Vote", "Threat is raised when at least two frames are flagged."),
        ("Alert Target", "Local Endpoint", "Escalates to the configured alert service when threat wins."),
    ]

    for column, (label, value, caption) in zip(cards, card_data):
        with column:
            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-label">{label}</div>
                    <div class="info-value">{value}</div>
                    <div class="info-caption">{caption}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_sidebar():
    with st.sidebar:
        st.markdown("### Session Notes")
        st.markdown(
            """
            <div class="sidebar-card">
                The UI has been refreshed, but the webcam capture and frame classification
                flow remains aligned with the original implementation.
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        st.caption("Run detection from the main panel whenever the camera is ready.")

        if st.session_state.get("last_run"):
            last_run = st.session_state["last_run"]
            st.markdown("### Latest Run")
            st.metric("Final Result", last_run["final_label"])
            st.metric("Threat Votes", last_run["threat_votes"], delta=f"{last_run['safe_votes']} safe")
            st.caption(last_run["alert_message"])


def render_status(container, message, tone="neutral"):
    tone_map = {
        "neutral": "status-neutral",
        "safe": "status-safe",
        "threat": "status-threat",
    }
    container.markdown(
        f'<div class="status-shell {tone_map.get(tone, "status-neutral")}">{message}</div>',
        unsafe_allow_html=True,
    )


def render_frame_result(column, index, frame, result, probability):
    badge_class = {
        "Threat": "badge-threat",
        "Safe": "badge-safe",
    }.get(result, "badge-neutral")

    with column:
        st.markdown(f'<div class="frame-title">Capture {index}</div>', unsafe_allow_html=True)
        st.image(frame, channels="BGR", use_container_width=True)
        st.markdown(
            f"""
            <div class="frame-card">
                <div class="frame-meta">
                    <span class="badge {badge_class}">{result}</span>
                    <span class="confidence-text">Confidence {probability:.2f}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(probability)


def run_detection_cycle():
    status_box = st.empty()
    progress_bar = st.progress(0.0)
    capture_columns = st.columns(CAPTURE_COUNT)

    render_status(status_box, "Connecting to camera and preparing capture window.")
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        progress_bar.empty()
        render_status(status_box, "Camera not accessible. Check permissions or device availability.", "threat")
        return

    frames = []

    for index in range(CAPTURE_COUNT):
        render_status(status_box, f"Capturing frame {index + 1} of {CAPTURE_COUNT}.")
        ret, frame = cap.read()
        if ret:
            frames.append(frame)
        progress_bar.progress((index + 1) / (CAPTURE_COUNT * 2))
        time.sleep(CAPTURE_INTERVAL_SECONDS)

    cap.release()

    if not frames:
        progress_bar.empty()
        render_status(status_box, "No frames were captured from the webcam feed.", "threat")
        return

    results = []
    threat_votes = 0

    for index, frame in enumerate(frames):
        render_status(status_box, f"Analyzing capture {index + 1} of {len(frames)}.")
        result, probability = process_frame(frame)
        probability = max(0.0, min(float(probability), 1.0))

        if result == "Threat":
            threat_votes += 1

        results.append(
            {
                "frame": frame,
                "result": result,
                "probability": probability,
            }
        )
        render_frame_result(capture_columns[index], index + 1, frame, result, probability)
        progress_bar.progress((CAPTURE_COUNT + index + 1) / (CAPTURE_COUNT * 2))

    for index in range(len(results), CAPTURE_COUNT):
        with capture_columns[index]:
            st.info("Frame unavailable for this capture slot.")

    safe_votes = len(results) - threat_votes
    threat_detected = threat_votes >= MAJORITY_THRESHOLD

    if threat_detected:
        alert_success, alert_message = send_alert(threat_votes)
        render_status(status_box, "Final result: THREAT DETECTED", "threat")
    else:
        alert_success = True
        alert_message = "No external alert sent because the run was classified as safe."
        render_status(status_box, "Final result: SAFE", "safe")

    progress_bar.progress(1.0)

    alert_status = "Sent" if threat_detected and alert_success else "Failed" if threat_detected else "Not Sent"

    summary_columns = st.columns(3)
    summary_columns[0].metric("Threat Votes", threat_votes)
    summary_columns[1].metric("Safe Votes", safe_votes)
    summary_columns[2].metric("Alert Status", alert_status)

    if threat_detected and alert_success:
        st.success(alert_message)
    elif threat_detected:
        st.warning(alert_message)
    else:
        st.info(alert_message)

    st.session_state["last_run"] = {
        "final_label": "THREAT" if threat_detected else "SAFE",
        "threat_votes": threat_votes,
        "safe_votes": safe_votes,
        "alert_message": alert_message,
    }


inject_styles()

if "last_run" not in st.session_state:
    st.session_state["last_run"] = None

render_sidebar()
render_header()
st.write("")
render_overview()
st.write("")

button_columns = st.columns([1, 1.6, 1])
with button_columns[1]:
    start_detection = st.button("Start Detection", type="primary", use_container_width=True)

st.caption("The pipeline still captures three frames, classifies each one, and makes a majority-vote decision.")
st.divider()

if start_detection:
    run_detection_cycle()
elif st.session_state["last_run"]:
    last_run = st.session_state["last_run"]
    tone = "threat" if last_run["final_label"] == "THREAT" else "safe"
    render_status(
        st.empty(),
        f"Latest completed run: {last_run['final_label']} with {last_run['threat_votes']} threat vote(s).",
        tone,
    )
