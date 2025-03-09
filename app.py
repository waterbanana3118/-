from flask import Flask, render_template, request
import requests

API_KEY = "CWA-DC1449B4-41B2-4C6E-A288-857A1155EA5E"
BASE_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001"

app = Flask(__name__)

def get_weather(location):
    """查詢天氣並提供小建議"""
    params = {
        "Authorization": API_KEY,
        "locationName": location
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if not data.get("records", {}).get("location"):
            return None, f"❌ 找不到 {location} 的天氣資訊。"

        location_data = data["records"]["location"][0]
        city = location_data["locationName"]
        weather = location_data["weatherElement"][0]["time"][0]["parameter"]["parameterName"]
        temp_min = int(location_data["weatherElement"][2]["time"][0]["parameter"]["parameterName"])
        temp_max = int(location_data["weatherElement"][4]["time"][0]["parameter"]["parameterName"])
        rain_prob = int(location_data["weatherElement"][1]["time"][0]["parameter"]["parameterName"])

        result = {
            "city": city,
            "weather": weather,
            "temp_min": temp_min,
            "temp_max": temp_max,
            "rain_prob": rain_prob,
        }

        # 組裝建議文字
        suggestion = "🔸 小建議："
        if temp_min < 10:
            suggestion += "哇！這是寒流嗎？一定要穿厚外套，不然會凍壞的！"
        elif temp_min < 15:
            suggestion += "今天天氣有點冷，不穿外套容易感冒！"
        elif temp_min < 20:
            suggestion += "今天有點涼，記得穿件外套保暖！"
        else:
            suggestion += "氣溫還不錯，穿著舒適就好！"

        if "雨" in weather:
            suggestion += " 而且正在下雨，記得帶傘！"
        elif "陰" in weather and rain_prob > 30:
            suggestion += " 今天陰天且有較高降雨機率，建議帶把傘！"

        result["suggestion"] = suggestion

        return result, None

    except requests.exceptions.RequestException as e:
        return None, f"❌ 無法獲取天氣資訊：{e}"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        location = request.form.get("location", "").strip()
        if not location:
            return render_template("index.html", error="請輸入城市名稱！")
        weather_info, error = get_weather(location)
        if error:
            return render_template("index.html", error=error)
        return render_template("index.html", weather=weather_info)
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
