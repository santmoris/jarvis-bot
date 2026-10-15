import os
import requests
import time

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """Ты — Джарвис, персональный ИИ-помощник Александра.
Ниша: психология и кибербезопасность для детей 5-18 лет и родителей.
ПРАВИЛА:
1. Обращение: Саша, Александр, друг, бро.
2. Саша не технарь: объясняй всё простыми словами, с бытовыми аналогиями, пошагово.
3. Стиль: дружеский, структурированный. Сначала суть (резюме в 3 строки), потом детали.
4. В конце ответа всегда добавляй: "[Task Observer]: В следующий раз предложу вариант на 10% эффективнее."
"""

def get_ai_response(user_text):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "qwen/qwen-2.5-72b-instruct",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text}
        ]
    }
    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        return "Извини, Саша, не смог получить ответ."
    except Exception as e:
        return f"Ошибка: {e}"

def main():
    last_update_id = 0
    print("Джарвис запущен и слушает команды в Telegram...")
    
    while True:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?offset={last_update_id + 1}&timeout=30"
        try:
            response = requests.get(url).json()
            if response.get("ok") and response.get("result"):
                for update in response["result"]:
                    last_update_id = update["update_id"]
                    if "message" in update and "text" in update["message"]:
                        chat_id = update["message"]["chat"]["id"]
                        text = update["message"]["text"]
                        print(f"Получил: {text}")
                        ai_response = get_ai_response(text)
                        send_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
                        for i in range(0, len(ai_response), 4000):
                            chunk = ai_response[i:i+4000]
                            requests.post(send_url, json={"chat_id": chat_id, "text": chunk})
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()
