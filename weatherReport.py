# -*- coding: UTF-8 -*-
import os
import urllib
import json
import time
import requests
import sys
from fbchat import Client
from fbchat.models import Message

# AccuWeather API setup
ACCUWEATHER_KEY          = os.environ['ACCUWEATHER_KEY']
LOCATION_KEY             = "49524_PC"   # Waterloo, ON, Canada
ACCUWEATHER_FORECAST_URL = "http://dataservice.accuweather.com/forecasts/v1/daily/1day/" + LOCATION_KEY
ACCUWEATHER_ALARM_URL    = "http://dataservice.accuweather.com/alarms/v1/1day/" + LOCATION_KEY

# FBChat API setup
FB_USER     = os.environ["FB_USER"]
FB_PASSWORD = os.environ["FB_PASSWORD"]

def getAlertText( alertType ):
    if( alertType == "Ice" ):
        return "Slippery conditions today! Be careful! 🌡 ⛸"
    elif( alertType == "Rain" ):
        return "Remember your umbrella, today's forecast calls for rain! 🌧 ☔"
    elif( alertType == "Snow" ):
        return "You'll be walking in a winter wonderland, because it is supposed to snow today! 🌨 ❄ "
    elif( alertType == "Wind" ):
        return "Be sure to bundle up, because it's going to be windy today! 🌪"
    elif( alertType == "WindGust" ):
        return "Hold on to your hat, wind gusts of over 60kph are in store for today!  🌬 💨"
    elif( alertType == "Thunderstorm" ):
        return "THUNDER!!! OOoooOOOOooooOOOOooOOh (thunderstorms are in store for today)! ⛈ ⚡"
    else :
        return "Unrecognized alert type."

if __name__ == '__main__':

    fbClient    = Client(FB_USER, FB_PASSWORD)
    fbUsers     = fbClient.fetchAllUsers()
    fbUsersList = [user.uid for user in fbUsers if user.uid != "0"]

    # Getting weather information
    forecastPayload = {
        "apikey"  : ACCUWEATHER_KEY,
        "details" : True,
        "metric"  : True
    }

    alertPayload = {
        "apikey" : ACCUWEATHER_KEY
    }

    r = requests.get(ACCUWEATHER_FORECAST_URL, params=forecastPayload)
    weatherForecast = r.json()

    r = requests.get(ACCUWEATHER_ALARM_URL, params=alertPayload)
    weatherAlerts = r.json()

    dailyMinimum = weatherForecast["DailyForecasts"][0]["Temperature"]["Minimum"]["Value"]
    dailyMaximum = weatherForecast["DailyForecasts"][0]["Temperature"]["Maximum"]["Value"]
    feelsLikeMinimum = weatherForecast["DailyForecasts"][0]["RealFeelTemperature"]["Minimum"]["Value"]
    feelsLikeMaximum = weatherForecast["DailyForecasts"][0]["RealFeelTemperature"]["Maximum"]["Value"]
    weatherSummary = weatherForecast["DailyForecasts"][0]["Day"]["LongPhrase"].lower()

    alerts = []

    if len(weatherAlerts) > 0:
        for alert in weatherAlerts[0]["Alarms"] :
            alertType = alert["AlarmType"]
            alertText = getAlertText( alertType )
            alerts.append(alertText)

    forecastMessage = Message(
                        text="Good morning!\nToday's weather is " + weatherSummary + 
                             "\n\nHigh: " + str(dailyMaximum) + u"°\n(feels like " + str(feelsLikeMaximum) + u"°)" +
                             "\nLow: " + str(dailyMinimum) + u"°\n(feels like " + str(feelsLikeMinimum) + u"°)" )

    # Sending weather updates
    for id in fbUsersList :
        fbClient.send(forecastMessage, thread_id=id)

        for alertText in alerts :
            alertMessage = Message(text=alertText)
            fbClient.send(alertMessage, thread_id=id)

        time.sleep(5)       # sleep for 5 seconds to avoid being too spammy
    
    fbClient.logout()
