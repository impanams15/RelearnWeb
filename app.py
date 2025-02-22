"""
Quadropic OSS
https://oss.quadropic.com
Author: [MohamedKamran, hemanthcs34, impanams15]
Date: Feb 22nd 2025
"""

import streamlit as st
import time
import os
from typing import Dict, Any
from dotenv import load_dotenv, set_key
from dataclasses import dataclass
from relearnweb_backend import graph, ResearchAgentState

# Constants
ENV_KEYS = {
    "LLM_ENDPOINT": "",
    "LLM_API_KEY": "",
    "LLM_MODEL_ID": "",
    "FIRECRAWL_API_KEY": ""
}

# Set Page Config
st.set_page_config(
    page_title="RelearnWeb",
    page_icon="🧠",
    layout="centered",
    menu_items={
        "About": """This is a research and learning tool for the web.
A Joint Effort by Quadropic OSS and Open Source Contributers.""",
        "Get Help": "mailto:oss@quadropic.com",
    }
)

def get_theme_css() -> str:
    """Return CSS for dark mode without background images."""
    background_color = "#121212"
    text_color = "#e0e0e0"  # Softer off-white for dark mode
    border_color = "#2c3e50"
    app_background = "rgba(0, 0, 0, 0.9)"
    sidebar_background = "rgba(0, 0, 0, 0.85)"
    button_background = "#2c3e50"
    
    return f"""
    <style>
    body {{
        background-color: {background_color};
        color: {text_color};
    }}
    .stApp {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid {border_color};
        background-color: {app_background};
    }}
    .stSidebar {{
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid {border_color};
        background-color: {sidebar_background};
    }}
    .stButton button {{
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
        border-radius: 5px;
        border: 1px solid {border_color};
        background-color: {button_background};
        color: {text_color};
    }}
    .stHeader {{
        text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.5);
    }}
    </style>
    """

@dataclass
class AppState:
    research_in_progress: bool = False
    show_settings: bool = False
    stop_requested: bool = False
    research_completed: bool = False

def init_session_state():
    """Initialize session state variables."""
    if 'state' not in st.session_state:
        st.session_state.state = AppState()

def load_settings() -> Dict[str, str]:
    """Load settings from .env file."""
    load_dotenv()
    return {key: os.getenv(key, default) for key, default in ENV_KEYS.items()}

def save_settings(settings: Dict[str, str]):
    """Save settings to .env file."""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    for key, value in settings.items():
        set_key(env_path, key, value)

def render_header():
    """Render application header."""
    st.title("RelearnWeb")
    st.write("Research and Learn the Web like a Pro. An FOSS Alternative to OpenAI's DeepResearch.")
    st.write("A Joint Effort by Quadropic OSS and Open Source Contributers")
    st.markdown("[Learn more about Quadropic](https://quadropic.com)")

def render_sidebar() -> Dict[str, Any]:
    """Render sidebar and return research parameters."""
    st.sidebar.header("Research Parameters")
    params = {
        "query": st.sidebar.text_input("Research Query", "Quantum Computing breakthroughs"),
        "depth": st.sidebar.number_input("Depth", value=1, min_value=0, max_value=10),
        "breadth": st.sidebar.number_input("Breadth", value=3, min_value=1, max_value=10)
    }
    return params

def render_settings():
    """Render settings form."""
    with st.form("settings_form"):
        st.subheader("AI Settings Configuration")
        current_settings = load_settings()
        new_settings = {
            key: st.text_input(
                key.replace("_", " ").title(), 
                value=current_settings[key],
                type="password" if "API_KEY" in key else "default"
            ) for key in ENV_KEYS
        }
        save_clicked = st.form_submit_button("Save Settings")
        cancel_clicked = st.form_submit_button("Cancel")
        
        if save_clicked:
            save_settings(new_settings)
            st.success("Settings saved successfully!")
            st.session_state.state.show_settings = False
            st.experimental_rerun()
        elif cancel_clicked:
            st.session_state.state.show_settings = False
            st.experimental_rerun()

def run_research(params: Dict[str, Any]):
    """Execute research pipeline."""
    initial_state = ResearchAgentState(
        depth=params["depth"],
        breadth=params["breadth"],
        query=params["query"],
        results="",
        directions="",
        learnings="",
        report=""
    )
    
    total_steps = 7 + 6 * params["depth"]
    progress_bar = st.progress(0)
    progress_text = st.empty()
    tabs = st.tabs(["Queries", "Next Direction", "Learnings", "Report"])
    
    prev_state = {"query": "", "directions": "", "learnings": "", "report": ""}
    
    for event_counter, event in enumerate(graph.compile().stream(initial_state), 1):
        if st.session_state.state.stop_requested:
            st.warning("Research Stopped by User")
            return
            
        progress = min(int(event_counter / total_steps * 100), 100)
        progress_bar.progress(progress)
        progress_text.text(f"Task {event_counter} of {total_steps} completed.")
        
        event_data = event[next(iter(event))]
        for tab, key in zip(tabs, ["query", "directions", "learnings", "report"]):
            if event_data[key] != prev_state[key]:
                if event_data[key].startswith("```"):
                    event_data[key] = event_data[key].strip("\n ```")
                tab.markdown(f"**{key.title()}:**\n\n{event_data[key]}")
                prev_state[key] = event_data[key]
    
    # After research completes, store the final report for export.
    st.session_state["research_report"] = prev_state["report"]
    st.session_state.state.research_completed = True
    
    # Show success message
    st.success("Research completed successfully! You can now export your research report.")
    
    # Force sidebar to update by creating a download button here as well
    st.sidebar.download_button(
        label="Export Research",
        data=st.session_state["research_report"],
        file_name="research_report.md",
        mime="text/markdown"
    )

def main():
    init_session_state()
    
    # Always apply dark mode theme
    st.markdown(get_theme_css(), unsafe_allow_html=True)
    
    render_header()
    params = render_sidebar()
    
    # Vertical Button Layout in Sidebar
    if st.session_state.state.research_in_progress:
        if st.sidebar.button("🛑 Stop Research"):
            st.session_state.state.stop_requested = True
            st.session_state.state.research_in_progress = False
    else:
        if st.sidebar.button("🚀 Start Research"):
            st.session_state.state.research_in_progress = True
    
    # Only show AI Settings button when research is not in progress
    if not st.session_state.state.research_in_progress:
        if st.sidebar.button("⚙️ AI Settings"):
            st.session_state.state.show_settings = True

    # Show Export Research button if research is completed and report exists,
    # without affecting the ongoing research
    if st.session_state.state.research_completed and "research_report" in st.session_state:
        st.sidebar.download_button(
            label="Export Research",
            data=st.session_state["research_report"],
            file_name="research_report.md",
            mime="text/markdown",
            help="Download your research report without interrupting the current task"
        )
    
    # Only show settings when research is not in progress
    if st.session_state.state.show_settings and not st.session_state.state.research_in_progress:
        render_settings()
    
    if st.session_state.state.research_in_progress:
        run_research(params)
        st.session_state.state.research_completed = True
        st.session_state.state.research_in_progress = False

if __name__ == "__main__":
    main()
