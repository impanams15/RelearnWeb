import streamlit as st
import time
import os
import json
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

# Set Page Config with Dark Mode Toggle Support
st.set_page_config(
    page_title="RelearnWeb",
    page_icon="🧠",
    layout="centered",
    initial_sidebar_state="expanded"
)

@dataclass
class AppState:
    research_in_progress: bool = False
    stop_requested: bool = False
    show_settings: bool = False
    saved_queries: list = None
    feedbacks: list = None

def init_session_state():
    """Initialize session state variables"""
    if 'state' not in st.session_state:
        st.session_state.state = AppState(saved_queries=[], feedbacks=[])

def load_settings() -> Dict[str, str]:
    """Load settings from .env file"""
    load_dotenv()
    return {key: os.getenv(key, default) for key, default in ENV_KEYS.items()}

def save_settings(settings: Dict[str, str]):
    """Save settings to .env file"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    for key, value in settings.items():
        set_key(env_path, key, value)

def render_header():
    """Render application header"""
    st.title("RelearnWeb")
    st.write("Research and Learn the Web like a Pro. An FOSS Alternative to OpenAI's DeepResearch.")
    st.markdown("[Learn more about Quadropic](https://quadropic.com)")

# Dark Mode Toggle
dark_mode = st.sidebar.checkbox("🌙 Enable Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
            body { background-color: #0E1117; color: white; }
        </style>
    """, unsafe_allow_html=True)

def render_sidebar() -> Dict[str, Any]:
    """Render sidebar and return research parameters"""
    st.sidebar.header("Research Parameters")
    query = st.sidebar.text_input("Research Query", "Quantum Computing breakthroughs")
    depth = st.sidebar.number_input("Depth", value=1, min_value=0, max_value=10)
    breadth = st.sidebar.number_input("Breadth", value=3, min_value=1, max_value=10)
    
    if st.sidebar.button("💾 Save Query"):
        if query not in st.session_state.state.saved_queries:
            st.session_state.state.saved_queries.append(query)
            st.sidebar.success("Query saved!")
    
    return {"query": query, "depth": depth, "breadth": breadth}

def run_research(params: Dict[str, Any]):
    """Execute research pipeline"""
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
    st.session_state.state.stop_requested = False
    
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
                tab.markdown(f"**{key.title()}:**\n\n{event_data[key]}")
                prev_state[key] = event_data[key]
        
        time.sleep(0.1)

def export_research():
    """Export research data as JSON"""
    research_data = {
        "saved_queries": st.session_state.state.saved_queries,
        "feedbacks": st.session_state.state.feedbacks
    }
    st.download_button("📥 Export Research", json.dumps(research_data, indent=4), "research_data.json", "application/json")

def collect_feedback():
    """Collect user feedback"""
    feedback = st.text_area("Provide your feedback about the research experience")
    if st.button("Submit Feedback"):
        st.session_state.state.feedbacks.append(feedback)
        st.success("Thank you for your feedback!")

def main():
    init_session_state()
    render_header()
    params = render_sidebar()
    
    col1, col2, col3 = st.sidebar.columns(3)
    with col1:
        if not st.session_state.state.research_in_progress:
            if st.button("⚙️ Configure AI Settings"):
                st.session_state.state.show_settings = True
    
    with col2:
        if not st.session_state.state.research_in_progress:
            if st.button("🚀 Start Research"):
                st.session_state.state.research_in_progress = True
                st.session_state.state.show_settings = False
                run_research(params)
                st.session_state.state.research_in_progress = False
    
    with col3:
        if st.session_state.state.research_in_progress:
            if st.button("🛑 Stop Research"):
                st.session_state.state.stop_requested = True
                st.session_state.state.research_in_progress = False
    
    st.sidebar.subheader("User Feedback")
    collect_feedback()
    export_research()

if __name__ == "__main__":
    main()
