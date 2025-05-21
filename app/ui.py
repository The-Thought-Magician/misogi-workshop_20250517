# Streamlit UI logic will go here 

import streamlit as st
import sys
import os

# Add the parent directory to sys.path to allow imports from graph.py
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# --- Initialize SessionState ---
# This must happen before any other operation that might access the session state
if "processing" not in st.session_state:
    st.session_state.processing = False
if "recommendation" not in st.session_state:
    st.session_state.recommendation = None
if "rating" not in st.session_state:
    st.session_state.rating = 0
if "rating_submitted" not in st.session_state:
    st.session_state.rating_submitted = False
if "attempts" not in st.session_state:
    st.session_state.attempts = 0
if "log" not in st.session_state:
    st.session_state.log = ["Welcome! Fill in your details to get started."]
if "result_message" not in st.session_state:  # Changed from final_message to result_message
    st.session_state.result_message = None
if "graph_state" not in st.session_state:
    st.session_state.graph_state = {}
if "run_key" not in st.session_state:
    st.session_state.run_key = 0
if "waiting_for_rating" not in st.session_state:
    st.session_state.waiting_for_rating = False

# Streamlit App Configuration
st.set_page_config(page_title="AI Outfit Recommender", layout="wide")
st.title("🧥 AI Outfit Recommender")
st.caption("Get personalized outfit recommendations based on your style and context!")

