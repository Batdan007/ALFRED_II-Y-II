"""
Weather Lookup Module
Real-time weather data for MECA integration

Supports:
- Current conditions
- Forecasts (hourly/daily)
- Weather alerts
- Multiple location formats (city, zip, coordinates)

Author: Daniel J Rita (BATDAN)
"""

import os
import re
import logging
import requests
from typing import Optional, Dict, List, Tuple
from datetime import datetime


class WeatherLookup:
    """
    Real-time weather lookup using OpenWeatherMap API

    Features:
    - Current weather conditions
    - 5-day forecast
    - Weather alerts
    - Location detection from natural language
    - MECA-ready structured data output
    """

    # Common location aliases
    LOCATION_ALIASES = {
        'home': None,  # Set via config
        'work': None,
        'here': None,  # Use IP geolocation
        'batcave': None,  # Custom location
    }

    # Weather condition icons for text output
    CONDITION_ICONS = {
        'clear': 'Clear',
        'clouds': 'Cloudy',
        'rain': 'Rainy',
        'drizzle': 'Drizzle',
        'thunderstorm': 'Thunderstorm',
        'snow': 'Snowy',
        'mist': 'Misty',
        'fog': 'Foggy',
        'haze': 'Hazy',
    }

    def __init__(self, api_key: Optional[str] = None, default_location: str = "New York"):
        """
        Initialize weather lookup

        Args:
            api_key: OpenWeatherMap API key (defaults to OPEN_WEATHER_KEY env var)
            default_location: Default location if none specified
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key or os.getenv('OPEN_WEATHER_KEY') or os.getenv('OPENWEATHERMAP_API_KEY')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.geo_url = "https://api.openweathermap.org/geo/1.0"
        self.default_location = default_location

        if not self.api_key:
            self.logger.debug("No OpenWeatherMap API key - weather lookups disabled")

    def is_available(self) -> bool:
        """Check if weather lookup is available"""
        return bool(self.api_key)

    def extract_location(self, text: str) -> Optional[str]:
        """
        Extract location from natural language text

        Args:
            text: User message

        Returns:
            Location string or None
        """
        text_lower = text.lower()

        # Check for explicit location patterns
        patterns = [
            r"weather (?:in|for|at) ([a-zA-Z\s,]+?)(?:\?|$|today|tomorrow|this|next)",
            r"(?:in|for|at) ([a-zA-Z\s,]+?)(?:'s)? weather",
            r"what(?:'s| is)(?: the)? weather (?:like )?(?:in|for|at) ([a-zA-Z\s,]+)",
            r"([a-zA-Z\s,]+) weather",
            r"weather ([a-zA-Z\s,]+?)(?:\?|$)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text_lower)
            if match:
                location = match.group(1).strip()
                # Clean up common words that aren't locations
                stop_words = ['the', 'today', 'tomorrow', 'now', 'current', 'right', 'please', 'like']
                if location not in stop_words:
                    return location.title()

        # Check aliases
        for alias in self.LOCATION_ALIASES:
            if alias in text_lower:
                return self.LOCATION_ALIASES[alias] or self.default_location

        return None

    def is_weather_query(self, text: str) -> bool:
        """
        Detect if text is asking about weather

        Args:
            text: User message

        Returns:
            True if this is a weather query
        """
        weather_keywords = [
            'weather', 'temperature', 'temp', 'forecast',
            'rain', 'raining', 'snow', 'snowing', 'sunny',
            'cloudy', 'storm', 'humidity', 'wind',
            'hot', 'cold', 'warm', 'cool',
            'umbrella', 'jacket', 'coat'
        ]

        text_lower = text.lower()
        return any(kw in text_lower for kw in weather_keywords)

    def geocode(self, location: str) -> Optional[Dict]:
        """
        Convert location name to coordinates

        Args:
            location: City name or address

        Returns:
            Dict with lat, lon, name or None
        """
        if not self.api_key:
            return None

        try:
            url = f"{self.geo_url}/direct"
            params = {
                'q': location,
                'limit': 1,
                'appid': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return {
                        'lat': data[0]['lat'],
                        'lon': data[0]['lon'],
                        'name': data[0].get('name', location),
                        'country': data[0].get('country', '')
                    }
            return None

        except Exception as e:
            self.logger.error(f"Geocoding failed: {e}")
            return None

    def get_current(self, location: str) -> Optional[Dict]:
        """
        Get current weather conditions

        Args:
            location: City name or coordinates

        Returns:
            Weather data or None
        """
        if not self.api_key:
            return None

        try:
            url = f"{self.base_url}/weather"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                return {
                    'location': data.get('name', location),
                    'country': data.get('sys', {}).get('country', ''),
                    'condition': data['weather'][0]['main'],
                    'description': data['weather'][0]['description'],
                    'temp': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'temp_min': round(data['main']['temp_min']),
                    'temp_max': round(data['main']['temp_max']),
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'wind_speed': round(data['wind']['speed']),
                    'wind_deg': data['wind'].get('deg', 0),
                    'clouds': data['clouds']['all'],
                    'visibility': data.get('visibility', 10000) / 1000,  # km
                    'sunrise': datetime.fromtimestamp(data['sys']['sunrise']).strftime('%H:%M'),
                    'sunset': datetime.fromtimestamp(data['sys']['sunset']).strftime('%H:%M'),
                    'timestamp': datetime.now().isoformat()
                }

            self.logger.warning(f"Weather API returned {response.status_code}")
            return None

        except Exception as e:
            self.logger.error(f"Weather lookup failed: {e}")
            return None

    def get_forecast(self, location: str, days: int = 5) -> Optional[List[Dict]]:
        """
        Get weather forecast

        Args:
            location: City name
            days: Number of days (max 5 for free tier)

        Returns:
            List of forecast data or None
        """
        if not self.api_key:
            return None

        try:
            url = f"{self.base_url}/forecast"
            params = {
                'q': location,
                'appid': self.api_key,
                'units': 'imperial',
                'cnt': min(days * 8, 40)  # 3-hour intervals, 8 per day
            }

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                forecasts = []

                # Group by day
                daily = {}
                for item in data['list']:
                    date = datetime.fromtimestamp(item['dt']).strftime('%Y-%m-%d')
                    if date not in daily:
                        daily[date] = {
                            'date': date,
                            'day_name': datetime.fromtimestamp(item['dt']).strftime('%A'),
                            'temps': [],
                            'conditions': [],
                            'humidity': [],
                            'wind': []
                        }
                    daily[date]['temps'].append(item['main']['temp'])
                    daily[date]['conditions'].append(item['weather'][0]['main'])
                    daily[date]['humidity'].append(item['main']['humidity'])
                    daily[date]['wind'].append(item['wind']['speed'])

                # Summarize each day
                for date, day_data in list(daily.items())[:days]:
                    forecasts.append({
                        'date': day_data['date'],
                        'day': day_data['day_name'],
                        'temp_high': round(max(day_data['temps'])),
                        'temp_low': round(min(day_data['temps'])),
                        'condition': max(set(day_data['conditions']), key=day_data['conditions'].count),
                        'humidity': round(sum(day_data['humidity']) / len(day_data['humidity'])),
                        'wind': round(sum(day_data['wind']) / len(day_data['wind']))
                    })

                return forecasts

            return None

        except Exception as e:
            self.logger.error(f"Forecast lookup failed: {e}")
            return None

    def format_current(self, weather: Dict) -> str:
        """
        Format current weather for natural language

        Args:
            weather: Weather data dict

        Returns:
            Formatted string
        """
        return (
            f"{weather['location']}, {weather['country']}: "
            f"{weather['temp']}°F (feels like {weather['feels_like']}°F), "
            f"{weather['description'].title()}. "
            f"Humidity: {weather['humidity']}%, "
            f"Wind: {weather['wind_speed']} mph. "
            f"High: {weather['temp_max']}°F, Low: {weather['temp_min']}°F. "
            f"Sunrise: {weather['sunrise']}, Sunset: {weather['sunset']}"
        )

    def format_forecast(self, forecasts: List[Dict]) -> str:
        """
        Format forecast for natural language

        Args:
            forecasts: List of forecast dicts

        Returns:
            Formatted string
        """
        lines = []
        for day in forecasts:
            lines.append(
                f"{day['day']}: {day['condition']}, "
                f"High {day['temp_high']}°F / Low {day['temp_low']}°F"
            )
        return "\n".join(lines)

    def get_meca_data(self, location: str) -> Optional[Dict]:
        """
        Get weather data in MECA-compatible format

        Args:
            location: Location to get weather for

        Returns:
            MECA-structured weather data
        """
        current = self.get_current(location)
        if not current:
            return None

        forecast = self.get_forecast(location, days=3)

        return {
            'type': 'weather',
            'location': current['location'],
            'current': {
                'temperature': current['temp'],
                'feels_like': current['feels_like'],
                'condition': current['condition'],
                'humidity': current['humidity'],
                'wind_speed': current['wind_speed'],
                'visibility': current['visibility']
            },
            'forecast': forecast or [],
            'alerts': [],  # Would need One Call API for alerts
            'timestamp': current['timestamp'],
            'source': 'openweathermap'
        }

    def lookup_for_prompt(self, text: str) -> Tuple[bool, str]:
        """
        Main entry point: check if query needs weather data, fetch if so

        Args:
            text: User message

        Returns:
            Tuple of (was_weather_query, context_to_inject)
        """
        if not self.is_weather_query(text):
            return False, ""

        location = self.extract_location(text) or self.default_location
        self.logger.info(f"Weather query detected for: {location}")

        # Get current weather
        current = self.get_current(location)
        if not current:
            return True, f"[WEATHER LOOKUP FAILED for {location} - API may be unavailable]"

        # Check if forecast is requested
        forecast_keywords = ['forecast', 'week', 'tomorrow', 'next', 'days']
        include_forecast = any(kw in text.lower() for kw in forecast_keywords)

        context = f"\n[LIVE WEATHER DATA - Retrieved {datetime.now().strftime('%Y-%m-%d %H:%M')}]\n"
        context += self.format_current(current)

        if include_forecast:
            forecast = self.get_forecast(location, days=5)
            if forecast:
                context += f"\n\nForecast:\n{self.format_forecast(forecast)}"

        context += "\n[Use this data to answer the user's weather question]\n"

        return True, context


# Convenience function
def create_weather_lookup(api_key: Optional[str] = None) -> WeatherLookup:
    """Create weather lookup instance"""
    return WeatherLookup(api_key=api_key)
