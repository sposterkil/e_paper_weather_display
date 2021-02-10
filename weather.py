import sys
import os

picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "pic")
icondir = os.path.join(picdir, "icon")
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "font")

# Search lib folder for display driver modules
sys.path.append("lib")
from waveshare_epd import epd4in2_V2

from datetime import datetime
import time
from PIL import Image, ImageDraw, ImageFont
import traceback
import telnetlib

import requests, json
from io import BytesIO
import csv

# Set the fonts
font22 = ImageFont.truetype(os.path.join(fontdir, "Font.ttc"), 22)
font30 = ImageFont.truetype(os.path.join(fontdir, "Font.ttc"), 30)
font35 = ImageFont.truetype(os.path.join(fontdir, "Font.ttc"), 35)
font50 = ImageFont.truetype(os.path.join(fontdir, "Font.ttc"), 50)
font60 = ImageFont.truetype(os.path.join(fontdir, "Font.ttc"), 60)
font100 = ImageFont.truetype(os.path.join(fontdir, "Font.ttc"), 100)
font160 = ImageFont.truetype(os.path.join(fontdir, "Font.ttc"), 160)
# Set the colors
black = "rgb(0,0,0)"
white = "rgb(255,255,255)"
grey = "rgb(235,235,235)"

API_KEY = "API KEY"
LOCATION = "Munich"
LATITUDE = "48.137154"
LONGITUDE = "11.576124"


def get_weather(lat, lon, api_key, units="imperial"):
    url = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&appid={api_key}&units={units}"
    response = requests.get(url)
    if not response.ok:
        raise Exception(response.json()["message"])
    body = response.json()
    return {
        "current_temp": body["current"]["temp"],
        "current_conditions": ", ".join(
            [condition["main"] for condition in body["current"]["weather"]]
        ),
        "forecast": [(day["temp"]["max"], day["temp"]["min"]) for day in body["daily"]][
            :3
        ],  # > [(279.4, 273.15), (279.4, 273.15)]
    }


def get_now_playing():
    url = f"http://192.168.178.167:81/api/track/metadata"
    response = requests.get(url)
    if not response.ok:
        raise Exception(response.json()["message"])
    body = response.json()
    return body


# define function for displaying error
def write_error_image(error_source):
    # Display an error
    print("Error in the", error_source, "request.")
    # Initialize drawing
    error_image = Image.new("1", (400, 300), 255)
    # Initialize the drawing
    draw = ImageDraw.Draw(error_image)
    draw.text((100, 150), error_source + " ERROR", font=font50, fill=black)
    draw.text((100, 300), "Retrying in 30 seconds", font=font22, fill=black)
    current_time = datetime.now().strftime("%H:%M")
    draw.text((300, 365), "Last Refresh: " + str(current_time), font=font50, fill=black)
    # Save the error image
    error_image_file = "error.png"
    error_image.save(os.path.join(picdir, error_image_file))
    # Close error image
    error_image.close()


def write_image(weather, music):
    # Something like
    image = Image.new("1", (400, 300), 255)
    draw = ImageDraw.Draw(image)  # make a new image object
    draw.text(weather, (10, 10), font=font50, fill=black)  # write Weather onto it
    draw.text(music, (200, 200), font=font50, fill=black)  # write Music onto it
    image_file = "image.png"
    image.save(os.path.join(picdir, image_file))
    image.close()


def display_image(image_path, epd):
    screen_output_file = Image.open(image_path)
    assert screen_output_file.width == epd.width
    assert screen_output_file.height == epd.height

    epd.display(epd.getbuffer(screen_output_file))


if __name__ == "main":
    print("Initializing and clearing screen.")
    epd = epd4in2_V2.EPD()
    epd.init()
    epd.Clear()

    weather = get_weather(lat, lon, api_key)
