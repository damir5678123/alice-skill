from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json

        # Проверяем, что запрос от Алисы
        if not data:
            return jsonify({
                "response": {
                    "text": "Пустой запрос",
                    "end_session": False
                }
            })

        # Извлекаем команду пользователя
        user_command = data['request'].get('original_utterance', '').lower()
        session = data['session']
        version = data['version']

        # Логика навыка
        if user_command == '':
            response_text = "Привет! Я ваш первый навык для Алисы. Скажите 'помощь' чтобы узнать что я умею!"
        elif 'привет' in user_command:
            response_text = "Приветствую! Рад вас видеть!"
        elif 'помощь' in user_command:
            response_text = "Я учебный навык. Попробуйте сказать: привет, время, как дела?"
        elif 'время' in user_command:
            from datetime import datetime
            current_time = datetime.now().strftime("%H:%M")
            response_text = f"Сейчас {current_time}"
        elif 'как дела' in user_command:
            response_text = "У меня всё отлично! А у вас?"
        else:
            response_text = f"Вы сказали: '{user_command}'. Я еще учусь!"

        # Формируем ответ для Алисы
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
    return "Навык для Алисы работает!"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)