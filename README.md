# AI Outfit Recommender with LangGraph

An intelligent outfit recommendation system built with LangGraph and Streamlit. This application uses OpenAI's language models to generate personalized outfit recommendations based on user preferences and weather conditions.

---

## 🚀 How to Run Locally (Step-by-Step)

1. **Clone this repository**
   ```bash
   git clone <your-repo-url>
   cd outfit-reco
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy the example file and add your credentials:
     ```bash
     cp .env.example .env
     ```
   - Open `.env` and fill in your actual API keys:
     ```env
     OPENAI_API_KEY=your_openai_api_key_here
     TAVILY_API_KEY=your_tavily_api_key_here
     ```
   - You can obtain a Tavily API key at: https://tavily.com/
   - (Optional) You can also enter the Tavily API key directly in the app UI if you prefer.

5. **Run the application**
   ```bash
   streamlit run app/ui.py
   ```
   - The app will open in your browser. If not, visit the URL shown in your terminal (usually http://localhost:8501).

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
