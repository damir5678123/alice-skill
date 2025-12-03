from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime
import random

app = Flask(__name__)

# Глобальные переменные для хранения состояния игры
game_state = {
    'active': False,
    'used_cities': [],
    'last_city': '',
    'player_name': '',
    'score': {'user': 0, 'bot': 0}
}

# База данных городов России
russian_cities = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Оренбург", "Орск", "Новотроицк", "Гай", "Бузулук", "Бугуруслан",
    "Кувандык", "Медногорск", "Соль-Илецк", "Ясный", "Абдулино",
    "Самара", "Челябинск", "Уфа", "Ростов-на-Дону", "Волгоград",
    "Пермь", "Краснодар", "Воронеж", "Саратов", "Тюмень", "Тольятти",
    "Ижевск", "Барнаул", "Ульяновск", "Иркутск", "Хабаровск", "Ярославль",
    "Владивосток", "Махачкала", "Томск", "Омск", "Кемерово", "Новокузнецк",
    "Рязань", "Астрахань", "Пенза", "Липецк", "Киров", "Чебоксары",
    "Калининград", "Тула", "Курск", "Сочи", "Ставрополь", "Магнитогорск"
]

def get_horoscope(sign="овен", day="today"):
    """Получение гороскопа через Aztro API"""
    try:
        sign_translation = {
            "овен": "aries", "телец": "taurus", "близнецы": "gemini",
            "рак": "cancer", "лев": "leo", "дева": "virgo",
            "весы": "libra", "скорпион": "scorpio", "стрелец": "sagittarius",
            "козерог": "capricorn", "водолей": "aquarius", "рыбы": "pisces"
        }
        
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
    "Выпей стакан воды - это полезно для здоровья! 💧",
    "Сделай перерыв - твои глаза тоже устают от экрана! 👀",
    "Позвони близким - им будет приятно! 📱",
    "Прогуляйся на свежем воздухе! 🌳",
    "Прочитай хотя бы 10 страниц книги! 📖"
]

compliments = [
    "Ты сегодня выглядишь особенно хорошо! 🌟",
    "У тебя отличное чувство юмора! 😄", 
    "Ты очень умный собеседник! 🧠",
    "С тобой приятно общаться! 💬",
    "Твои вопросы всегда интересные! ❓",
    "Ты делаешь этот мир лучше! 🌍"
]

def get_currency_rates():
    try:
        url = "https://www.cbr-xml-daily.ru/daily_json.js"
        response = requests.get(url)
        data = response.json()
        
        usd = data['Valute']['USD']['Value']
        eur = data['Valute']['EUR']['Value']
        btc_response = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=rub")
        btc_data = btc_response.json()
        btc = btc_data.get('bitcoin', {}).get('rub', 'Не доступен')
        
        return f"💰 Курсы:\n🇺🇸 USD: {usd}₽\n🇪🇺 EUR: {eur}₽\n₿ BTC: {btc}₽"
    except:
        return "Не удалось получить курс валют"

def get_weather(city_name):
    """Получение погоды через Open-Meteo API"""
    try:
        city_translation = {
            "москва": "Moscow", "санкт-петербург": "Saint Petersburg", 
            "питер": "Saint Petersburg", "казань": "Kazan",
            "новосибирск": "Novosibirsk", "екатеринбург": "Yekaterinburg",
            "сочи": "Sochi", "крым": "Simferopol", "краснодар": "Krasnodar",
            "нижний новгород": "Nizhny Novgorod", "ростов": "Rostov-on-Don",
            "самара": "Samara", "омск": "Omsk", "челябинск": "Chelyabinsk",
            "уфа": "Ufa", "волгоград": "Volgograd", "пермь": "Perm",
            "воронеж": "Voronezh", "красноярск": "Krasnoyarsk",
            "оренбург": "Orenburg", "новотроицк": "Novotroitsk", 
            "гай": "Gai", "орск": "Orsk", "бузулук": "Buzuluk",
            "бугуруслан": "Buguruslan", "кувандык": "Kuvandyk",
            "медногорск": "Mednogorsk", "соль-илецк": "Sol-Iletsk",
            "ясный": "Yasny", "абдулино": "Abdulino"
        }
        
        city_lower = city_name.lower().strip()
        english_city = city_translation.get(city_lower, city_name)
        
        # 1. Получаем координаты города
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={english_city}&count=1&language=ru"
        geo_response = requests.get(geo_url, timeout=10)
        geo_data = geo_response.json()
        
        if 'results' in geo_data and geo_data['results']:
            lat = geo_data['results'][0]['latitude']
            lon = geo_data['results'][0]['longitude']
            found_city_name = geo_data['results'][0]['name']
            
            # 2. Получаем погоду
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
            weather_response = requests.get(weather_url, timeout=10)
            weather_data = weather_response.json()
            
            if 'current_weather' in weather_data:
                temp = weather_data['current_weather']['temperature']
                windspeed = weather_data['current_weather']['windspeed']
                weathercode = weather_data['current_weather']['weathercode']
                
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
                
                # Дополнительная информация
                feels_like = temp - 2 if windspeed > 10 else temp  # Простой расчет "ощущается как"
                
                advice = ""
                if temp > 25:
                    advice = " ☀️ Сегодня жарко, пейте больше воды!"
                elif temp < 0:
                    advice = " ❄️ Сегодня морозно, одевайтесь теплее!"
                elif "дождь" in weather_text:
                    advice = " ☔ Не забудьте зонт!"
                
                return f"🌡️ В {found_city_name}:\nТемпература: {temp}°C (ощущается как {feels_like}°C)\nПогода: {weather_text}\nВетер: {windspeed} км/ч{advice}"
            else:
                return "Не удалось получить данные о погоде"
        else:
            return "Город не найден. Попробуйте: Москва, Санкт-Петербург, Оренбург, Орск"
            
    except requests.exceptions.Timeout:
        return "Превышено время ожидания. Попробуйте позже."
    except Exception as e:
        print(f"Ошибка в get_weather: {e}")
        return "Не удалось получить погоду. Попробуйте другой город."

