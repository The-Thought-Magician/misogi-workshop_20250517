"""
Weather Service Module
Provides functions to fetch real weather data from OpenWeatherMap API
"""

import os
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# OpenWeatherMap API settings
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Fallback data in case API call fails
FALLBACK_WEATHER = {
    "Delhi": {"temp_c": 35, "condition": "Sunny and Hot"},
    "Mumbai": {"temp_c": 28, "condition": "Humid and Cloudy"},
    "Bangalore": {"temp_c": 25, "condition": "Pleasant and Breezy"},
    "Chennai": {"temp_c": 32, "condition": "Hot and Humid"},
    "Kolkata": {"temp_c": 30, "condition": "Warm and Rainy"},
    "Rajasthan": {"temp_c": 40, "condition": "Very Hot and Dry"},
    "Kerala": {"temp_c": 29, "condition": "Tropical and Humid"},
    "Default": {"temp_c": 27, "condition": "Moderate"}
}

# Mapping of Indian states to major cities for weather lookup
STATE_TO_CITY = {
    "Delhi": "Delhi",
    "Mumbai": "Mumbai",
    "Bangalore": "Bangalore",
    "Chennai": "Chennai",
    "Kolkata": "Kolkata",
    "Rajasthan": "Jaipur",
    "Kerala": "Kochi",
    # Add more mappings as needed
}

def kelvin_to_celsius(kelvin: float) -> float:
    """Convert temperature from Kelvin to Celsius."""
    return kelvin - 273.15

def get_condition_description(weather_data: Dict[str, Any]) -> str:
    """Generate a human-friendly condition description from weather data."""
    if not weather_data or "weather" not in weather_data:
        return "Unknown"
    
    main = weather_data["weather"][0]["main"]
    description = weather_data["weather"][0]["description"]
    
    if "temp" in weather_data["main"]:
        temp = kelvin_to_celsius(weather_data["main"]["temp"])
        
        # Create human-readable condition based on temperature and weather
        if temp > 35:
            temp_desc = "Very Hot"
        elif temp > 30:
            temp_desc = "Hot"
        elif temp > 25:
            temp_desc = "Warm"
        elif temp > 20:
            temp_desc = "Pleasant"
        elif temp > 15:
            temp_desc = "Cool"
        elif temp > 10:
            temp_desc = "Cold"
        else:
            temp_desc = "Very Cold"
        
        # Add humidity descriptor if available
        humidity_desc = ""
        if "humidity" in weather_data["main"]:
            humidity = weather_data["main"]["humidity"]
            if humidity > 80:
                humidity_desc = " and Humid"
            elif humidity < 30:
                humidity_desc = " and Dry"
        
        return f"{temp_desc}{humidity_desc} with {description.capitalize()}"
    
    return f"{main} - {description.capitalize()}"

def get_weather_for_location(location: str) -> Dict[str, Any]:
    """
    Fetch real weather data for a given location from OpenWeatherMap API.
    Falls back to simulated data if API call fails.
    
    Args:
        location: Location name (Indian state or city)
    
    Returns:
        Dictionary containing temperature and condition
    """
    # Early return if API key not set
    if not OPENWEATHER_API_KEY:
        print("Warning: OpenWeatherMap API key not set. Using fallback data.")
        return FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])
    
    # Map state to city for weather lookup if needed
    city = STATE_TO_CITY.get(location, location)
    
    try:
        # Prepare API request
        params = {
            "q": city,
            "appid": OPENWEATHER_API_KEY,
            "units": "metric"  # Get temperatures directly in Celsius
        }
        
        # Make API request
        response = requests.get(BASE_URL, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            weather_data = response.json()
            
            # Extract relevant information
            temp_c = weather_data["main"]["temp"]
            condition = get_condition_description(weather_data)
            
            # Add cache timestamp to avoid excessive API calls
            timestamp = time.time()
            
            return {
                "temp_c": temp_c,
                "condition": condition,
                "data_source": "api",
                "timestamp": timestamp
            }
        else:
            print(f"Weather API error: {response.status_code}. Using fallback data.")
            return FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])
            
    except Exception as e:
        print(f"Error fetching weather data: {str(e)}. Using fallback data.")
        return FALLBACK_WEATHER.get(location, FALLBACK_WEATHER["Default"])

# Test function
if __name__ == "__main__":
    test_locations = ["Delhi", "Mumbai", "Bangalore", "Unknown"]
    for loc in test_locations:
        print(f"\nWeather for {loc}:")
        print(get_weather_for_location(loc)) 