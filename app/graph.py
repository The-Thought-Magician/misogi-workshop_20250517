import os
from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import random

load_dotenv()

# Ensure environment variables are set
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY not found in environment variables. Please set it in a .env file.")


class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        height: User's height.
        gender: User's gender.
        location: User's selected location (Indian state).
        occasion: The occasion for the outfit.
        mood: User's desired mood.
        weather: Simulated weather information for the location.
        recommendation: The generated outfit recommendation.
        rating: User's rating for the recommendation (1-10).
        attempts: Number of recommendation attempts made.
        max_attempts: Maximum number of attempts allowed.
        final_message: The final message to display to the user.
        log: A list to store messages and decisions for the running log.
    """
    height: Annotated[str, "User height"]
    gender: Annotated[str, "User gender"]
    location: Annotated[str, "User location (Indian state)"]
    occasion: Annotated[str, "Occasion for the outfit"]
    mood: Annotated[str, "Desired mood for the outfit"]
    weather: Annotated[Dict[str, Any], "Weather information"] # Example: {'temp': 25, 'condition': 'Sunny'}
    recommendation: Annotated[str, "Outfit recommendation"]
    rating: Annotated[int, "User rating (1-10)"]
    attempts: Annotated[int, "Number of attempts made"]
    max_attempts: Annotated[int, "Maximum allowed attempts"]
    final_message: Annotated[str, "Final output message"]
    log: Annotated[List[str], "Running log of graph execution"]

# --- Weather Simulation ---
# A simple dictionary to simulate weather conditions for different Indian states.
# Feel free to expand this!
SIMULATED_WEATHER = {
    "Delhi": {"temp_c": 35, "condition": "Sunny and Hot"},
    "Mumbai": {"temp_c": 28, "condition": "Humid and Cloudy"},
    "Bangalore": {"temp_c": 25, "condition": "Pleasant and Breezy"},
    "Chennai": {"temp_c": 32, "condition": "Hot and Humid"},
    "Kolkata": {"temp_c": 30, "condition": "Warm and Rainy"},
    "Rajasthan": {"temp_c": 40, "condition": "Very Hot and Dry"},
    "Kerala": {"temp_c": 29, "condition": "Tropical and Humid"},
    "Default": {"temp_c": 27, "condition": "Moderate"} # Default fallback
}

# --- LLM Setup ---
# Using OpenAI GPT-4o Mini
# Remember to have OPENAI_API_KEY in your .env file
LLM = ChatOpenAI(temperature=0, model_name="gpt-4o-mini", openai_api_key=os.environ["OPENAI_API_KEY"])


# --- Graph Nodes ---

def fetch_weather_node(state: GraphState) -> dict:
    """
    Simulates fetching weather based on the location in the state.
    Updates the 'weather' field in the state and adds a log entry.
    """
    location = state.get("location", "Default")
    weather_info = SIMULATED_WEATHER.get(location, SIMULATED_WEATHER["Default"])
    
    log_entry = f"Node: fetch_weather - Location: {location}, Fetched Weather: {weather_info}"
    print(log_entry) # Also print to console for debugging

    # Ensure the log list exists before appending
    current_log = state.get("log", [])
    
    return {"weather": weather_info, "log": current_log + [log_entry]}

def generate_outfit_node(state: GraphState) -> dict:
    """
    Generates an outfit recommendation using the LLM based on user inputs and weather.
    Updates the 'recommendation' and 'attempts' fields in the state and adds log entries.
    """
    height = state["height"]
    gender = state["gender"]
    location = state["location"]
    occasion = state["occasion"]
    mood = state["mood"]
    weather = state["weather"]
    attempts = state.get("attempts", 0) + 1 # Increment attempt counter

    # Prepare the prompt for the LLM
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

Previous Attempt Number: {attempts-1} (if > 0, try something different from previous attempts if possible, though user feedback isn't directly provided here).

Outfit Recommendation:"""

    log_entry_prompt = f"Node: generate_outfit - Attempt: {attempts} - Calling LLM (OpenAI {LLM.model_name}) with prompt:\n{prompt[:300]}..." # Truncate prompt for log
    print(log_entry_prompt)
    current_log = state.get("log", [])
    current_log.append(log_entry_prompt)

    # Call the LLM
    try:
        response = LLM.invoke([HumanMessage(content=prompt)])
        recommendation = response.content.strip()
    except Exception as e:
        error_message = f"Error calling OpenAI LLM: {e}"
        print(error_message)
        current_log.append(error_message)
        recommendation = "Sorry, I couldn't generate a recommendation due to an error with the AI model."

    log_entry_response = f"Node: generate_outfit - LLM Response: {recommendation}"
    print(log_entry_response)
    current_log.append(log_entry_response)

    return {"recommendation": recommendation, "attempts": attempts, "log": current_log}

