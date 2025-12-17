# Siriwat Tidsuksai (Armmy)
# 670510727
# sec001


import json
from urllib.request import urlopen
from flask import jsonify
from app import app
from flask import Flask, render_template
from datetime import datetime


def read_web_page(url):
    assert url.startswith("https://")
    with urlopen(url) as res:
        return res.read()


@app.route('/weather')
def hw01_localweather():
    return app.send_static_file('hw01_localweather.html')


@app.route("/api/weather")
def api_weather():
    url = "https://air-quality-api.open-meteo.com/v1/air-quality?latitude=18.8037949&longitude=98.9499454&hourly=pm10,pm2_5,us_aqi&current=us_aqi,pm2_5,pm10&timezone=Asia%2FBangkok"
    response = read_web_page(url)
    data_json = json.loads(response)

    h = data_json['hourly']
    c = data_json['current']['time']

    idx = h['time'].index(c)
    nextidx = idx + 1

    CSet = {key: values[idx] for key, values in h.items()}
    NSet = {key: values[nextidx] for key, values in h.items()}

    data = {
        'current': CSet,
        'next_hr': NSet
    }

    return jsonify(data)


@app.route("/hw03/prcp/")
def hw03_prcp():
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=7.0084&longitude=100.4767&start_date=2025-11-01&end_date=2025-12-07&daily=precipitation_hours&timezone=Asia%2FBangkok"
    response = read_web_page(url)
    data_json = json.loads(response)
    daily = data_json["daily"]
    prev = None

    data = []
    for prcp1, prcp2 in zip(daily["time"], daily["precipitation_sum"]):
        date = datetime.strptime(prcp1, "%Y-%m-%d")
        day = date.strftime('%a')[:2]
        THEmonth = str(date.month)
        month = datetime.strptime(THEmonth, '%m').strftime("%b") 

        curr = prcp2
        if prev == None:
            arrow = ""
        elif curr > prev:
            arrow = "↑"
        elif curr < prev:
            arrow = "↓"
        else:
            arrow = "↔"
        prev = curr

        data.append({
            "year": date.year,
            "month": month,
            "day": date.day,
            "weekday": day,
            "prcp": prcp2,
            "arrow": arrow
        })

    return render_template('lab03/hw03_prcp.html', data=data)


@app.route("/api/hw3")
def apihw3():
    url = "https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=7.0084&longitude=100.4767&start_date=2025-11-01&end_date=2025-12-07&daily=precipitation_hours&timezone=Asia%2FBangkok"
    response = read_web_page(url)
    data_json = json.loads(response)
    daily = data_json["daily"]
    prev = None

    data = []
    for prcp1, prcp2 in zip(daily["time"], daily["precipitation_sum"]):
        date = datetime.strptime(prcp1, "%Y-%m-%d")
        day = date.strftime('%a')[:2]
        THEmonth = str(date.month)
        month = datetime.strptime(THEmonth, '%m').strftime("%b") 

        curr = prcp2
        if prev is None:
            arrow = ""
        elif curr > prev:
            arrow = "↑"
        elif curr < prev:
            arrow = "↓"
        else:
            arrow = "↔"
        prev = curr

        data.append({
            "year": date.year,
            "month": month,
            "day": date.day,
            "weekday": day,
            "prcp": prcp2,
            "arrow": arrow
        })

    return jsonify(data)
