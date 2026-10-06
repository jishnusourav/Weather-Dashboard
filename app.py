from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/weather", methods=["POST"])
def weather():

    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "error": "No data received."
            }), 400

        city = data.get("city", "").strip()

        if not city:
            return jsonify({
                "error": "Please enter a city name."
            }), 400

        # -------------------------------------------------
        # 1. FIND CITY
        # -------------------------------------------------

        geo_params = {
            "name": city,
            "count": 5,
            "language": "en",
            "format": "json"
        }

        geo_response = requests.get(
            GEOCODING_URL,
            params=geo_params,
            timeout=10
        )

        geo_response.raise_for_status()

        geo_data = geo_response.json()

        if not geo_data.get("results"):
            return jsonify({
                "error": f"Could not find '{city}'. Try a different city name."
            }), 404

        results = geo_data["results"]

        # Prefer an exact city-name match when available
        location = results[0]

        city_lower = city.lower()

        for result in results:

            result_name = result.get(
                "name",
                ""
            ).lower()

            if result_name == city_lower:
                location = result
                break

        latitude = location["latitude"]
        longitude = location["longitude"]

        city_name = location.get("name", city)

        country = location.get(
            "country",
            ""
        )

        country_code = location.get(
            "country_code",
            ""
        )

        admin1 = location.get(
            "admin1",
            ""
        )

        elevation = location.get(
            "elevation",
            None
        )

        # -------------------------------------------------
        # 2. WEATHER REQUEST
        # -------------------------------------------------

        current_variables = ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "rain",
            "showers",
            "weather_code",
            "cloud_cover",
            "pressure_msl",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
            "visibility",
            "is_day"
        ])

        daily_variables = ",".join([
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "precipitation_sum",
            "rain_sum",
            "precipitation_hours",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "wind_direction_10m_dominant",
            "uv_index_max",
            "sunrise",
            "sunset"
        ])

        weather_params = {
            "latitude": latitude,
            "longitude": longitude,

            "current": current_variables,

            "daily": daily_variables,

            "forecast_days": 7,

            "timezone": "auto",

            "temperature_unit": "celsius",

            "wind_speed_unit": "kmh",

            "precipitation_unit": "mm",

            "timeformat": "iso8601"
        }

        weather_response = requests.get(
            WEATHER_URL,
            params=weather_params,
            timeout=15
        )

        weather_response.raise_for_status()

        weather_data = weather_response.json()

        current = weather_data.get("current", {})
        current_units = weather_data.get(
            "current_units",
            {}
        )

        daily = weather_data.get("daily", {})

        if not current:
            return jsonify({
                "error": "Weather information is unavailable right now."
            }), 500

        weather_code = current.get(
            "weather_code",
            0
        )

        description, icon = get_weather_info(
            weather_code
        )

        wind_direction = current.get(
            "wind_direction_10m"
        )

        wind_direction_text = get_wind_direction(
            wind_direction
        )

        # -------------------------------------------------
        # 3. BUILD 7-DAY FORECAST
        # -------------------------------------------------

        forecast = []

        dates = daily.get("time", [])

        for i in range(len(dates)):

            day_code = daily["weather_code"][i]

            day_description, day_icon = get_weather_info(
                day_code
            )

            forecast.append({
                "date": dates[i],

                "icon": day_icon,

                "description": day_description,

                "max_temp": round(
                    daily["temperature_2m_max"][i]
                ),

                "min_temp": round(
                    daily["temperature_2m_min"][i]
                ),

                "feels_max": round(
                    daily["apparent_temperature_max"][i]
                ),

                "feels_min": round(
                    daily["apparent_temperature_min"][i]
                ),

                "precipitation": round(
                    daily["precipitation_sum"][i],
                    1
                ),

                "rain": round(
                    daily["rain_sum"][i],
                    1
                ),

                "precipitation_probability": (
                    daily[
                        "precipitation_probability_max"
                    ][i]
                ),

                "wind_speed": round(
                    daily["wind_speed_10m_max"][i],
                    1
                ),

                "wind_gusts": round(
                    daily["wind_gusts_10m_max"][i],
                    1
                ),

                "uv_index": round(
                    daily["uv_index_max"][i],
                    1
                ),

                "sunrise": daily["sunrise"][i],

                "sunset": daily["sunset"][i]
            })

        # -------------------------------------------------
        # 4. SEND RESULT TO FRONTEND
        # -------------------------------------------------

        result = {

            "location": {
                "city": city_name,
                "country": country,
                "country_code": country_code,
                "state": admin1,
                "latitude": latitude,
                "longitude": longitude,
                "elevation": elevation,
                "timezone": weather_data.get(
                    "timezone",
                    ""
                )
            },

            "current": {

                "time": current.get("time"),

                "temperature": current.get(
                    "temperature_2m"
                ),

                "humidity": current.get(
                    "relative_humidity_2m"
                ),

                "feels_like": current.get(
                    "apparent_temperature"
                ),

                "precipitation": current.get(
                    "precipitation"
                ),

                "rain": current.get(
                    "rain"
                ),

                "showers": current.get(
                    "showers"
                ),

                "cloud_cover": current.get(
                    "cloud_cover"
                ),

                "pressure": current.get(
                    "pressure_msl"
                ),

                "surface_pressure": current.get(
                    "surface_pressure"
                ),

                "wind_speed": current.get(
                    "wind_speed_10m"
                ),

                "wind_direction": wind_direction,

                "wind_direction_text": wind_direction_text,

                "wind_gusts": current.get(
                    "wind_gusts_10m"
                ),

                "visibility": current.get(
                    "visibility"
                ),

                "is_day": current.get(
                    "is_day"
                ),

                "weather_code": weather_code,

                "description": description,

                "icon": icon
            },

            "units": current_units,

            "forecast": forecast
        }

        return jsonify(result)

    except requests.exceptions.Timeout:

        return jsonify({
            "error": "The weather service took too long to respond. Please try again."
        }), 504

    except requests.exceptions.RequestException as e:

        print("API Error:", e)

        return jsonify({
            "error": "Unable to connect to the weather service."
        }), 500

    except Exception as e:

        print("Application Error:", e)

        return jsonify({
            "error": "Something went wrong. Please try again."
        }), 500


