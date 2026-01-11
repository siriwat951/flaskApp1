# Siriwat Tidsuksai (Armmy)
# 670510727
# sec001


import json
from urllib import response
from urllib.request import urlopen
from flask import jsonify
from app import app
from flask import Flask, render_template
from datetime import datetime
from app.forms import forms



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
    
    
@app.route("/hw04")
def hw04_rwd():
    return app.send_static_file('hw04_rwd.html')


def get_quality_class(avg):
    if avg <= 50:
        return "good"
    elif avg <= 100:
        return "moderate"
    elif avg <= 150:
        return "unhealthy-sensitive"
    elif avg <= 200:
        return "unhealthy"
    elif avg <= 300:
        return "very-unhealthy"
    else:
        return "hazardous"


@app.route("/api/hw05")
def apihw5():
    urlB = "https://api.waqi.info/feed/here/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseB = read_web_page(urlB)
    data_jsonB = json.loads(responseB)

    forecastB = []

    pm25_dailyB = data_jsonB['data']['forecast']['daily']['pm25']

    for i in range(1, 4):
        avg = pm25_dailyB[i]['avg']
        
        forecastB.append({
            "aqi": avg,
            "day": pm25_dailyB[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataB = {
    "aqi": data_jsonB['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": data_jsonB['data']['city']['name'],
    "date": data_jsonB['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastB
    }

    urlC = "https://api.waqi.info/feed/@5775/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseC = read_web_page(urlC)
    data_jsonC = json.loads(responseC)

    forecastC = []
    pm25_dailyC = data_jsonC['data']['forecast']['daily']['pm25']

    for i in range(1, 4):
        avg = pm25_dailyC[i]['avg']
        
        forecastC.append({
            "aqi": avg,
            "day": pm25_dailyC[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataC = {
    "aqi": data_jsonC['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": data_jsonC['data']['city']['name'],
    "date": data_jsonC['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastC
    }

    urlU = "https://api.waqi.info/feed/@12797/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseU = read_web_page(urlU)
    data_jsonU = json.loads(responseU)

    forecastU = []
    pm25_dailyU = data_jsonU['data']['forecast']['daily']['pm25']
    for i in range(1, 4):
        avg = pm25_dailyU[i]['avg']

        forecastU.append({
            "aqi": avg,
            "day": pm25_dailyU[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataU = {
    "aqi": data_jsonU['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": 'Ubon Ratchathani',
    "date": data_jsonU['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastU
    }

    urlP = "https://api.waqi.info/feed/@1827/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseP = read_web_page(urlP)
    data_jsonP = json.loads(responseP)

    forecastP = []
    pm25_dailyP = data_jsonP['data']['forecast']['daily']['pm25']
    for i in range(1, 4):
        avg = pm25_dailyP[i]['avg']

        forecastP.append({
            "aqi": avg,
            "day": pm25_dailyP[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataP = {
    "aqi": data_jsonP['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": 'Phuket',
    "date": data_jsonP['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastP
    }

    dataall = {
        'Chiang_Mai': dataC,
        'Ubon': dataU,
        'Bangkok': dataB,
        'Phuket': dataP
    }

    return jsonify(dataall)


@app.route("/hw05/aqicard")
def hw05_aqicard():
    urlB = "https://api.waqi.info/feed/here/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseB = read_web_page(urlB)
    data_jsonB = json.loads(responseB)

    forecastB = []

    pm25_dailyB = data_jsonB['data']['forecast']['daily']['pm25']

    for i in range(1, 4):
        avg = pm25_dailyB[i]['avg']
        
        forecastB.append({
            "aqi": avg,
            "day": pm25_dailyB[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataB = {
    "aqi": data_jsonB['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": data_jsonB['data']['city']['name'],
    "date": data_jsonB['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastB
    }

    urlC = "https://api.waqi.info/feed/@5775/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseC = read_web_page(urlC)
    data_jsonC = json.loads(responseC)

    forecastC = []
    pm25_dailyC = data_jsonC['data']['forecast']['daily']['pm25']

    for i in range(1, 4):
        avg = pm25_dailyC[i]['avg']
        
        forecastC.append({
            "aqi": avg,
            "day": pm25_dailyC[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataC = {
    "aqi": data_jsonC['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": data_jsonC['data']['city']['name'],
    "date": data_jsonC['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastC
    }

    urlU = "https://api.waqi.info/feed/@12797/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseU = read_web_page(urlU)
    data_jsonU = json.loads(responseU)

    forecastU = []
    pm25_dailyU = data_jsonU['data']['forecast']['daily']['pm25']
    for i in range(1, 4):
        avg = pm25_dailyU[i]['avg']

        forecastU.append({
            "aqi": avg,
            "day": pm25_dailyU[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataU = {
    "aqi": data_jsonU['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": 'Ubon Ratchathani',
    "date": data_jsonU['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastU
    }

    urlP = "https://api.waqi.info/feed/@1827/?token=5881668d3bc2c2b7a4186d643095627c584ba14c"
    responseP = read_web_page(urlP)
    data_jsonP = json.loads(responseP)

    forecastP = []
    pm25_dailyP = data_jsonP['data']['forecast']['daily']['pm25']
    for i in range(1, 4):
        avg = pm25_dailyP[i]['avg']

        forecastP.append({
            "aqi": avg,
            "day": pm25_dailyP[i]['day'],
            "quality-class": get_quality_class(avg)
        })

    dataP = {
    "aqi": data_jsonP['data']['forecast']['daily']['pm25'][0]['avg'],
    "city": 'Phuket',
    "date": data_jsonP['data']['forecast']['daily']['pm25'][0]['day'],
    "forecast": forecastP
    }

    dataall = {
        'Chiang_Mai': dataC,
        'Ubon': dataU,
        'Bangkok': dataB,
        'Phuket': dataP
    }

    return render_template('hw05_aqicard.html', data=dataall)


def read_file(filename, mode="rt"):
    with open(filename, mode, encoding='utf-8') as fin:
        return fin.read()

def write_file(filename, contents, mode="wt"):
    with open(filename, mode, encoding="utf-8") as fout:
        fout.write(contents)

@app.route('/hw06/register/', methods=('GET', 'POST'))
def lab06_hw06_register():
    form = forms.RegistrationForm()
    if form.validate_on_submit():
        raw_json = read_file('data/users.json')
        users = json.loads(raw_json)
        users.append({'username': form.username.data,
                            'email': form.email.data,
                            'password': form.password.data,
                            'confirm_password': form.confirm_password.data,
                            })
        write_file('data/users.json',
                   json.dumps(users, indent=4))
        return redirect(url_for('lab06_hw06_users'))
    return render_template('lab06/hw06_register.html', form=form)

@app.route('/hw06/users/', methods=('GET', 'POST'))
def lab06_hw06_users():
    raw_json = read_file('data/users.json')
    course_list = json.loads(raw_json)
    return render_template('lab06/hw06_users.html', course_list=course_list)