def extract_city_from_command(command):
    """Извлекает название города из команды пользователя"""
    keywords = ["погода", "в", "какая", "скажи", "покажи", "как", "что"]
    
    for keyword in keywords:
        command = command.replace(keyword, "")
    
    return command.strip()

def start_cities_game(user_name=""):
    """Начинает игру в города"""
    global game_state
    game_state['active'] = True
    game_state['used_cities'] = []
    game_state['last_city'] = ''
    game_state['player_name'] = user_name if user_name else "игрок"
    game_state['score'] = {'user': 0, 'bot': 0}
    
    first_city = random.choice(russian_cities)
    game_state['used_cities'].append(first_city.lower())
    game_state['last_city'] = first_city
    
    return f"🏙️ Отлично! Начинаем игру в города!\nЯ начинаю: {first_city}\nТебе на букву '{first_city[-1].upper()}'. Назови город!"

def play_cities_game(user_city):
    """Обрабатывает ход в игре в города"""
    global game_state
    
    user_city_lower = user_city.lower()
    
    # Проверяем что город не использовался
    if user_city_lower in game_state['used_cities']:
        return f"Город {user_city} уже был использован! Попробуй другой."
    
    # Проверяем что город существует в нашем списке
    if user_city not in russian_cities and user_city_lower not in [c.lower() for c in russian_cities]:
        # Ищем похожий город
        similar = [c for c in russian_cities if c.lower().startswith(user_city_lower[0])]
        if similar:
            return f"Я не знаю города {user_city}. Возможно, вы имели в виду {', '.join(similar[:3])}?"
        return f"Я не знаю города {user_city}. Попробуй другой российский город."
    
    # Проверяем что город начинается на нужную букву
    if game_state['last_city']:
        last_letter = game_state['last_city'][-1].lower()
        if last_letter in ['ь', 'ы', 'ъ']:
            last_letter = game_state['last_city'][-2].lower()
        
        if user_city_lower[0] != last_letter:
            return f"Город должен начинаться на букву '{last_letter.upper()}'! Попробуй другой."
    
    # Добавляем город пользователя
    game_state['used_cities'].append(user_city_lower)
    game_state['score']['user'] += 1
    
    # Ищем ответный город
    last_letter_user = user_city[-1].lower()
    if last_letter_user in ['ь', 'ы', 'ъ']:
        last_letter_user = user_city[-2].lower()
    
    available_cities = [c for c in russian_cities 
                       if c.lower().startswith(last_letter_user) 
                       and c.lower() not in game_state['used_cities']]
    
    if available_cities:
        bot_city = random.choice(available_cities)
        game_state['used_cities'].append(bot_city.lower())
        game_state['last_city'] = bot_city
        game_state['score']['bot'] += 1
        
        next_letter = bot_city[-1].upper()
        if next_letter in ['Ь', 'Ы', 'Ъ']:
            next_letter = bot_city[-2].upper()
        
        return f"✅ Отлично! {user_city} - хороший город!\n🤖 Мой ход: {bot_city}\nТебе на букву '{next_letter}'. Назови город!"
    else:
        # Бот не может найти город
        game_state['active'] = False
        score = game_state['score']
        return f"🎉 Поздравляю! Ты выиграл!\nЯ не могу найти город на букву '{last_letter_user.upper()}'.\n🏆 Счет: Ты {score['user']} : {score['bot']} Я"

