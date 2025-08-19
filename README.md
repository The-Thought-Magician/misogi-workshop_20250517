# 🧥 LangGraph AI Outfit Recommender

A beginner-friendly **LangGraph-powered AI stylist** that recommends personalized outfits based on user preferences, weather conditions, and iterative feedback.

## 🎯 What This Project Teaches

This project is designed to teach **LangGraph fundamentals** through a practical, engaging application:

### 🔧 LangGraph Concepts Demonstrated
- **StateGraph**: Managing workflow state and data flow
- **Nodes**: Individual processing functions (weather fetching, AI generation, decision logic)
- **Edges**: Fixed transitions between nodes
- **Conditional Edges**: Dynamic routing based on business logic
- **State Management**: Shared data structure flowing between all nodes
- **Error Handling**: Graceful failure management in distributed workflows

### 🚀 Key Features
- ✅ **Real Weather Integration**: Fetches live weather data using Tavily Search API
- ✅ **AI-Powered Recommendations**: Uses OpenAI GPT-4 for personalized outfit suggestions
- ✅ **Feedback Loop**: Iterates up to 5 times until user rating ≥ 7
- ✅ **Transparent Logging**: Shows every decision and step in the workflow
- ✅ **Interactive UI**: Streamlit-based web interface with wizard-like flow

## 🛠️ Setup & Installation

### 1. Navigate to Project Directory
```bash
cd misogi-workshop_20250517
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create Environment Variables
Create a `.env` file in the root directory:

```bash
# Required: OpenAI API for outfit generation
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Tavily API for real weather data (fallback data used if not provided)
TAVILY_API_KEY=your_tavily_api_key_here
```

**Getting API Keys:**
- **OpenAI**: Visit [platform.openai.com](https://platform.openai.com) → API Keys
- **Tavily** (Optional): Visit [tavily.com](https://tavily.com) → Get API Key

### 4. Run the Application
```bash
streamlit run app/ui.py
```

The app will open in your browser at `http://localhost:8501`

---

## Features

- Real-time weather data integration via Tavily Search API
- Interactive UI built with Streamlit
- Personalized outfit recommendations based on:
  - Weather conditions
  - Occasion
  - User's desired mood
  - Gender
  - Height
- Iterative recommendation system that learns from user feedback

## System Architecture

The application is built with a LangGraph workflow:
1. **get_weather**: Uses Tavily Search API to find real-time weather data
2. **generate_outfit**: Creates personalized outfit recommendations using LLM
3. **check_rating**: Evaluates user feedback to decide whether to continue or finalize
4. **generate_result**: Creates the final message with the best recommendation

## API Keys

- **OpenAI API Key**: Required for generating outfit recommendations
- **Tavily API Key**: Required for real-time weather data. Without this, the system falls back to simulated weather data.

## Troubleshooting

- If you encounter errors related to API keys, ensure they are correctly set in your `.env` file or provided through the UI.
- Make sure all dependencies are installed correctly.
- For issues with the graph execution, check the process logs available in the UI.

## How Tavily Weather Search Works

The app uses Tavily's search capabilities to find current weather information for a given location:

1. Constructs a search query like "current weather in [location] temperature celsius"
2. Sends this query to Tavily Search API
3. Parses the search results to extract temperature and weather conditions
4. Falls back to simulated data if the search doesn't yield reliable results

This approach allows the application to get up-to-date weather information without relying on a specific weather API.
