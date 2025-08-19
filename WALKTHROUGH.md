# 🎓 LangGraph Outfit Recommender - Code Walkthrough

This document provides a detailed explanation of how the code works, perfect for understanding LangGraph concepts.

## 🏗️ Overall Architecture

```
User Input → LangGraph Workflow → AI Recommendations → User Feedback → Final Result
     ↓              ↓                    ↓                ↓              ↓
   Streamlit    StateGraph          OpenAI API       Rating Loop    Success/Fail
    (UI)        Execution           + Weather API      (≤5 times)     Message
```

## 📂 File Structure & Responsibilities

### 1. `app/fixed_graph.py` - The LangGraph Workflow (Backend)

This is the **heart** of the application. It contains:

#### State Definition
```python
class OutfitState(TypedDict):
    height: Annotated[str, "User height"]
    gender: Annotated[str, "User gender"]  
    location: Annotated[str, "User location"]
    # ... more fields
```

**Key Concept**: In LangGraph, the `State` is a shared data structure that flows through all nodes. Each node can read from it and update it.

#### Node Functions
Each node is a regular Python function that:
- Takes the current state as input
- Performs some processing  
- Returns a dictionary of updates to merge into the state

**Node 1: `get_weather(state)`**
```python
def get_weather(state: OutfitState) -> Dict:
    location = state.get("location", "Default")
    weather_info = get_weather_for_location(location)  # API call
    return {"weather": weather_info, "log": logs + [log_entry]}
```

This node demonstrates:
- Reading from state (`location`)
- External API calls (weather service)
- Updating state with new data (`weather`)
- Transparent logging (`log`)

**Node 2: `generate_outfit(state)`**
```python
def generate_outfit(state: OutfitState) -> Dict:
    # Extract user context
    height = state["height"]
    gender = state["gender"] 
    weather = state["weather"]
    
    # Create AI prompt
    prompt = f"You are a fashion stylist... Height: {height}..."
    
    # Call LLM
    response = LLM.invoke([HumanMessage(content=prompt)])
    
    return {
        "recommendation": response.content.strip(),
        "attempts": attempt,
        "log": logs + [log_entry]
    }
```

This node demonstrates:
- Complex state access (multiple fields)
- LLM integration with structured prompts
- Attempt tracking
- Error handling

**Node 3: `generate_result(state)`**
```python
def generate_result(state: OutfitState) -> Dict:
    rating = state.get("rating", 0)
    attempts = state.get("attempts", 0)
    
    if rating >= 7:
        result = f"🎉 Perfect outfit found after {attempts} attempt(s)!"
    else:
        result = f"💔 We tried our best but couldn't find the perfect outfit..."
        
    return {"result_message": result, "log": logs + [log_entry]}
```

This is the **terminal node** that creates final messages.

#### Conditional Logic
```python
def check_rating(state: OutfitState) -> str:
    rating = state.get("rating", 0)
    attempts = state.get("attempts", 0)
    max_attempts = state.get("max_attempts", 5)
    
    if rating >= 7:
        return "generate_result"     # User satisfied
    elif attempts >= max_attempts:
        return "generate_result"     # Give up
    else:
        return "generate_outfit"     # Try again
```

**Key Concept**: This function determines which node to execute next based on business logic.

#### Graph Assembly
```python
def create_graph():
    workflow = StateGraph(OutfitState)
    
    # Add nodes
    workflow.add_node("get_weather", get_weather)
    workflow.add_node("generate_outfit", generate_outfit)  
    workflow.add_node("generate_result", generate_result)
    
    # Set entry point
    workflow.set_entry_point("get_weather")
    
    # Add edges
    workflow.add_edge("get_weather", "generate_outfit")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "generate_outfit",
        check_rating,
        {
            "generate_outfit": "generate_outfit",  # Loop back
            "generate_result": "generate_result"   # Finish
        }
    )
    
    workflow.add_edge("generate_result", END)
    
    return workflow
```

**Key Concept**: This creates the actual workflow graph with nodes and edges.

### 2. `app/ui.py` - Streamlit Frontend

This file demonstrates how to integrate LangGraph with a web UI:

#### Session State Management
```python
def initialize_session_state():
    defaults = {
        "processing": False,
        "recommendation": None,
        "rating": 0,
        # ... more fields
    }
```

Streamlit's session state maintains data across user interactions.

#### Graph Execution
```python
# Execute the graph
stream = app.stream(st.session_state.graph_state, config=config)
for event in stream:
    node_name = list(event.keys())[0]
    node_output = event[node_name]
    
    # Update session state
    st.session_state.graph_state.update(node_output)
    
    # Update UI in real-time
    if 'recommendation' in node_output:
        st.session_state.recommendation = node_output['recommendation']
```

**Key Concept**: `app.stream()` executes the graph and yields results from each node, allowing for real-time UI updates.

#### User Feedback Loop
```python
# Show recommendation and wait for rating
if st.session_state.waiting_for_rating and st.session_state.recommendation:
    st.markdown(st.session_state.recommendation)
    rating_value = st.slider("Rating:", 1, 10, 5)
    if st.button("Submit Rating"):
        st.session_state.rating = rating_value
        st.session_state.graph_state['rating'] = rating_value
        # Continue graph execution...
```

