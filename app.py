import sys
from urllib import request, error, parse

from configparser import ConfigParser
import requests, base64
from flask import Flask, render_template, request
import logging
import os
from PIL import Image

app = Flask(__name__)


base_weather_app_url = "http://api.openweathermap.org/data/2.5/weather"

background_images = {
    'clear sky': 'clear_sky.png',
    'few clouds': 'few_clouds.png',
    'scattered clouds': 'scattered_clouds.png',
    'broken clouds': 'broken_clouds.png',
    'overcast clouds': 'broken_clouds.png',
    'thunderstorm with light rain': 'thunderstorm.png',
    'thunderstorm with rain': 'thunderstorm.png',
    'thunderstorm with heavy rain': 'thunderstorm.png',
    'light thunderstorm': 'thunderstorm.png',
    'thunderstorm': 'thunderstorm.png',
    'heavy thunderstorm': 'thunderstorm.png',
    'ragged thunderstorm': 'thunderstorm.png',
    'thunderstorm with light drizzle': 'thunderstorm.png',
    'thunderstorm with drizzle': 'thunderstorm.png',
    'thunderstorm with heavy drizzle': 'thunderstorm.png',
    'light intensity drizzle': 'mist.png',
    'drizzle': 'mist.png',
    'heavy intensity drizzle': 'mist.png',
    'light intensity drizzle rain': 'mist.png',
    'drizzle rain': 'mist.png',
    'heavy intensity drizzle rain': 'mist.png',
    'shower rain and drizzle': 'mist.png',
    'heavy shower rain and drizzle': 'mist.png',
    'shower drizzle': 'mist.png',
    'light rain': 'rain.png',
    'moderate rain': 'rain.png',
    'heavy intensity rain': 'rain.png',
    'very heavy rain': 'rain.png',
    'extreme rain': 'rain.png',
    'freezing rain': 'rain.png',
    'light intensity shower rain': 'rain.png',
    'shower rain': 'rain.png',
    'heavy intensity shower rain': 'rain.png',
    'ragged shower rain': 'rain.png',
    'light snow': 'snow.png',
    'snow': 'snow.png',
    'heavy snow': 'snow.png',
    'sleet': 'snow.png',
    'light shower sleet': 'snow.png',
    'shower sleet': 'snow.png',
    'light rain and snow': 'snow.png',
    'rain and snow': 'snow.png',
    'light shower snow': 'snow.png',
    'shower snow': 'snow.png',
    'heavy shower snow': 'snow.png',
    'mist': 'mist.png',
}


def _get_api_key():
    """Fetch the API key from your configuration file.
    Expects a configuration file named "secrets.ini" with structure:

        [openweather]
        api_key=<YOUR-OPENWEATHER-API-KEY>
    """
    config = ConfigParser()
    config.read("secrets.ini")
    return config["openweather"]["api_key"]


@app.route("/")
def root():
    return render_template('weather_index.html')


def build_weather_url(imperial=True):

    api_key = _get_api_key()
    city = request.form["city"].strip()
    url_encoded_city_name = parse.quote_plus(city)
    units = "imperial" if imperial else "metric"
    url = (f"{base_weather_app_url}?q={url_encoded_city_name}"
           f"&units={units}&appid={api_key}"
           )
    return url


@app.route("/weather", methods=["GET", "POST"])
def get_weather():
    api_key = _get_api_key()
    city = request.form["city"].strip()
    url = build_weather_url(imperial=True)

    try:
        response = requests.get(url)

    except error.HTTPError as http_error:
        if http_error.code == 401:
            sys.exit("Access denied. Check your API key.")
        elif http_error.code == 404:
            sys.exit(f"Failed to get weather data for {city}")
        else:
            sys.exit(f"Something went wrong...{http_error.code}")

    weather_data = response.json()

    logging.debug(f"weather_data: {weather_data}")
    # print(weather_data)

    longitude = weather_data["coord"]["lon"]
    latitude = weather_data["coord"]["lat"]
    city = weather_data["name"]
    country = weather_data["sys"]["country"]
    weather_condition = weather_data["weather"][0]["description"]
    weather = weather_condition.capitalize()
    temperature = round(weather_data["main"]["temp"])
    real_feel = round(weather_data["main"]["feels_like"])
    min_temperature = round(weather_data["main"]["temp_min"])
    max_temperature = round(weather_data["main"]["temp_max"])
    humidity = weather_data["main"]["humidity"]
    wind_speed = round(weather_data["wind"]["speed"])
    icon_id = weather_data["weather"][0]['icon']
    icon_url = f'http://openweathermap.org/img/wn/{icon_id}.png'
    icon_response = requests.get(icon_url)
    icon_data = icon_response.content

    with open('static/weather_icon.png', 'wb') as f:
        f.write(icon_data)

    # geo_url = (f"http://api.openweathermap.org/data/2.5/solar_radiation?lat={latitude}&lon={longitude}&appid={api_key}")
    #
    # try:
    #     geo_response = requests.get(geo_url)
    #
    # except error.HTTPError as http_error:
    #     if http_error.code == 401:
    #         sys.exit("Access denied. Check your API key.")
    #     elif http_error.code == 404:
    #         sys.exit(f"Failed to get weather data for {city}")
    #     else:
    #         sys.exit(f"Something went wrong...{http_error.code}")
    #
    # geo_data = geo_response.json()
    # print(f'geo data: {geo_data}')

    background_image = background_images.get(weather_condition, 'default.png')

    return render_template("weather.html",
                           api_key=api_key,
                           city=city,
                           weather=weather,
                           temperature=temperature,
                           real_feel=real_feel,
                           humidity=humidity,
                           wind_speed=wind_speed,
                           longitude=longitude,
                           latitude=latitude,
                           country=country,
                           background_image=background_image,
                           min_temperature=min_temperature,
                           max_temperature=max_temperature,
                            )


if __name__ == "__main__":
    app.run(debug=True)