from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from utils.llm import generate_llm_response
from utils.firecrawler import crawl_firechain

# -------------------------------
# Define the Research Agent State
# -------------------------------

# Define the custom state structure for the research agent.
class ResearchAgentState(TypedDict):
    depth: int
    breadth: int
    query: str
    results: str
    directions: str
    learnings: str
    report: str

# Node: Input Node (initializes or verifies state parameters)
def input_node(state: ResearchAgentState) -> ResearchAgentState:
    # You can modify or confirm state values here if needed.
    return state

# Node: Deep Research - perform initial research using the query.
def learner_node(state: ResearchAgentState) -> ResearchAgentState:
    prompt = (
        f"You are a research assistant. We have a query: '{state['query']}'.\n"
        f"Depth: {state['depth']}, Breadth: {state['breadth']}.\n"
        "Generate an outline of subtopics or steps to research deeply."
        "First talk about the goal of the research that this query is meant to accomplish, then go deeper into how to advance the research once the results are found, mention additional research directions. Be as specific as possible, especially for additional research directions.",
        f"Previous Learnings and Directions:\n{state['learnings']}\n{state['directions']}"
    )
    response = generate_llm_response(system_prompt=prompt, user_prompt = prompt, streaming=False)
    outline = response
    state["results"] = f"Initial Outline:\n{outline}"
    return state

# Node: SERP Queries - simulate search engine queries.
def serp_queries(state: ResearchAgentState) -> ResearchAgentState:
    numqueries = 2
    prompt = f"Given the following prompt from the user, generate a list of SERP queries to research the topic. Return a maximum of ${numqueries} queries, but feel free to return less if the original prompt is clear. Make sure each query is unique and not similar to each other:"
    res = generate_llm_response(system_prompt=prompt,user_prompt=prompt)
    state["queries"] = res
    return state

# Node: Process Results - summarize the collected research.
def process_results(state: ResearchAgentState) -> ResearchAgentState:
    search_results = crawl_firechain(state["queries"])
    state["results"] = search_results
    prompt = (
        "Summarize the following research findings in bullet points. "
        "Highlight key learnings and potential directions.\n\n"
        f"{state['results']}"
    )
    summary = generate_llm_response(system_prompt=prompt, user_prompt=prompt)
    state["learnings"] = summary
    return state

# Node: Compile Results - generate potential directions based on the learnings.
def compile_results(state: ResearchAgentState) -> ResearchAgentState:
    prompt = (
        f"Based on these learnings:\n{state['learnings']}\n"
        "List 3 next directions or deeper questions to explore."
    )
    response = generate_llm_response(system_prompt=prompt, user_prompt=prompt)
    state["directions"] = response
    return state

# Node: Check Depth - conditional function to decide the next node.
def check_depth(state: ResearchAgentState):
    # If depth is still greater than 0, return the key for the next direction.
    # Otherwise, return the key for compiling the final report.
    return "next_direction" if state["depth"] > 0 else "markdown_report"

# Node: Next Direction - refine the query and reduce the depth.
def next_direction(state: ResearchAgentState) -> ResearchAgentState:
    state["depth"] -= 1  # Decrement depth
    state["query"] = f"{state['query']} + (refined with new subtopics)"
    return state

# Node: Markdown Report - compile the final report.
def markdown_report(state: ResearchAgentState) -> ResearchAgentState:
    md_report = (
        f"-Final Report\n\n"
        f"- Query\n{state['query']}\n\n"
        f"- Key Learnings\n{state['learnings']}\n\n"
    )
    report_prompt = (
        "Generate a markdown report based on the research findings. "
        "Include the query, key learnings, and potential solutions you have found."
        f"{md_report}"
    )
    md_report_llm = generate_llm_response(system_prompt=report_prompt, user_prompt=report_prompt)
    state["report"] = md_report_llm
    return state

# -------------------------------
# Build the LangGraph state graph
# -------------------------------
graph = StateGraph(state_schema=ResearchAgentState)

# Add nodes to the graph.
graph.add_node("input", input_node)
graph.add_node("learner_node", learner_node)
graph.add_node("serp_queries", serp_queries)
graph.add_node("process_results", process_results)
graph.add_node("compile_results", compile_results)
graph.add_node("check_depth", lambda state: state)  # 'check_depth' node passes state unchanged.
graph.add_node("next_direction", next_direction)
graph.add_node("markdown_report", markdown_report)

# Define explicit edges between nodes.
graph.add_edge(START, "input")
graph.add_edge("input", "learner_node")
graph.add_edge("learner_node", "serp_queries")
graph.add_edge("serp_queries", "process_results")
graph.add_edge("process_results", "compile_results")
graph.add_edge("compile_results", "check_depth")

# Add conditional edges: the 'check_depth' node uses the `check_depth` function to decide the next step.
graph.add_conditional_edges(
    "check_depth", 
    check_depth, 
    path_map={
        "next_direction": "next_direction",
        "markdown_report": "markdown_report"
    }
)

# Connect the 'next_direction' node back to 'learner_node' for further iterations.
graph.add_edge("next_direction", "learner_node")

# Finally, connect the 'markdown_report' node to END.
graph.add_edge("markdown_report", END)

# ---------------------------------
# Execute the graph with an initial state.
# ---------------------------------
initial_state: ResearchAgentState = {
    "depth": 1,  # For example, perform one round of refinement.
    "breadth": 3,
    "query": "Quantum Computing breakthroughs",
    "results": "",
    "directions": "",
    "learnings": "",
    "report": ""
}

final_state = graph.compile()

for event in final_state.stream(initial_state):
    for value in event.values():
        print(value)
        print("-" * 10)