def end_cities_game():
    """Завершает игру в города"""
    global game_state
    score = game_state['score']
    game_state['active'] = False
    return f"🏁 Игра завершена!\n🏆 Финальный счет: Ты {score['user']} : {score['bot']} Я\nСпасибо за игру! Хочешь сыграть еще?"

def get_joke():
    """Возвращает случайную шутку"""
    jokes = [
        "Почему программисты путают Хэллоуин и Рождество? Потому что Oct 31 == Dec 25! 😄",
        "Как называется песня, которую поёт API? JSON-der-ella! 🎵",
        "Почему Python лучше Java? Потому что в Python нет NullPointerException! 🐍",
        "Что сказал один HTTP другому? Ты опять 404-й? 🌐",
        "Почему Python не нуждается в парковке? Потому что он интерпретируемый! 🚗",
        "Как программист делает кофе? Он debugs его! ☕",
        "Почему JavaScript разработчик пошел в бар? Чтобы найти closure! 🍻"
    ]
    return random.choice(jokes)

def get_fact():
    """Возвращает случайный факт"""
    facts = [
        "Open-Meteo API полностью бесплатный и без ограничений! Используется NASA и ECMWF данными 🛰️",
        "Первый программист была женщина - Ада Лавлейс, дочь поэта Байрона! 👩‍💻",
        "Python был назван в честь комедийного шоу 'Монти Пайтон', а не змеи! 🐍",
        "Самый популярный язык программирования в мире - JavaScript! 🌍",
        "Первая компьютерная мышь была сделана из дерева в 1964 году! 🖱️",
        "Первый компьютерный вирус был создан в 1983 году! 🦠",
        "Самый первый сайт в интернете до сих пор работает! 🌐"
    ]
    return random.choice(facts)

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
        
        # Извлекаем имя пользователя если есть
        user_name = ""
        if 'user' in session:
            user_name = session['user'].get('first_name', '')

        print(f"Получена команда: {user_command}")

        # Проверяем активна ли игра в города
        if game_state['active']:
            # Если игра активна, проверяем команды связанные с игрой
            if any(word in user_command for word in ['стоп', 'закончить', 'хватит', 'выйти']):
                response_text = end_cities_game()
            elif any(word in user_command for word in ['счет', 'очки', 'результат']):
                score = game_state['score']
                response_text = f"🏆 Текущий счет:\n{game_state['player_name']}: {score['user']}\nЯ: {score['bot']}"
            elif any(word in user_command for word in ['помощь', 'правила']):
                response_text = "🏙️ Правила игры в города:\n1. Называй российские города\n2. Город должен начинаться на последнюю букву предыдущего города\n3. Города не должны повторяться\n4. Чтобы закончить игру, скажи 'стоп'"
            else:
                # Пытаемся извлечь название города
                city_keywords = ["город ", "называю ", "это "]
                user_city = user_command
                for keyword in city_keywords:
                    if keyword in user_command:
                        user_city = user_command.split(keyword)[-1].strip()
                        break
                
                # Если это похоже на город (больше 3 букв)
                if len(user_city) > 2:
                    response_text = play_cities_game(user_city.capitalize())
                else:
                    response_text = "Это не похоже на город. Назови российский город или скажи 'стоп' чтобы закончить игру."
            
            response = {
                "version": version,
                "session": session,
                "response": {
                    "text": response_text,
                    "end_session": False
                }
            }
            return jsonify(response)

        # ОСНОВНАЯ ЛОГИКА НАВЫКА (если игра не активна)
        if user_command == '':
            greeting = f"Привет{', ' + user_name if user_name else ''}! 👋"
            response_text = f"{greeting}\nЯ твой умный помощник! Спроси:\n• 'погода в Оренбурге' 🌤️\n• 'курс валют' 💰\n• 'гороскоп тельца' ♈\n• 'сыграем в города' 🏙️\n• 'совет' 💡\n• 'шутка' 😄\n• 'помощь' 📋"
        
        elif any(word in user_command for word in ['привет', 'здравствуй', 'добрый']):
            greeting = f"Привет{', ' + user_name if user_name else ''}! 😊"
            response_text = f"{greeting} Рад тебя видеть! Чем могу помочь?"
        
        elif 'как дела' in user_command or 'как ты' in user_command:
            moods = ["Отлично! Готов помогать! 👍", "Прекрасно! А у тебя? 😊", "Как у хорошего навыка - работаю! ⚡"]
            response_text = random.choice(moods)
        
        elif 'спасибо' in user_command or 'благодарю' in user_command:
            thanks_responses = ["Всегда рад помочь! 🤗", "Пожалуйста! Обращайся еще! 😊", "Рад был помочь! 💪"]
            response_text = random.choice(thanks_responses)
        
        elif 'комплимент' in user_command or 'похвали' in user_command:
            response_text = random.choice(compliments)
        
        elif 'помощь' in user_command or 'что ты умеешь' in user_command:
            response_text = """📋 Я умею многое:

🌤️ ПОГОДА: в любом городе (Оренбург, Орск, Москва, СПб)
💰 КУРСЫ: доллар, евро, биткоин
♈ ГОРОСКОП: на сегодня для любого знака
🏙️ ИГРА: в города (скажи "сыграем в города")
💡 СОВЕТЫ: полезные советы на день
😄 ШУТКИ: программистские шутки
📚 ФАКТЫ: интересные факты
⏰ ВРЕМЯ: текущее время

Просто скажи что хочешь! 🚀"""
        
        elif 'время' in user_command or 'который час' in user_command:
            current_time = datetime.now().strftime("%H:%M")
            time_of_day = ""
            hour = int(datetime.now().strftime("%H"))
            if 5 <= hour < 12:
                time_of_day = "Доброе утро! ☀️"
            elif 12 <= hour < 17:
                time_of_day = "Добрый день! 🌞"
            elif 17 <= hour < 23:
                time_of_day = "Добрый вечер! 🌙"
            else:
                time_of_day = "Доброй ночи! 🌌"
            
            response_text = f"{time_of_day}\nСейчас {current_time} ⏰"
        
        # ИГРА В ГОРОДА
        elif any(word in user_command for word in ['города', 'сыграем', 'игра', 'поиграем']):
            response_text = start_cities_game(user_name)
        
        # ГОРОСКОП
        elif 'гороскоп' in user_command or 'знак зодиака' in user_command:
            sign = extract_zodiac_sign(user_command)
            if sign:
                response_text = get_horoscope(sign)
            else:
                response_text = "Для какого знака зодиака гороскоп? Например: 'гороскоп для тельца' или 'гороскоп стрельца'"
        
        # КУРСЫ ВАЛЮТ
        elif 'курс' in user_command or 'валют' in user_command or 'доллар' in user_command or 'евро' in user_command:
            response_text = get_currency_rates()

        elif 'совет' in user_command or 'посоветуй' in user_command:
            response_text = random.choice(advices)
            
        # ПОГОДА
        elif 'погода' in user_command:
            orenburg_cities = {
                'оренбург': 'оренбург', 'новотроицк': 'новотроицк', 'гай': 'гай',
                'орск': 'орск', 'бузулук': 'бузулук', 'бугуруслан': 'бугуруслан',
                'кувандык': 'кувандык', 'медногорск': 'медногорск', 'соль-илецк': 'соль-илецк',
                'ясный': 'ясный', 'абдулино': 'абдулино'
            }
            
            found_city = None
            for city_keyword, city_name in orenburg_cities.items():
                if city_keyword in user_command:
                    found_city = city_name
                    break
            
            if found_city:
                response_text = get_weather(found_city)
            elif any(city in user_command for city in ['москв', 'питер', 'санкт-петербург', 'казан', 'новосибирск', 'екатеринбург', 'сочи']):
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
                city = extract_city_from_command(user_command)
                if city:
                    response_text = get_weather(city)
                else:
                    response_text = "В каком городе показать погоду? Например: 'погода в Оренбурге' или 'погода в Орске'"
        
        # ШУТКИ
        elif 'шутк' in user_command or 'пошути' in user_command:
            response_text = get_joke()
        
        # ФАКТЫ
        elif 'факт' in user_command or 'интересно' in user_command:
            response_text = get_fact()

        # ПРОЩАНИЕ
        elif any(word in user_command for word in ['пока', 'до свидания', 'спокойной ночи']):
            farewells = [
                f"Пока{', ' + user_name if user_name else ''}! Возвращайся! 👋",
                "До свидания! Буду ждать тебя! 😊",
                "Пока! Приятно было пообщаться! 🤗"
            ]
            response_text = random.choice(farewells)

        else:
            # Умный ответ на непонятную команду
            if random.random() > 0.5:
                response_text = f"Извини, не совсем понял '{user_command}'. Скажи 'помощь' чтобы узнать что я умею. 🤔"
            else:
                response_text = f"Прости, я еще учусь понимать такие фразы как '{user_command}'. Попробуй сказать 'помощь' для списка команд. 📚"

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
    return """🚀 Умный навык для Алисы с улучшенным диалогом!

✨ Возможности:
• 🌤️ Подробная погода с ощущениями
• 💰 Курсы валют (USD, EUR, BTC)
• ♈ Гороскопы на сегодня
• 🏙️ Игра в города России
• 💡 Полезные советы
• 😄 Шутки и комплименты
• 📚 Интересные факты

🏙️ Поддерживает города Оренбургской области!
"""

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
