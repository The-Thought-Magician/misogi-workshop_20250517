"""
Tavily Weather Service Module
Uses Tavily search API to fetch real-time weather data for locations
"""

import os
import requests
import json
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Tavily API settings
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
TAVILY_SEARCH_URL = "https://api.tavily.com/search"

# Debug - print masked key to verify it's loaded (showing only first and last 2 chars)
if TAVILY_API_KEY:
    masked_key = TAVILY_API_KEY[:2] + "*****" + TAVILY_API_KEY[-2:] if len(TAVILY_API_KEY) > 4 else "***"
    print(f"Tavily API key loaded: {masked_key}")
else:
    print("No Tavily API key found in environment variables")

# Fallback data in case API call fails
FALLBACK_WEATHER = {
    "Delhi": {"temp_c": 35, "condition": "Sunny and Hot"},
    "Mumbai": {"temp_c": 28, "condition": "Humid and Cloudy"},
    "Bangalore": {"temp_c": 25, "condition": "Pleasant and Breezy"},
    "Chennai": {"temp_c": 32, "condition": "Hot and Humid"},
    "Kolkata": {"temp_c": 30, "condition": "Warm and Rainy"},
    "Rajasthan": {"temp_c": 40, "condition": "Very Hot and Dry"},
    "Kerala": {"temp_c": 29, "condition": "Tropical and Humid"},
    "Pune": {"temp_c": 26, "condition": "Pleasant and Partly Cloudy"},
    "Shimla": {"temp_c": 18, "condition": "Cool and Misty"},
    "Patna": {"temp_c": 33, "condition": "Hot and Humid"},
    "Dubai": {"temp_c": 38, "condition": "Very Hot and Dry"},
    "Indore": {"temp_c": 28, "condition": "Warm and Clear"},
    "Default": {"temp_c": 27, "condition": "Moderate"}
}

# Available locations (used for UI dropdown)
AVAILABLE_LOCATIONS = list(FALLBACK_WEATHER.keys())
AVAILABLE_LOCATIONS.remove("Default")  # Don't show 'Default' as an option in the UI

def extract_temperature(text: str) -> Optional[float]:
    """
    Extracts temperature values from text.
    Looks for patterns like "XX°C", "XX degrees Celsius", etc.
    
    Args:
        text: Text containing temperature information
        
    Returns:
        Temperature in Celsius if found, None otherwise
    """
    # Look for patterns like "25°C", "25 °C", "25 degrees Celsius"
    celsius_patterns = [
        r'(\d+(?:\.\d+)?)°C',  # 25°C
        r'(\d+(?:\.\d+)?) °C',  # 25 °C
        r'(\d+(?:\.\d+)?) degrees Celsius',  # 25 degrees Celsius
        r'(\d+(?:\.\d+)?) Celsius',  # 25 Celsius
        r'temperature (?:is|of) (\d+(?:\.\d+)?)',  # temperature is 25 or temperature of 25
        r'(\d+(?:\.\d+)?) degrees'  # 25 degrees (assume Celsius)
    ]
    
    for pattern in celsius_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                continue
    
    # If no Celsius temperature found, try Fahrenheit and convert
    fahrenheit_patterns = [
        r'(\d+(?:\.\d+)?)°F',  # 77°F
        r'(\d+(?:\.\d+)?) °F',  # 77 °F
        r'(\d+(?:\.\d+)?) degrees Fahrenheit',  # 77 degrees Fahrenheit
        r'(\d+(?:\.\d+)?) Fahrenheit'  # 77 Fahrenheit
    ]
    
    for pattern in fahrenheit_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                fahrenheit = float(match.group(1))
                # Convert to Celsius
                return round((fahrenheit - 32) * 5/9, 1)
            except ValueError:
                continue
    
    return None

