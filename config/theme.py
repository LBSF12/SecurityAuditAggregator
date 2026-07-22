import streamlit as st


def apply_application_theme() -> None:
    """
    Apply the ESAA Microsoft-inspired interface styling.
    """

    st.markdown(
        """
        <style>
            /* Main application */
            .stApp {
                background:
                    linear-gradient(
                        180deg,
                        #f8fafc 0%,
                        #f1f5f9 100%
                    );
            }

            .block-container {
                padding-top: 1.4rem;
                padding-bottom: 3rem;
                max-width: 1500px;
            }

            /* Header */
            .esaa-header {
                position: relative;
                overflow: hidden;
                padding: 1.8rem 2rem;
                margin-bottom: 1.4rem;
                border-radius: 18px;
                background:
                    linear-gradient(
                        135deg,
                        #071b33 0%,
                        #0f3d69 55%,
                        #1264a3 100%
                    );
                box-shadow:
                    0 14px 34px rgba(15, 61, 105, 0.20);
            }

            .esaa-header::after {
                content: "";
                position: absolute;
                width: 240px;
                height: 240px;
                right: -80px;
                top: -100px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.08);
            }

            .esaa-brand-row {
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .esaa-logo {
                display: flex;
                justify-content: center;
                align-items: center;
                width: 58px;
                height: 58px;
                border-radius: 15px;
                background: rgba(255, 255, 255, 0.15);
                font-size: 2rem;
                border: 1px solid rgba(255, 255, 255, 0.20);
            }

            .esaa-header h1 {
                color: #ffffff;
                margin: 0;
                padding: 0;
                font-size: 2rem;
                line-height: 1.2;
                font-weight: 700;
            }

            .esaa-header p {
                color: #dbeafe;
                margin: 0.55rem 0 0 0;
                max-width: 900px;
                font-size: 0.98rem;
            }

            .esaa-badge {
                display: inline-block;
                margin-top: 1rem;
                padding: 0.32rem 0.75rem;
                border-radius: 999px;
                color: #e0f2fe;
                background: rgba(14, 165, 233, 0.20);
                border: 1px solid rgba(186, 230, 253, 0.25);
                font-size: 0.78rem;
                font-weight: 600;
            }

            /* Section cards */
            .esaa-section {
                padding: 1.25rem 1.4rem;
                border-radius: 15px;
                border: 1px solid #dbe3ec;
                background: rgba(255, 255, 255, 0.92);
                box-shadow: 0 5px 18px rgba(15, 23, 42, 0.05);
                margin-bottom: 1rem;
            }

            .esaa-section-title {
                color: #0f2e4f;
                font-size: 1.18rem;
                font-weight: 700;
                margin-bottom: 0.35rem;
            }

            .esaa-section-description {
                color: #64748b;
                font-size: 0.92rem;
                margin-bottom: 0;
            }

            /* Metrics */
            div[data-testid="stMetric"] {
                background: rgba(255, 255, 255, 0.94);
                border: 1px solid #dbe3ec;
                padding: 1rem 1.1rem;
                border-radius: 14px;
                box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
                min-height: 115px;
            }

            div[data-testid="stMetricLabel"] {
                color: #526276;
                font-weight: 600;
            }

            div[data-testid="stMetricValue"] {
                color: #0f2e4f;
                font-weight: 700;
            }

            /* Tabs */
            button[data-baseweb="tab"] {
                font-weight: 600;
            }

            /* Buttons */
            .stButton > button,
            .stDownloadButton > button {
                border-radius: 10px;
                min-height: 2.8rem;
                font-weight: 600;
            }

            /* File uploader */
            div[data-testid="stFileUploader"] {
                padding: 0.4rem;
                border-radius: 14px;
            }

            /* Sidebar */
            section[data-testid="stSidebar"] {
                background:
                    linear-gradient(
                        180deg,
                        #071b33 0%,
                        #0b2948 100%
                    );
            }

            section[data-testid="stSidebar"] * {
                color: #e5eef8;
            }

            section[data-testid="stSidebar"]
            div[data-baseweb="select"] * {
                color: initial;
            }

            section[data-testid="stSidebar"]
            button {
                color: initial;
            }

            .sidebar-brand {
                padding: 0.4rem 0 0.8rem 0;
            }

            .sidebar-brand-title {
                font-size: 1.7rem;
                font-weight: 800;
                color: #ffffff;
            }

            .sidebar-brand-subtitle {
                color: #b8cae0;
                font-size: 0.82rem;
                line-height: 1.4;
                margin-top: 0.2rem;
            }

            .sidebar-section-title {
                color: #ffffff;
                font-size: 0.95rem;
                font-weight: 700;
                margin-top: 0.5rem;
            }

            .sidebar-item {
                color: #c8d7e8;
                font-size: 0.87rem;
                padding: 0.15rem 0;
            }

            /* Dataframe */
            div[data-testid="stDataFrame"] {
                border-radius: 12px;
                overflow: hidden;
                border: 1px solid #dbe3ec;
            }

            /* Mobile layout */
            @media (max-width: 768px) {
                .esaa-header {
                    padding: 1.3rem;
                }

                .esaa-header h1 {
                    font-size: 1.45rem;
                }

                .esaa-logo {
                    width: 48px;
                    height: 48px;
                }
            }
        </style>
        """,
        unsafe_allow_html=True,
    )