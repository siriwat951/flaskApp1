# Siriwat Tidsuksai (Armmy)
# 670510727
# sec001


import json
from urllib.request import urlopen
from flask import jsonify
from app import app
from flask import Flask, render_template


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