# Try to import graph components
try:
    # Import from our fixed_graph module
    from app.fixed_graph import app, OutfitState, AVAILABLE_LOCATIONS

    # --- Constants even if graph fails ---
    MAX_ATTEMPTS = 5
    INDIAN_STATES = AVAILABLE_LOCATIONS
    GENDERS = ["Male", "Female", "Other"]
    OCCASIONS = ["Party", "Date", "Formal", "Daily Casual", "Vacation"]
    MOODS = ["Confident", "Minimal", "Romantic", "Bold", "Relaxed", "Streetwear"]

    # --- UI Layout ---
    col1, col2 = st.columns([1, 1.5])

    with col1:
        st.header("Step 1: Your Details")
        height = st.text_input("Height (e.g., 5'10\", 170cm)", "5'10\"")
        gender = st.selectbox("Gender", GENDERS, index=0)

        st.header("Step 2: Context")
        location = st.selectbox("Location (Indian State)", INDIAN_STATES, index=INDIAN_STATES.index("Bangalore") if "Bangalore" in INDIAN_STATES else 0)
        occasion = st.selectbox("Occasion", OCCASIONS, index=3)  # Default to Daily Casual
        mood = st.selectbox("Desired Mood", MOODS, index=4)  # Default to Relaxed

        # API key input
        with st.expander("Tavily API Settings"):
            tavily_key = st.text_input(
                "Tavily API Key", 
                value=os.getenv("TAVILY_API_KEY", ""),
                type="password",
                help="Required for real-time weather data via Tavily's search API"
            )
            
            if tavily_key:
                # Save to .env file
                env_path = os.path.join(parent_dir, ".env")
                try:
                    # Read existing content first
                    env_content = ""
                    if os.path.exists(env_path):
                        with open(env_path, "r") as f:
                            env_content = f.read()
                    
                    # Check if we need to update or add
                    if "TAVILY_API_KEY=" in env_content:
                        # Update existing key
                        lines = env_content.split("\n")
                        new_lines = []
                        for line in lines:
                            if line.startswith("TAVILY_API_KEY="):
                                new_lines.append(f"TAVILY_API_KEY={tavily_key}")
                            else:
                                new_lines.append(line)
                        updated_content = "\n".join(new_lines)
                    else:
                        # Add new key
                        if env_content and not env_content.endswith("\n"):
                            env_content += "\n"
                        updated_content = f"{env_content}TAVILY_API_KEY={tavily_key}\n"
                    
                    # Write back
                    with open(env_path, "w") as f:
                        f.write(updated_content)
                    
                    # Set environment variable for current session
                    os.environ["TAVILY_API_KEY"] = tavily_key
                    
                except Exception as e:
                    st.warning(f"Could not save API key to .env file: {e}")
            
            # Add info about data source
            st.info("ℹ️ Tavily Search API will be used to search for real-time weather data. If the API key is not provided, fallback data will be used.")

        # Action button for starting the process
        button_disabled = st.session_state.processing or st.session_state.result_message is not None
        
        if st.button("✨ Get Outfit Recommendation", 
                    use_container_width=True, 
                    type="primary",
                    disabled=button_disabled):
            
            # Reset state
            st.session_state.processing = True
            st.session_state.recommendation = None
            st.session_state.result_message = None
            st.session_state.rating = 0
            st.session_state.rating_submitted = False
            st.session_state.waiting_for_rating = False
            st.session_state.attempts = 0
            st.session_state.log = ["Starting new recommendation process..."]
            st.session_state.graph_state = {}
            st.session_state.run_key += 1
            
            # Create initial state for the graph (notice the key is result_message instead of final_message)
            initial_input = {
                "height": height,
                "gender": gender,
                "location": location,
                "occasion": occasion,
                "mood": mood,
                "rating": 0,
                "attempts": 0,
                "max_attempts": MAX_ATTEMPTS,
                "log": st.session_state.log[:],
                "weather": {},
                "recommendation": "",
                "result_message": ""  # Changed from final_message to result_message
            }
            st.session_state.graph_state = initial_input
            
            # Add a success message and rerun to start processing
            st.success("Starting the recommendation process...")
            st.rerun()

    # Display static content in the right column
    with col2:
        # Content varies based on current state
        if st.session_state.result_message:
            st.header("🏁 Final Result")
            st.success(st.session_state.result_message)
            
            # Add a restart button
            if st.button("Start Over", use_container_width=True):
                st.session_state.processing = False
                st.session_state.recommendation = None
                st.session_state.result_message = None
                st.session_state.rating = 0
                st.session_state.rating_submitted = False
                st.session_state.waiting_for_rating = False
                st.session_state.attempts = 0
                st.session_state.log = ["Welcome! Fill in your details to get started."]
                st.session_state.graph_state = {}
                st.rerun()
        elif st.session_state.waiting_for_rating and st.session_state.recommendation:
            # Show the recommendation and wait for rating
            st.header("💡 Recommendation")
            st.markdown(st.session_state.recommendation)
            st.divider()
            
            st.header("⭐ Rate the Outfit (1-10)")
            rating_value = st.slider("Rating:", 1, 10, 5, key=f"rating_slider_{st.session_state.run_key}_{st.session_state.attempts}")
            if st.button("Submit Rating & Continue", key=f"submit_rating_{st.session_state.run_key}_{st.session_state.attempts}", use_container_width=True):
                st.session_state.rating = rating_value
                st.session_state.rating_submitted = True
                st.session_state.waiting_for_rating = False
                st.rerun()  # Rerun to process the rating
                
            # Show live log if available
            if st.session_state.log:
                with st.expander("View Process Log"):
                    st.text_area("Process Steps:", value="\n".join(st.session_state.log), height=200, key=f"log_waiting_{st.session_state.run_key}")
        else:
            st.header("Output will appear here")
            st.info("Fill out the form and click the recommendation button to get started.")
    
    # --- Processing Logic (only runs if processing flag is set) ---
    if st.session_state.processing and not st.session_state.result_message and not st.session_state.waiting_for_rating:
        st.info("Processing your request...")
        
        # Prepare initial state if it's the first attempt
        if st.session_state.attempts == 0:
            with st.spinner("Setting up and getting weather..."):
                # Graph state was already set up above when the button was clicked
                st.session_state.log.append("Invoking graph...")
        
        # Add rating to graph state if it's a retry and rating has been submitted
        elif st.session_state.rating_submitted:
            with st.spinner("Processing your rating..."):
                st.session_state.graph_state['rating'] = st.session_state.rating
                st.session_state.log.append(f"User rated previous outfit: {st.session_state.rating}. Continuing graph...")
                # Reset the rating_submitted flag for the next iteration
                st.session_state.rating_submitted = False
        
        # Process the graph (either initial run or continuation after rating)
        config = {"recursion_limit": 15}
        
        # Placeholders for dynamic content
        with col2:
            log_placeholder = st.empty()
            result_placeholder = st.empty()
        
        try:
            # Stream events from the graph
            with st.spinner("Running recommendation engine..."):
                stream = app.stream(st.session_state.graph_state, config=config)
                for event in stream:
                    node_name = list(event.keys())[0]
                    node_output = event[node_name]
                    
                    # Update the state
                    st.session_state.graph_state.update(node_output)
                    
                    # Update session state convenience variables
                    if 'log' in node_output:
                        st.session_state.log = node_output['log']
                    if 'recommendation' in node_output:
                        st.session_state.recommendation = node_output['recommendation']
                    if 'attempts' in node_output:
                        st.session_state.attempts = node_output['attempts']
                    if 'result_message' in node_output:  # Changed from final_message to result_message
                        st.session_state.result_message = node_output['result_message']
                    
                    # Update the UI
                    with log_placeholder.container():
                        st.header("📝 Live Log")
                        st.text_area("Process Steps:", value="\n".join(st.session_state.log), height=300, key=f"log_{st.session_state.run_key}_{st.session_state.attempts}")
                    
                    # If we got a recommendation, pause and wait for rating
                    if node_name == "generate_outfit" and st.session_state.recommendation:
                        st.session_state.waiting_for_rating = True
                        st.rerun()  # Rerun to show the rating UI
                    
                    # Show final message if available
                    if st.session_state.result_message:
                        with result_placeholder.container():
                            st.header("🏁 Final Result")
                            st.success(st.session_state.result_message)
                        st.session_state.processing = False
                        st.rerun()  # Rerun to update UI state
            
            # If the stream ends without a final message
            if not st.session_state.result_message:
                st.warning("Process completed but no final message was generated.")
                st.session_state.processing = False
        
        except Exception as e:
            st.error(f"An error occurred during processing: {e}")
            st.session_state.log.append(f"ERROR: {e}")
            st.session_state.processing = False
        
except Exception as e:
    st.error(f"Critical application error: {e}")
    st.exception(e)  # Show the full traceback for debugging
    st.warning("The application is not able to initialize. Check the environment and dependencies.") 