# -------------------------------------------------
# WEATHER CODE
# -------------------------------------------------

def get_weather_info(code):

    weather_conditions = {

        0: ("Clear Sky", "☀️"),

        1: ("Mainly Clear", "🌤️"),

        2: ("Partly Cloudy", "⛅"),

        3: ("Overcast", "☁️"),

        45: ("Fog", "🌫️"),

        48: ("Rime Fog", "🌫️"),

        51: ("Light Drizzle", "🌦️"),

        53: ("Drizzle", "🌦️"),

        55: ("Heavy Drizzle", "🌧️"),

        56: ("Freezing Drizzle", "🌧️"),

        57: ("Heavy Freezing Drizzle", "🌧️"),

        61: ("Light Rain", "🌦️"),

        63: ("Moderate Rain", "🌧️"),

        65: ("Heavy Rain", "🌧️"),

        66: ("Freezing Rain", "🌧️"),

        67: ("Heavy Freezing Rain", "🌧️"),

        71: ("Light Snow", "🌨️"),

        73: ("Snow", "❄️"),

        75: ("Heavy Snow", "❄️"),

        77: ("Snow Grains", "❄️"),

        80: ("Light Rain Showers", "🌦️"),

        81: ("Rain Showers", "🌧️"),

        82: ("Heavy Rain Showers", "⛈️"),

        85: ("Snow Showers", "🌨️"),

        86: ("Heavy Snow Showers", "❄️"),

        95: ("Thunderstorm", "⛈️"),

        96: ("Thunderstorm with Hail", "⛈️"),

        99: ("Heavy Thunderstorm with Hail", "⛈️")
    }

    return weather_conditions.get(
        code,
        ("Unknown Weather", "🌍")
    )


# -------------------------------------------------
# WIND DIRECTION
# -------------------------------------------------

def get_wind_direction(degrees):

    if degrees is None:
        return "Unknown"

    directions = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW"
    ]

    index = round(degrees / 22.5) % 16

    return directions[index]


if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )