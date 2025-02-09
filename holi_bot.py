import asyncio
import requests
import os
import threading
import http.server
import socketserver
from http.server import BaseHTTPRequestHandler, HTTPServer
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import json

TOKEN = "7809691512:AAHmFFAGkXu34oW3IujqoTcTmiwzs66Hwe0"
SERVER_URL = "https://server-for-holi.onrender.com/save_user"
MENU_URL = "https://t.me/holiarus_bot/Holiarus?start=menu"

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

user_data = {}  # Хранение данных пользователей

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/get_user/"):
            user_id = self.path.split("/")[-1]
            if user_id in user_data:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(user_data[user_id]).encode())
            else:
                self.send_response(404)
                self.end_headers()


def run_server():
    port = 8080
    server = HTTPServer(("", port), RequestHandler)
    print(f"Сервер запущен на порту {port}")
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Фейковый сервер запущен на порту {port}")
        httpd.serve_forever()

threading.Thread(target=keep_alive, daemon=True).start()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    user_data[user_id] = {"name": user_name, "crystals": 0, "keys": 0}

    try:
        requests.post(SERVER_URL, json={"id": user_id, "name": user_name})
    except requests.exceptions.RequestException as e:
        print(f"Ошибка отправки данных на сервер: {e}")

    builder = InlineKeyboardBuilder()
    builder.button(text="Перейти на канал", url="https://t.me/holiarus")
    builder.button(text="Играть в 1 клик🐵", url=f"{MENU_URL}?userId={user_id}")
    builder.adjust(1)

    await message.answer(
        f'Привет, {user_name}! Добро пожаловать в Holiarus 🐵.\n\n'
        'Теперь ты — участник захватывающего прыжкового приключения! Прыгай по платформам, преодолевай '
        'препятствия и осваивай новые навыки. Игра находится в активной разработке, и мы оценим твои успехи '
        'в будущих обновлениях.\n\n'
        'Зови друзей — вместе вы сможете добиться ещё больших высот!\n\n',
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.message(F.text == '/help')
async def help_cmd(message: types.Message):
    await message.answer('Игра на стадии разработки, возможны сбои и изменения в геймплее. Благодарим за понимание! 🫠')

@dp.message(F.text)
async def unknown_command(message: types.Message):
    await message.answer('Вы ввели неизвестную команду')

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')
