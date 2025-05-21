"""
LangGraph Outfit Recommender - Core Logic
This version has a clean implementation to avoid state key conflicts
"""

import os
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from app.tavily_weather_service import get_weather_for_location, AVAILABLE_LOCATIONS

# Load environment variables
load_dotenv()

# Ensure API key is available
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY not found. Please set it in a .env file.")

# --- LLM Setup ---
LLM = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=os.environ["OPENAI_API_KEY"])

# --- State Definition ---
class OutfitState(TypedDict):
    """State schema for the outfit recommendation graph."""
    # User inputs
    height: Annotated[str, "User height"]
    gender: Annotated[str, "User gender"]
    location: Annotated[str, "User location (Indian state)"]
    occasion: Annotated[str, "Occasion for the outfit"]
    mood: Annotated[str, "Desired mood for the outfit"]
    
    # Derived data
    weather: Annotated[Dict[str, Any], "Weather information"]
    recommendation: Annotated[str, "Outfit recommendation"]
    rating: Annotated[int, "User rating (1-10)"]
    attempts: Annotated[int, "Number of recommendation attempts made"]
    max_attempts: Annotated[int, "Maximum number of attempts allowed"]
    result_message: Annotated[str, "Final output message"] # Changed name from final_message
    log: Annotated[List[str], "Running log of graph execution"]

# --- Graph Nodes ---
def get_weather(state: OutfitState) -> Dict:
    """Fetches weather information for the specified location using Tavily search API."""
    location = state.get("location", "Default")
    
    # Fetch weather from API
    weather_info = get_weather_for_location(location)
    
    # Log the data source (API or fallback)
    source = weather_info.get("data_source", "fallback")
    log_entry = f"Node: get_weather - Location: {location}, Weather: {weather_info['temp_c']}°C, {weather_info['condition']} (Source: {source})"
    logs = state.get("log", [])
    
    return {"weather": weather_info, "log": logs + [log_entry]}

def generate_outfit(state: OutfitState) -> Dict:
    """Generates outfit recommendation using LLM."""
    # Extract required fields from state
    height = state["height"]
    gender = state["gender"]
    location = state["location"]
    occasion = state["occasion"]
    mood = state["mood"]
    weather = state["weather"]
    
    # Increment attempt counter
    attempt = state.get("attempts", 0) + 1
    
    # Prepare prompt
    prompt = f"""You are a fashion stylist AI. Generate a specific and actionable outfit recommendation for the following user profile and context.
Be creative but practical. Output only the outfit recommendation, nothing else.

User Profile:
- Height: {height}
- Gender: {gender}

Context:
- Location: {location}
- Occasion: {occasion}
- Desired Mood: {mood}
- Current Weather: {weather['temp_c']}°C, {weather['condition']}

Previous Attempt Number: {attempt-1} (if > 0, try something different from previous attempts if possible).

Outfit Recommendation:"""

    # Log the prompt (truncated for cleaner logs)
    log_entry = f"Node: generate_outfit - Attempt: {attempt} - Calling LLM with prompt for {gender}, {occasion}, {mood}"
    logs = state.get("log", [])
    logs.append(log_entry)
    
    # Call the LLM
    try:
        response = LLM.invoke([HumanMessage(content=prompt)])
        recommendation = response.content.strip()
        log_entry_resp = f"Node: generate_outfit - LLM generated recommendation (length: {len(recommendation)})"
    except Exception as e:
        recommendation = f"Sorry, I couldn't generate a recommendation due to an error."
        log_entry_resp = f"Node: generate_outfit - Error: {str(e)}"
    
    # Return updated state
    return {
        "recommendation": recommendation, 
        "attempts": attempt,
        "log": logs + [log_entry_resp]
    }

def check_rating(state: OutfitState) -> str:
    """Determines whether to retry or finish based on rating and attempts."""
    rating = state.get("rating", 0)
    attempts = state.get("attempts", 0)
    max_attempts = state.get("max_attempts", 5)
    
    logs = state.get("log", [])
    log_entry = f"Node: check_rating - Rating: {rating}, Attempts: {attempts}/{max_attempts}"
    logs.append(log_entry)
    
    if rating >= 7:
        decision = "generate_result"
        log_entry_decision = f"Decision: Rating is satisfactory ({rating} >= 7). Proceeding to generate result."
    elif attempts >= max_attempts:
        decision = "generate_result"
        log_entry_decision = f"Decision: Maximum attempts reached ({attempts}). Proceeding to generate result."
    else:
        decision = "generate_outfit"
        log_entry_decision = f"Decision: Rating too low ({rating} < 7) and attempts < {max_attempts}. Trying again."
    
    logs.append(log_entry_decision)
    state["log"] = logs
    
    return decision

def generate_result(state: OutfitState) -> Dict:
    """Generates the final result message."""
    rating = state.get("rating", 0)
    attempts = state.get("attempts", 0)
    max_attempts = state.get("max_attempts", 5)
    recommendation = state.get("recommendation", "No recommendation generated")
    
    if rating >= 7:
        result = f"Perfect outfit found after {attempts} attempt(s)! 🎉\n\nFinal Recommendation:\n{recommendation}"
    else:
        result = f"Sorry, we couldn't find the perfect outfit after {max_attempts} attempts. 💔\n\nLast Recommendation:\n{recommendation}"
    
    logs = state.get("log", [])
    log_entry = f"Node: generate_result - Creating final message"
    
    return {
        "result_message": result,
        "log": logs + [log_entry]
    }

# --- Graph Definition ---
def create_graph():
    """Creates the LangGraph workflow."""
    # Create a new graph
    workflow = StateGraph(OutfitState)
    
    # Add nodes
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("generate_outfit", generate_outfit)
    workflow.add_node("generate_result", generate_result)
    
    # Define entry point
    workflow.set_entry_point("get_weather")
    
    # Add regular edges
    workflow.add_edge("get_weather", "generate_outfit")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "generate_outfit",
        check_rating,
        {
            "generate_outfit": "generate_outfit",
            "generate_result": "generate_result"
        }
    )
    
    # Add final edge
    workflow.add_edge("generate_result", END)
    
    return workflow

# Compile the graph
app_graph = create_graph()
app = app_graph.compile()

# Example usage for testing
if __name__ == "__main__":
    print("Testing the outfit recommendation graph...")
    
    # Create test input
    test_input = {
        "height": "5'10\"",
        "gender": "Male",
        "location": "Mumbai",
        "occasion": "Party",
        "mood": "Confident",
        "rating": 0,
        "attempts": 0,
        "max_attempts": 3,
        "log": ["Starting test..."],
        "weather": {},
        "recommendation": "",
        "result_message": ""  # Note: using result_message instead of final_message
    }
    
    # Run the graph
    result = app.invoke(test_input)
    
    # Print the result
    print("\nRecommendation:", result.get("recommendation"))
    print("\nAttempts:", result.get("attempts"))
    print("\nLog entries:", len(result.get("log", []))) 