import requests

url = "https://api.openweathermap.org/data/2.5/weather?q=Nuwara%20Eliya,LK&units=metric&appid=your_api_key_here"
# I will make a curl call to open weather to see their standard payload format
import urllib.request
import json
try:
    response = urllib.request.urlopen("https://api.weather.gov/v1/this_is_just_a_placeholder")
except:
    pass
