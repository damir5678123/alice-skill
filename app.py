from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime
import random

app = Flask(__name__)

def get_horoscope(sign="овен", day="today"):
    """Получение гороскопа через Aztro API"""
    try:
        # Перевод русских названий на английские
        sign_translation = {
            "овен": "aries", "телец": "taurus", "близнецы": "gemini",
            "рак": "cancer", "лев": "leo", "дева": "virgo",
            "весы": "libra", "скорпион": "scorpio", "стрелец": "sagittarius",
            "козерог": "capricorn", "водолей": "aquarius", "рыбы": "pisces"
        }
        
        # Эмодзи для знаков
        sign_emojis = {
            "овен": "♈", "телец": "♉", "близнецы": "♊",
            "рак": "♋", "лев": "♌", "дева": "♍", 
            "весы": "♎", "скорпион": "♏", "стрелец": "♐",
            "козерог": "♑", "водолей": "♒", "рыбы": "♓"
        }
        
        english_sign = sign_translation.get(sign.lower(), "aries")
        emoji = sign_emojis.get(sign.lower(), "✨")
        
        url = f"https://aztro.sameerkumar.website/?sign={english_sign}&day={day}"
        response = requests.post(url, timeout=10)
        data = response.json()
        
        description = data.get('description', 'Гороскоп временно недоступен')
        lucky_number = data.get('lucky_number', '?')
        lucky_time = data.get('lucky_time', '?')
        mood = data.get('mood', '?')
        
        return f"{emoji} Гороскоп для {sign.capitalize()}:\n{description}\n\n🍀 Счастливое число: {lucky_number}\n⏰ Счастливое время: {lucky_time}\n😊 Настроение: {mood}"
        
    except Exception as e:
        print(f"Ошибка гороскопа: {e}")
        return "Не удалось получить гороскоп. Попробуйте позже."

def extract_zodiac_sign(command):
    """Извлекает знак зодиака из команды"""
    zodiac_signs = [
        "овен", "телец", "близнецы", "рак", "лев", "дева",
        "весы", "скорпион", "стрелец", "козерог", "водолей", "рыбы"
    ]
    
    command_lower = command.lower()
    for sign in zodiac_signs:
        if sign in command_lower:
            return sign
    return None

advices = [
    "Сегодня отличный день для изучения чего-то нового! 📚",
    "Не откладывай на завтра то, что можно сделать сегодня! ⏰",
    "Улыбнись - это повышает настроение! 😊",
    "Выпей стакан воды - это полезно для здоровья! 💧"
]

def get_currency_rates():
    try:
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url)
        data = response.json()
        
        usd = data['Valute']['USD']['Value']
        eur = data['Valute']['EUR']['Value']
        return f"💰 Курс: USD {usd}₽, EUR {eur}₽"
    except:
        return "Не удалось получить курс валют"

def get_weather(city_name):
    """Получение погоды через Open-Meteo API"""
    try:
        # Словарь для перевода русских названий городов
        city_translation = {
            "москва": "Moscow", "санкт-петербург": "Saint Petersburg", 
            "питер": "Saint Petersburg", "казань": "Kazan",
            "новосибирск": "Novosibirsk", "екатеринбург": "Yekaterinburg",
            "сочи": "Sochi", "крым": "Simferopol", "краснодар": "Krasnodar",
            "нижний новгород": "Nizhny Novgorod", "ростов": "Rostov-on-Don",
            "самара": "Samara", "омск": "Omsk", "челябинск": "Chelyabinsk",
            "уфа": "Ufa", "волгоград": "Volgograd", "пермь": "Perm",
            "воронеж": "Voronezh", "красноярск": "Krasnoyarsk"
        }
        
        # Преобразуем русское название в английское
        city_lower = city_name.lower().strip()
        english_city = city_translation.get(city_lower, city_name)
        
        print(f"Ищем погоду для: {english_city}")
        
        # 1. Получаем координаты города
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={english_city}&count=1&language=ru"
        geo_response = requests.get(geo_url, timeout=10)
        geo_data = geo_response.json()
        
        print(f"Геоданные: {geo_data}")
        
        if 'results' in geo_data and geo_data['results']:
            lat = geo_data['results'][0]['latitude']
            lon = geo_data['results'][0]['longitude']
            found_city_name = geo_data['results'][0]['name']
            
            # 2. Получаем погоду по координатам
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
            weather_response = requests.get(weather_url, timeout=10)
            weather_data = weather_response.json()
            
            print(f"Данные погоды: {weather_data}")
            
            if 'current_weather' in weather_data:
                temp = weather_data['current_weather']['temperature']
                windspeed = weather_data['current_weather']['windspeed']
                weathercode = weather_data['current_weather']['weathercode']
                
                # Преобразуем код погоды в текст
                weather_descriptions = {
                    0: "☀️ ясно", 1: "🌤️ малооблачно", 2: "⛅ переменная облачность",
                    3: "☁️ пасмурно", 45: "🌫️ туман", 48: "🌫️ изморозь",
                    51: "🌦️ легкая морось", 53: "🌦️ морось", 55: "🌧️ сильная морось",
                    61: "🌧️ небольшой дождь", 63: "🌧️ дождь", 65: "⛈️ сильный дождь",
                    71: "🌨️ небольшой снег", 73: "🌨️ снег", 75: "❄️ сильный снег",
                    80: "🌦️ ливень", 81: "🌧️ сильный ливень", 82: "⛈️ очень сильный ливень",
                    95: "⛈️ гроза"
                }
                
                weather_text = weather_descriptions.get(weathercode, "⛅ хорошая погода")
                
                return f"В {found_city_name} {temp}°C, {weather_text}, ветер {windspeed} км/ч"
            else:
                return "Не удалось получить данные о погоде"
        else:
            return "Город не найден. Попробуйте: Москва, Санкт-Петербург, Казань, Сочи"
            
    except requests.exceptions.Timeout:
        return "Превышено время ожидания. Попробуйте позже."
    except Exception as e:
        print(f"Ошибка в get_weather: {e}")
        return "Не удалось получить погоду. Попробуйте другой город."