This creates the interactive feedback loop.

### 3. `app/tavily_weather_service.py` - Weather API Integration

```python
def get_weather_for_location(location: str) -> Dict[str, Any]:
    search_query = f"current weather in {location} temperature celsius"
    
    payload = {
        "query": search_query,
        "search_depth": "advanced",
        "include_domains": ["weather.com", "accuweather.com"],
        "max_results": 5
    }
    
    response = requests.post(TAVILY_SEARCH_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        return parse_weather_from_search_results(response.json(), location)
    else:
        return FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])
```

This demonstrates external API integration with graceful fallbacks.

## 🔄 Execution Flow

Let's trace through a complete execution:

### 1. User Fills Form
- Height: "5'10\""
- Gender: "Male"
- Location: "Mumbai"  
- Occasion: "Party"
- Mood: "Confident"

### 2. Graph Execution Starts

**Step 1: `get_weather` node**
- Input: `{location: "Mumbai", ...}`
- Action: Calls Tavily API to search "current weather in Mumbai temperature celsius"
- Output: `{weather: {temp_c: 28, condition: "Humid and Cloudy"}, ...}`

**Step 2: `generate_outfit` node**
- Input: All user data + weather data
- Action: Calls OpenAI with prompt:
  ```
  You are a fashion stylist AI...
  Height: 5'10"
  Gender: Male
  Location: Mumbai  
  Occasion: Party
  Mood: Confident
  Current Weather: 28°C, Humid and Cloudy
  ```
- Output: `{recommendation: "For a party in Mumbai's humid weather...", attempts: 1}`

**Step 3: `check_rating` function**
- User rates the outfit: 6/10
- Logic: `6 < 7` and `attempts (1) < max_attempts (5)`
- Decision: Return `"generate_outfit"` (try again)

**Step 4: `generate_outfit` node (again)**
- Input: Same data + previous attempt info
- Action: Calls OpenAI with "This is attempt #2, try something different"  
- Output: `{recommendation: "A different party outfit...", attempts: 2}`

**Step 5: `check_rating` function**
- User rates: 8/10
- Logic: `8 >= 7`  
- Decision: Return `"generate_result"` (finish)

**Step 6: `generate_result` node**
- Input: Final state with rating=8, attempts=2
- Output: `{result_message: "🎉 Perfect outfit found after 2 attempt(s)! ..."}`

**Step 7: END**
- Graph execution completes
- UI shows final result

## 🎯 Key LangGraph Concepts Illustrated

### 1. **State Management**
- State flows through all nodes automatically
- Nodes return partial updates that get merged
- State preserves data across the entire workflow

### 2. **Node Composition**  
- Each node is a focused function with single responsibility
- Nodes can call external APIs, LLMs, or any Python code
- Return values automatically update the shared state

### 3. **Conditional Routing**
- `check_rating()` function dynamically determines next node
- Enables complex business logic and loops
- Supports different execution paths based on data

### 4. **Streaming Execution**
- `app.stream()` yields results as each node completes
- Enables real-time UI updates
- User can see progress and intermediate results

### 5. **Error Handling**
- Each node handles its own errors gracefully
- Fallback data ensures workflow continues even with API failures
- Logging tracks all decisions and failures

## 🚀 Extending the System

Now that you understand the architecture, you can extend it:

### Add New Nodes
```python
def validate_outfit(state: OutfitState) -> Dict:
    recommendation = state["recommendation"]
    # Add validation logic here
    return {"validation_score": score, "log": logs + [entry]}

# Add to graph
workflow.add_node("validate_outfit", validate_outfit)
workflow.add_edge("generate_outfit", "validate_outfit")
```

### Modify Decision Logic
```python  
def check_rating(state: OutfitState) -> str:
    rating = state.get("rating", 0)
    validation_score = state.get("validation_score", 0)
    
    if rating >= 7 and validation_score >= 8:
        return "generate_result"
    # Add more complex logic...
```

### Add Parallel Processing
```python
# Generate multiple outfit options in parallel
workflow.add_node("generate_casual", generate_casual_outfit)
workflow.add_node("generate_formal", generate_formal_outfit)
workflow.add_node("combine_options", combine_outfit_options)
```

## 🎓 Learning Outcomes

After studying this code, you should understand:

✅ **LangGraph Core Concepts**: StateGraph, Nodes, Edges, Conditional Edges  
✅ **State Management**: How data flows and gets updated  
✅ **External Integrations**: API calls within graph nodes  
✅ **Conditional Logic**: Dynamic routing based on business rules  
✅ **User Interaction**: Integrating graphs with web interfaces  
✅ **Error Handling**: Graceful failure management  
✅ **Real-time Updates**: Streaming execution and UI updates  

## 🔧 Next Steps

1. **Experiment**: Modify prompts, add new nodes, change logic
2. **Extend**: Add image generation, shopping links, memory
3. **Learn More**: Explore advanced LangGraph features like sub-graphs, checkpoints
4. **Build**: Create your own LangGraph applications using this pattern

This codebase provides a solid foundation for understanding and building LangGraph applications. The key is starting simple (like this outfit recommender) and gradually adding complexity as you learn! 🎉