def retry_or_finish_node(state: GraphState) -> str:
    """
    Determines the next step based on the user's rating and the number of attempts.

    Returns:
        "generate_outfit": If rating < 7 and attempts < max_attempts.
        "final_message": If rating >= 7 or attempts >= max_attempts.
    """
    rating = state.get("rating", 0) # Default to 0 if not provided yet
    attempts = state["attempts"]
    max_attempts = state["max_attempts"]

    log_entry = f"Node: retry_or_finish - Rating: {rating}, Attempts: {attempts}/{max_attempts}"
    print(log_entry)
    current_log = state.get("log", [])
    current_log.append(log_entry)

    if rating >= 7:
        decision = "final_message"
        log_entry_decision = "Node: retry_or_finish - Decision: Rating >= 7. Proceeding to final message."
    elif attempts >= max_attempts:
        decision = "final_message"
        log_entry_decision = f"Node: retry_or_finish - Decision: Max attempts ({max_attempts}) reached. Proceeding to final message."
    else:
        decision = "generate_outfit"
        log_entry_decision = f"Node: retry_or_finish - Decision: Rating < 7 and attempts < {max_attempts}. Retrying outfit generation."

    print(log_entry_decision)
    current_log.append(log_entry_decision)

    # NOTE: This node *only* returns the decision string for the conditional edge.
    # It needs to update the log *in place* if we want the log update reflected,
    # because returning just the string won't merge back into the state.
    # A better practice might be to have a separate node just for logging if needed here,
    # or accept that this node's log update happens but isn't stored back unless handled carefully.
    # For simplicity now, we print and append, assuming state is managed by graph execution.
    # We return *only* the edge name. LangGraph handles state updates from nodes that return dicts.

    return decision

def final_message_node(state: GraphState) -> dict:
    """
    Generates the final message based on the last rating and attempt count.
    Updates the 'final_message' field in the state and adds a log entry.
    """
    rating = state.get("rating", 0)
    attempts = state["attempts"]
    max_attempts = state["max_attempts"]
    recommendation = state["recommendation"] # Get the last recommendation

    if rating >= 7:
        final_message = f"Perfect outfit found after {attempts} attempt(s)! 🎉\n\nFinal Recommendation:\n{recommendation}"
    else:
        # This branch is reached if attempts >= max_attempts and rating < 7
        final_message = f"Sorry, we couldn't find the perfect outfit after {max_attempts} attempts. 💔\n\nLast Recommendation:\n{recommendation}"

    log_entry = f"Node: final_message - Generating final message: {final_message}"
    print(log_entry)
    current_log = state.get("log", [])

    return {"final_message": final_message, "log": current_log + [log_entry]}

# --- Graph Definition ---

def create_graph() -> StateGraph:
    """Creates and configures the LangGraph StateGraph."""
    workflow = StateGraph(GraphState)

    # Add the nodes
    workflow.add_node("fetch_weather", fetch_weather_node)
    workflow.add_node("generate_outfit", generate_outfit_node)
    workflow.add_node("final_message", final_message_node)

    # Set the entry point
    # The user inputs (height, gender, location, etc.) are expected to be in the initial state
    workflow.set_entry_point("fetch_weather")

    # Add edges
    workflow.add_edge("fetch_weather", "generate_outfit")

    # Add the conditional edge
    # After generating an outfit, we decide whether to retry or finish
    workflow.add_conditional_edges(
        "generate_outfit", # Source node
        retry_or_finish_node, # Function that returns the next node name
        {
            "generate_outfit": "generate_outfit", # If "generate_outfit" is returned, loop back
            "final_message": "final_message"    # If "final_message" is returned, go to final message
        }
    )

    # The final message node leads to the end
    workflow.add_edge("final_message", END)

    return workflow

# --- Compile the Graph ---
# We create an instance of the graph and compile it.
# This compiled graph ('app') is what the UI will interact with.

app_graph = create_graph()
app = app_graph.compile()

# --- Example Usage (for testing) ---
if __name__ == "__main__":
    # This block allows testing the graph logic directly if the file is run as a script
    print("Testing graph execution...")

    # Define initial inputs simulating UI interaction
    initial_state = {
        "height": "5'10\"",
        "gender": "Male",
        "location": "Bangalore",
        "occasion": "Daily Casual",
        "mood": "Relaxed",
        "rating": 0, # Start with 0 rating
        "attempts": 0,
        "max_attempts": 5,
        "log": ["Initial state created."]
    }

    # Stream events to see the flow
    config = {"recursion_limit": 10} # Increase recursion limit for loops

    # Simulate the first run (generate first outfit)
    print("\n--- First Recommendation ---")
    # Note: Use stream or invoke. Stream is better for observing intermediate steps.
    # We'll use invoke here for simplicity in testing, but Streamlit will use stream.
    final_state_after_first_rec = app.invoke(initial_state, config=config)
    print("\n--- State after first recommendation ---")
    print(f"Recommendation: {final_state_after_first_rec.get('recommendation')}")
    print(f"Attempts: {final_state_after_first_rec.get('attempts')}")
    print(f"Log: \n" + "\n".join(final_state_after_first_rec.get('log', [])))


    # Simulate giving a bad rating (e.g., 5) and running again
    print("\n--- Simulating Rating (5) and Retrying ---")
    state_after_rating = final_state_after_first_rec.copy()
    state_after_rating["rating"] = 5 # Update rating
    state_after_rating["log"].append("User rated the outfit: 5")

    final_state_after_retry = app.invoke(state_after_rating, config=config)
    print("\n--- State after second recommendation (after rating 5) ---")
    print(f"Recommendation: {final_state_after_retry.get('recommendation')}")
    print(f"Attempts: {final_state_after_retry.get('attempts')}")
    print(f"Log: \n" + "\n".join(final_state_after_retry.get('log', [])))


    # Simulate giving a good rating (e.g., 8)
    print("\n--- Simulating Rating (8) and Finishing ---")
    state_after_good_rating = final_state_after_retry.copy()
    state_after_good_rating["rating"] = 8 # Update rating
    state_after_good_rating["log"].append("User rated the outfit: 8")

    final_state_after_finish = app.invoke(state_after_good_rating, config=config)
    print("\n--- Final State (after rating 8) ---")
    print(f"Final Message: {final_state_after_finish.get('final_message')}")
    print(f"Attempts: {final_state_after_finish.get('attempts')}")
    print(f"Log: \n" + "\n".join(final_state_after_finish.get('log', []))) 