def extract_city_from_command(command):
    """Извлекает название города из команды пользователя"""
    # Убираем ключевые слова
    keywords = ["погода", "в", "какая", "скажи", "покажи", "как", "что"]
    
    for keyword in keywords:
        command = command.replace(keyword, "")
    
    return command.strip()

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json

        if not data:
            return jsonify({
                "response": {
                    "text": "Пустой запрос",
                    "end_session": False
                }
            })

        user_command = data['request'].get('original_utterance', '').lower()
        session = data['session']
        version = data['version']

        print(f"Получена команда: {user_command}")

        # ОСНОВНАЯ ЛОГИКА НАВЫКА
        if user_command == '':
            response_text = "Привет! Я ваш умный помощник с настоящей погодой! 🌤️ Спросите: 'погода в Москве', 'курс валют', 'сколько время', 'расскажи шутку','совет','гороскоп' или 'помощь'"
        
        elif 'привет' in user_command:
            response_text = "Привет! Рад вас видеть! Спросите погоду в любом городе России! 🇷🇺"
        
        elif 'помощь' in user_command or 'что ты умеешь' in user_command:
            response_text = "Я умею: 🌤️ Показывать погоду в любом городе, 💰 Курсы валют, ⏰ Говорить время, 😄 Рассказывать шутки, 📚 Показывать интересные факты. Просто спросите!"
        
        elif 'время' in user_command or 'который час' in user_command:
            current_time = datetime.now().strftime("%H:%M")
            response_text = f"Сейчас {current_time} ⏰"
        # ГОРОСКОП
        elif 'гороскоп' in user_command or 'знак зодиака' in user_command:
            sign = extract_zodiac_sign(user_command)
                 if sign:
                     response_text = get_horoscope(sign)
                 else:
                    response_text = "Для какого знака зодиака гороскоп? Например: 'гороскоп для тельца' или 'гороскоп стрельца'"
        
        # КУРСЫ ВАЛЮТ - ДОБАВЛЕНО ПРАВИЛЬНО
        elif 'курс' in user_command or 'валют' in user_command:
            response_text = get_currency_rates()

        elif 'совет' in user_command:
            response_text = random.choice(advices)
            
        # ПОГОДА С OPEN-METEO
        elif 'погода' in user_command:
            if any(city in user_command for city in ['москв', 'питер', 'санкт-петербург', 'казан', 'новосибирск', 'екатеринбург', 'сочи']):
                # Для известных городов
                if 'москв' in user_command:
                    response_text = get_weather("москва")
                elif 'санкт-петербург' in user_command or 'питер' in user_command:
                    response_text = get_weather("санкт-петербург")
                elif 'казан' in user_command:
                    response_text = get_weather("казань")
                elif 'новосибирск' in user_command:
                    response_text = get_weather("новосибирск")
                elif 'екатеринбург' in user_command:
                    response_text = get_weather("екатеринбург")
                elif 'сочи' in user_command:
                    response_text = get_weather("сочи")
            else:
                # Для других городов - извлекаем название
                city = extract_city_from_command(user_command)
                if city:
                    response_text = get_weather(city)
                else:
                    response_text = "В каком городе показать погоду? Например: 'погода в Москве'"
        
        # ШУТКИ
        elif 'шутк' in user_command or 'пошути' in user_command:
            jokes = [
                "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25! 😄",
                "Как называется песня, которую поёт API? JSON-der-ella! 🎵",
                "Почему Python лучше Java? Потому что в Python нет NullPointerException! 🐍",
                "Что сказал один HTTP другому? Ты опять 404-й? 🌐",
                "Почему Python не нуждается в парковке? Потому что он интерпретируемый! 🚗"
            ]
            response_text = random.choice(jokes)
        
        # ФАКТЫ
        elif 'факт' in user_command or 'интересно' in user_command:
            facts = [
                "Open-Meteo API полностью бесплатный и без ограничений! Используется NASA и ECMWF данными 🛰️",
                "Первый программист была женщина - Ада Лавлейс, дочь поэта Байрона! 👩‍💻",
                "Python был назван в честь комедийного шоу 'Монти Пайтон', а не змеи! 🐍",
                "Самый популярный язык программирования в мире - JavaScript! 🌍",
                "Первая компьютерная мышь была сделана из дерева в 1964 году! 🖱️"
            ]
            response_text = random.choice(facts)

        else:
            response_text = f"Не понял команду '{user_command}'. Скажите 'помощь' для списка команд. 🤔"

        print(f"Отправляем ответ: {response_text}")

        response = {
            "version": version,
            "session": session,
            "response": {
                "text": response_text,
                "end_session": False
            }
        }

        return jsonify(response)

    except Exception as e:
        print(f"Ошибка в webhook: {e}")
        return jsonify({
            "response": {
                "text": "Произошла ошибка. Попробуйте еще раз.",
                "end_session": True
            }
        })

@app.route('/')
def home():
    return "Умный навык для Алисы с настоящей погодой и курсами валют! 🌤️💰"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)


