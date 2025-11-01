from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

# Ключ для погоды (бесплатный с openweathermap.org)
WEATHER_API_KEY = "ваш_ключ"  # Получите на openweathermap.org


def get_weather(city="Москва"):
    """Получение погоды"""
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temp = data['main']['temp']
            description = data['weather'][0]['description']
            return f"В {city} сейчас {temp}°C, {description}"
        else:
            return "Не удалось получить погоду"
    except:
        return "Ошибка при получении погоды"


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

        # ОСНОВНАЯ ЛОГИКА НАВЫКА
        if user_command == '':
            response_text = "Привет! Я улучшенный навык! Скажите: погода, время, расскажи шутку, или помощь"

        elif 'привет' in user_command:
            response_text = "Приветствую! Рад вас видеть!"

        elif 'помощь' in user_command or 'что ты умеешь' in user_command:
            response_text = "Я умею: говорить время, рассказывать погоду, шутить, считать и многое другое! Попробуйте!"

        elif 'время' in user_command or 'который час' in user_command:
            current_time = datetime.now().strftime("%H:%M")
            response_text = f"Сейчас {current_time}"

        # НОВАЯ ФУНКЦИЯ: ПОГОДА
        elif 'погода' in user_command:
            if 'москв' in user_command:
                response_text = get_weather("Moscow")
            elif 'санкт-петербург' in user_command or 'питер' in user_command:
                response_text = get_weather("Saint Petersburg")
            else:
                response_text = get_weather()

        # НОВАЯ ФУНКЦИЯ: ШУТКИ
        elif 'шутк' in user_command or 'пошути' in user_command:
            jokes = [
                "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25!",
                "Как называется песня, которую поёт API? JSON-der-ella!",
                "Почему Python стал таким популярным? Потому что у него есть змеиное очарование!",
                "Что сказал один HTTP другому? Ты опять 404-й?"
            ]
            import random
            response_text = random.choice(jokes)

        # НОВАЯ ФУНКЦИЯ: КАЛЬКУЛЯТОР
        elif 'сколько будет' in user_command or 'посчитай' in user_command:
            try:
                # Простой калькулятор
                expr = user_command.replace('сколько будет', '').replace('посчитай', '').strip()
                result = eval(expr)  # осторожно с eval!
                response_text = f"{expr} = {result}"
            except:
                response_text = "Не могу посчитать. Попробуйте например: сколько будет 2+2"

        # НОВАЯ ФУНКЦИЯ: ФАКТЫ
        elif 'факт' in user_command or 'интересно' in user_command:
            facts = [
                "Знаете ли вы, что первый программист была женщина - Ада Лавлейс!",
                "Python был назван не в честь змеи, а в честь комедийного шоу 'Монти Пайтон'!",
                "Самый популярный язык программирования в мире - JavaScript!",
                "Первая компьютерная мышь была сделана из дерева!"
            ]
            import random
            response_text = random.choice(facts)

        else:
            response_text = f"Вы сказали: '{user_command}'. Я еще учусь! Скажите 'помощь' для списка команд."

        # Формируем ответ
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
        print(f"Ошибка: {e}")
        return jsonify({
            "response": {
                "text": "Произошла ошибка",
                "end_session": True
            }
        })


@app.route('/')
def home():
    return "Улучшенный навык для Алисы работает!"


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)