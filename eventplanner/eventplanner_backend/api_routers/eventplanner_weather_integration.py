from collections import defaultdict
from datetime import datetime, timedelta

import requests
from fastapi import APIRouter
from eventplanner.eventplanner_backend.schemas.eventplanner_base_models import (
    Weather,
    HourlyWeatherData,
    TimeInterval,
    DailyWeatherData,
)

weather_management_router = APIRouter()


def create_weather_data(response):
    hourly_data_list = []
    for i in range(len(response.Hourly().Variables(0).ValuesAsNumpy())):
        hourly_data_list.append(
            HourlyWeatherData(
                time=datetime.fromtimestamp(
                    response.Hourly().Time()[i]
                ),  # Adjust as needed
                temperature_2m=response.Hourly().Variables(0).ValuesAsNumpy()[i],
                relative_humidity_2m=response.Hourly().Variables(1).ValuesAsNumpy()[i],
                dew_point_2m=response.Hourly().Variables(2).ValuesAsNumpy()[i],
                apparent_temperature=response.Hourly().Variables(3).ValuesAsNumpy()[i],
                precipitation_probability=response.Hourly()
                .Variables(4)
                .ValuesAsNumpy()[i],
                precipitation=response.Hourly().Variables(5).ValuesAsNumpy()[i],
                rain=response.Hourly().Variables(6).ValuesAsNumpy()[i],
                snowfall=response.Hourly().Variables(7).ValuesAsNumpy()[i],
                snow_depth=response.Hourly().Variables(8).ValuesAsNumpy()[i],
                wind_speed_80m=response.Hourly().Variables(9).ValuesAsNumpy()[i],
                temperature_180m=response.Hourly().Variables(10).ValuesAsNumpy()[i],
                soil_temperature_6cm=response.Hourly().Variables(11).ValuesAsNumpy()[i],
            )
        )
    return Weather(hourly_data=hourly_data_list)


@weather_management_router.get("/weather/data")
def fetch_and_create_weather_data(
    latitude: float, longitude: float, time_interval: TimeInterval = TimeInterval.DAY_7
):
    base_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "dew_point_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "rain",
            "snowfall",
            "snow_depth",
            "wind_speed_80m",
            "temperature_180m",
            "soil_temperature_6cm",
        ],
        "forecast_days": int(time_interval.value),
    }

    response = requests.get(base_url, params=params)
    response.raise_for_status()
    data = response.json()["hourly"]

    hourly_data_list = []
    for i in range(len(data["time"])):
        hourly_weather = HourlyWeatherData(
            time=datetime.fromisoformat(data["time"][i]),
            temperature_2m=data["temperature_2m"][i],
            relative_humidity_2m=data["relative_humidity_2m"][i],
            dew_point_2m=data["dew_point_2m"][i],
            apparent_temperature=data["apparent_temperature"][i],
            precipitation_probability=data["precipitation_probability"][i],
            precipitation=data["precipitation"][i],
            rain=data["rain"][i],
            snowfall=data["snowfall"][i],
            snow_depth=data["snow_depth"][i],
            wind_speed_80m=data["wind_speed_80m"][i],
            temperature_180m=data["temperature_180m"][i],
            soil_temperature_6cm=data["soil_temperature_6cm"][i],
        )
        hourly_data_list.append(hourly_weather)

    daily_list = []
    for day in range(int(time_interval.value)):
        daily_weather_data = hourly_data_list[day * 24 : (day + 1) * 24]
        daily_list.append(
            DailyWeatherData(
                date=daily_weather_data[0].time.date(), hourly_data=daily_weather_data
            )
        )
    return daily_list
