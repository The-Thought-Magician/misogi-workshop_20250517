# 🚀 Quick Setup Guide

This guide will help you get the LangGraph AI Outfit Recommender running on your system.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
# Install required packages
pip install langgraph==0.4.5
pip install langchain==0.3.25  
pip install langchain-openai==0.3.17
pip install streamlit==1.34.0
pip install python-dotenv==1.0.1
pip install requests==2.31.0
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the root directory:

```env
# Required for AI recommendations
OPENAI_API_KEY=your_openai_key_here

# Optional for real weather data (uses fallback if not provided)
TAVILY_API_KEY=your_tavily_key_here
```

### 3. Test the Backend

Test the LangGraph workflow:

```bash
python3 app/fixed_graph.py
```

You should see output showing the graph execution with sample data.

### 4. Run the Web Application

Start the Streamlit app:

```bash
streamlit run app/ui.py
```

The app will open in your browser at `http://localhost:8501`

## API Keys

### OpenAI API Key (Required)
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up/log in
3. Go to API Keys section  
4. Create a new API key
5. Copy it to your `.env` file

### Tavily API Key (Optional)
1. Visit [tavily.com](https://tavily.com)
2. Sign up for a free account
3. Get your API key from dashboard
4. Copy it to your `.env` file

**Note**: Without Tavily key, the app uses fallback weather data, which works perfectly fine for testing!

## Testing Without Dependencies

If you want to test the core logic without installing all dependencies:

```bash
python3 test_logic.py
```

This will verify that all the decision logic and data structures work correctly.

## Troubleshooting

### "Module not found" errors
- Make sure you installed all dependencies with pip
- Check that you're using the correct Python version (3.8+)

### "API key not found" errors  
- Check your `.env` file is in the correct location (root directory)
- Make sure the variable names match exactly: `OPENAI_API_KEY` and `TAVILY_API_KEY`

### Streamlit issues
- Try refreshing the browser page
- Check the terminal for error messages
- Make sure no other apps are using port 8501

## Project Structure

```
misogi-workshop_20250517/
├── app/
│   ├── fixed_graph.py          # LangGraph workflow (backend)
│   ├── ui.py                   # Streamlit interface  
│   ├── tavily_weather_service.py # Weather API service
│   └── weather_service.py      # Fallback weather data
├── test_logic.py              # Standalone logic tests
├── requirements.txt           # Python dependencies
├── .env                      # Environment variables (create this)
└── README.md                 # Full documentation
```

## Next Steps

Once everything is running:

1. **Explore the Code**: Start with `app/fixed_graph.py` to understand the LangGraph workflow
2. **Experiment**: Try modifying prompts, adding new nodes, or changing decision logic
3. **Learn**: Read the extensive comments throughout the code
4. **Extend**: Add new features like image generation, shopping links, or memory

Happy learning! 🎉