def extract_weather_condition(text: str) -> Optional[str]:
    """
    Extracts weather condition descriptions from text.
    
    Args:
        text: Text containing weather information
        
    Returns:
        Weather condition description if found, None otherwise
    """
    # Common weather condition keywords to look for
    condition_patterns = [
        r'(sunny|clear sky|clear)',
        r'(cloudy|overcast|cloud cover)',
        r'(rainy|raining|rain shower|light rain|heavy rain)',
        r'(snowy|snowing|snow shower|light snow|heavy snow)',
        r'(foggy|misty|hazy)',
        r'(stormy|thunderstorm|thunder|lightning)',
        r'(windy|strong winds|gusts)',
        r'(humid|humidity|muggy)',
        r'(dry|arid)',
        r'(hot|warm|pleasant|cool|cold|chilly|freezing)'
    ]
    
    # Look for weather condition descriptions
    for pattern in condition_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(0).capitalize()
    
    # If no specific condition found, look for sentences containing "weather"
    weather_sentences = re.findall(r'[^.!?]*(?:weather|condition)[^.!?]*[.!?]', text, re.IGNORECASE)
    if weather_sentences:
        return weather_sentences[0].strip()
    
    return None

def parse_weather_from_search_results(search_results: Dict[str, Any], location: str) -> Dict[str, Any]:
    """
    Parses weather information from Tavily search results.
    
    Args:
        search_results: Tavily search results
        location: Location name
        
    Returns:
        Dictionary with parsed weather information
    """
    # Extract content from search results
    all_text = ""
    if "results" in search_results:
        for result in search_results["results"]:
            if "content" in result:
                all_text += result["content"] + " "
    
    # Extract temperature and condition
    temp_c = extract_temperature(all_text)
    condition = extract_weather_condition(all_text)
    
    # If we couldn't extract temperature or condition, use fallback
    if temp_c is None or condition is None:
        print(f"Warning: Couldn't extract complete weather data for {location} from Tavily results. Using fallback data.")
        fallback = FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])
        
        # Use extracted values if available, fallback otherwise
        temp_c = temp_c if temp_c is not None else fallback["temp_c"]
        condition = condition if condition is not None else fallback["condition"]
    
    return {
        "temp_c": temp_c,
        "condition": condition,
        "data_source": "tavily",
        "timestamp": time.time()
    }

def get_weather_for_location(location: str) -> Dict[str, Any]:
    """
    Fetch real weather data for a given location using Tavily search API.
    Falls back to simulated data if API call fails.
    
    Args:
        location: Location name (city or region)
    
    Returns:
        Dictionary containing temperature and condition
    """
    # Early return if API key not set
    if not TAVILY_API_KEY:
        print("Warning: Tavily API key not set. Using fallback data.")
        return FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])
    
    try:
        # Construct search query for current weather
        search_query = f"current weather in {location} temperature celsius"
        print(f"Searching for: '{search_query}'")
        
        # Prepare API request - Using different header format per Tavily API docs
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {TAVILY_API_KEY}"  # Changed from X-Api-Key to Authorization: Bearer
        }
        
        payload = {
            "query": search_query,
            "search_depth": "advanced",
            "include_domains": ["weather.com", "accuweather.com", "weatherapi.com", "timeanddate.com", "bbc.com", "cnn.com"],
            "include_answer": True,
            "max_results": 5
        }
        
        # Make API request
        print(f"Making request to {TAVILY_SEARCH_URL}")
        response = requests.post(TAVILY_SEARCH_URL, json=payload, headers=headers)
        
        # Check if request was successful
        if response.status_code == 200:
            search_results = response.json()
            print(f"Successfully received response from Tavily")
            
            # Parse weather information from search results
            weather_data = parse_weather_from_search_results(search_results, location)
            return weather_data
        else:
            # Print more detailed error information
            error_detail = f"Status: {response.status_code}"
            try:
                error_detail += f", Response: {response.text[:200]}"
            except:
                pass
                
            print(f"Tavily API error: {response.status_code}. Details: {error_detail}. Using fallback data.")
            return FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])
            
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}. Using fallback data.")
        return FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])

# Test function
if __name__ == "__main__":
    test_locations = ["Delhi", "Mumbai", "Bangalore", "New York"]
    for loc in test_locations:
        print(f"\nWeather for {loc}:")
        weather = get_weather_for_location(loc)
        print(f"Temperature: {weather['temp_c']}°C")
        print(f"Condition: {weather['condition']}")
        print(f"Source: {weather.get('data_source', 'fallback')}") 