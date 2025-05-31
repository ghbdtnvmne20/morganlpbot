import asyncio
import time
import os
import httpx
from PIL import Image, ImageDraw, ImageFont, ImageOps
import textwrap
from io import BytesIO
from datetime import datetime
import json
import asyncio
from telethon.tl.functions.messages import ReadHistoryRequest
import random
from collections import deque
import re
import uuid
from telethon.tl.types import User, ChannelParticipantCreator, ChannelParticipantAdmin
from telethon import TelegramClient, events, Button
from telethon.errors import UsernameInvalidError, UserNotMutualContactError, FloodWaitError, PeerFloodError, UserPrivacyRestrictedError, ChatAdminRequiredError, MessageIdInvalidError, MessageNotModifiedError
from telethon.tl.functions.channels import InviteToChannelRequest
from telethon.tl.types import ChannelParticipantsAdmins
import replicate
from telethon.tl.types import ChannelParticipantsSearch
import aiohttp
from telethon.tl.types import Channel, Chat
from dataclasses import dataclass, field
from typing import Dict
from telethon.tl.types import ChannelParticipantsAdmins, ChannelParticipantCreator, ChannelParticipantAdmin, User
from telethon.errors.rpcerrorlist import ChatAdminRequiredError
import requests


# --- ВАЖНО: НАСТРОЙТЕ ВАШИ АККАУНТЫ НИЖЕ ---
ACCOUNTS = [
    {
        'api_id': 29564997,  # Замените на API ID вашего первого аккаунта
        'api_hash': '435acfcb83c05255fdfcba6fffb3e11c',  # Замените на API Hash вашего первого аккаунта
        'session_name': 'my_userbot_session' # Уникальное имя сессии для первого аккаунта
    }
]
MISTRAL_API_KEY = "zuqIvHaKX3Lg3oWM6UF6uFHVT047g3t5"
REPLICATE_API_TOKEN = "r8_CuZy4cz7qVfvTe3qh2ZSu42F7UsFgNM4GvkcD"
NICKNAMES_FILE = 'nicknames.json'
os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
last_message_times = {}
COMMAND_COOLDOWN = 5
AUTOREPLY_FILE = 'autoreplies.json'
MY_USER_ID = 812717808 # Изначально None, будет установлено при старте

clients = []
for acc in ACCOUNTS:
    client = TelegramClient(acc['session_name'], acc['api_id'], acc['api_hash'])
    clients.append(client)
    client = clients[0]  # Сделаем client глобальной переменной

RPS_RULES = {
    'камень': 'ножницы',   # Камень побеждает ножницы
    'ножницы': 'бумага',   # Ножницы побеждают бумагу
    'бумага': 'камень'     # Бумага побеждает камень
}

RPS_CHOICES = {
    'камень': '🪨',
    'ножницы': '✂️',
    'бумага': '📋'
}
BACKGROUND_IMAGES = {
    1: r'C:/Users/Кобра/Downloads/фон1.jpg',   # Пример: Первый фон
    2: r'C:/Users/Кобра/Downloads/фон2.jpg',   # Пример: Второй фон
    3: r'C:/Users/Кобра/Downloads/фон3.jpg',  # Пример: Третий фон
    # Добавляйте сюда столько фонов, сколько хотите
}
# Фон по умолчанию, если номер не указан или неверен
DEFAULT_BACKGROUND_PATH = r'C:/Users/Кобра/Downloads/фывп.jpg' # Ваш текущий фон по умолчанию
# Вы можете добавить больше аккаунтов, если хотите:
# {
#     'api_id': ВАШ_API_ID_2,
#     'api_hash': 'ВАШ_API_HASH_2',
#     'session_name': 'my_second_userbot_session'
# },
# --------------------------------------------------
HELP_TEXT_PAGE_1 = (
    "📚 **Доступные команды юзербота (Страница 1/2):**\n\n"
    "✨ .помощь - Показать список всех команд.\n"
    "🤖 .botinfo - Показать информацию о юзерботе и его создателе.\n"
    "ℹ️ .инфо [юзернейм/ID] / [ответ на сообщение] - Получить информацию о пользователе.\n"
    "🏓 .пинг - Проверить время отклика юзербота.\n"
    "❤️ .love - Отправить анимированное сердце.\n"
    "❤️ .цветноесердце - Отправить сердце, которое меняет цвета в течении нескольких секунд.\n"
    "💬 .цит либо .цит [номер фона от 1 до 3] (ответом на сообщение) - Создать красивую цитату из сообщения.\n"
    "🐱 .котики - Отправить случайную фотографию котика.\n"
    "🐶 .собачки - Отправить случайную фотографию собачки.\n"
    "➕ .добавить [юзернейм/ID] - Добавить пользователя в чат (требуются права администратора).\n"
    "📩 .игнор - Подсчитать количество непрочитанных чатов.\n"
    "🔥 .огонь - Показать анимацию огня.\n"
    "🔢 .калькулятор [выражение] - Вычислить математическое выражение.\n"
    "☀️ .погода [город] - Получить текущую погоду в городе.\n"
    "💬 .чатинфо - Получить информацию о текущем чате и ссылку на него.\n"
    "🆕 .ai - Искуственный интелект. (НОВИНКА)\n"
    "📚 .wiki [запрос] - Найти информацию в Wikipedia.\n\n"

    "🎲 **Игра 'Слова (на последнюю букву)':**\n"
    "  .слподбор - Начать подбор игроков.\n"
    "  .слвойти - Присоединиться к игре.\n"
    "  .слстарт - Начать игру (только организатор).\n"
    "  .слстоп - Остановить игру (только организатор).\n"
    "  .слвыйти - Выйти из игры.\n"
    "  .слвернутся - Вернутся в игру (когда играет более 2х человек).\n\n\n"
    " 👨‍👩‍👧‍👦 **РП Команды:**\n"
    " .поцеловать [юзер]\n"
    " .укусить [юзер]\n"
    " .обнять [юзер]\n"
    " .шлепнуть[юзер]\n"
    " .ударить [юзер]\n"
    " .погладить [юзер]\n\n"

    "ℹ️ Используйте команды с точкой в начале.\n"
    "ℹ️ Переключится на 2 страницу - .помощь2\n\n"
    "👑 [MorganLP](t.me/sedativine)"
)

HELP_TEXT_PAGE_2 = (
    "📚 **Дополнительные команды юзербота (Страница 2/2):**\n\n"
    "🎲 .кубик - Бросить игральный кубик и получить случайное число от 1 до 6.\n"
    "🗒️ .цитатадня - Получить случайную цитату дня на русском языке.\n"
    "🔮 .вероятность [вопрос] - Рассчитать случайную вероятность для заданного вопроса.\n"
    "📌 .закрепи (в ответ на сообщение) - Закрепить сообщение в текущем чате (бот должен быть администратором с правами на закрепление сообщений).\n"
    "💘 .сердце2  - Похожая штука на .love\n"
    "🌈 .разноцветноесердце  - Генерирует полное сердце (как в .love), но разноцветное\n"
    "📨 .спам [сообщение] [количество]  - Спамит сообщениями.\n"
    "🌍 .ник [желаемый ник]  - Установить желаемый ник в беседе.\n"
    "🤖 .автоответ [тригер] [текст автоответа] - Установить автоответчик по тригеру.\n"
    "🌐 .google [запрос] - Искать что угодно в Google.\n"
    "🪨 .цуефа [камень\ножницы\бумага] - Сыграть в цуефа с ботом.\n"
    "📣 .zov|.вызов [сообщение] - Вызвать всех участников чата с определенным сообщением.\n"
    "\n\n"
    "👑 [MorganLP](t.me/sedativine)"
)

PROTECTED_USER_IDS = [812717808]
IGNORED_USERS_FILE = 'ignored_users.txt'
ignored_user_ids = set() # Используем set для быстрого поиска и уникальных ID


RP_COMMAND_TEMPLATES = {
    "поцеловать": [
        "{sender} нежно целует {target} в щечку.",
        "{sender} дарит страстный поцелуй {target}.",
        "{sender} целует {target} в лобик, желая доброго дня.",
        "{sender} легонько чмокает {target} в носик.",
        "{sender} воздушно целует {target}."
    ],
    "обнять": [
        "{sender} крепко обнимает {target}.",
        "{sender} заключает {target} в теплые объятия.",
        "{sender} нежно обнимает {target} со спины.",
        "{sender} обнимает {target}, чтобы утешить.",
        "{sender} обнимает {target} с распростертыми объятиями."
    ],
    "ударить": [
        "{sender} несильно ударяет {target} по плечу.",
        "{sender} отвешивает {target} шутливый подзатыльник.",
        "{sender} в шутку бьет {target} кулаком.",
        "{sender} грозно смотрит на {target} и замахивается.",
        "{sender} внезапно ударяет {target} с криком 'Банзай!'."
    ],
    "погладить": [
        "{sender} нежно гладит {target} по голове.",
        "{sender} ласково поглаживает {target} по руке.",
        "{sender} гладит {target} по спинке, успокаивая.",
        "{sender} проводит рукой по волосам {target}.",
        "{sender} поглаживает {target} по щеке."
    ],
    "шлепнуть": [
        "{sender} шутливо шлепает {target}.",
        "{sender} игриво шлепает {target} по попке."
    ],
     "укусить": [
        "{sender} игриво кусает {target} за ушко.",
        "{sender} делает вид, что кусает {target}."
    ],
     "подаритьайфон": [
        "{sender} с обьятиями подарил {target} айфон.",
    ]
}

RP_ACTION_GIFS = {
    'обнять': [
        "https://media1.tenor.com/m/SKTwrr1xu2gAAAAd/the-apothecary-diaries-kusuriya-no-hitorigoto.gif",
        "https://media1.tenor.com/m/cBcV5uqNYvYAAAAd/fruits-basket-fruits.gif",
        "https://media1.tenor.com/m/nwxXREHNog0AAAAd/hug-anime.gif",
        "https://media1.tenor.com/m/7oCaSR-q1kkAAAAd/alice-vt.gif"
    ],
    'поцеловать': [
        "https://media1.tenor.com/m/SKTwrr1xu2gAAAAd/the-apothecary-diaries-kusuriya-no-hitorigoto.gif",
        "https://media1.tenor.com/m/hK8IUmweJWAAAAAd/kiss-me-%D0%BB%D1%8E%D0%B1%D0%BB%D1%8E.gif"
    ],
    'ударить': [
        "https://media1.tenor.com/m/UyqTkkAxpioAAAAd/my-oni-girl-myonigirl.gif"
    ],
    'погладить': [
        "https://media.tenor.com/7cd6UYpGetIAAAAi/floppa-pet.gif"
    ],
    # Добавьте больше RP-действий по аналогии:
    # 'действие': [
    #     "url_гифки_1",
    #     "url_гифки_2"
    # ],
    'шлепнуть': [
        "https://media1.tenor.com/m/XbJu4_F243UAAAAC/mother-secretary.gif"
    ],
    'укусить': [
        "https://media1.tenor.com/m/L8GrZ1X6ThsAAAAC/bite.gif"
    ],
    'подаритьайфон': [
        "https://media1.tenor.com/m/oxkQGOU-rSwAAAAd/gift-present.gif"
    ]
}


# Глобальная переменная для кэширования полных сообщений для кнопок
full_unread_messages_cache = {}

# Глобальные переменные для игры "Слова"
WORDS_GAME_FILE = 'words_games.json' # Файл для сохранения данных игры
active_words_games = {} # This should be loaded from a persistent storage
active_duels: Dict[str, dict] = {}  # ключ — chat_id, значение — словарь с боем
autoreplies = {}
if os.path.exists(AUTOREPLY_FILE):
    with open(AUTOREPLY_FILE, 'r', encoding='utf-8') as f:
        autoreplies = json.load(f)
    print(f"Загружено {len(autoreplies)} автоответов.")

# --- Функция для сохранения автоответов ---
def save_autoreplies():
    with open(AUTOREPLY_FILE, 'w', encoding='utf-8') as f:
        json.dump(autoreplies, f, ensure_ascii=False, indent=4)
    print("Автоответы сохранены.")


# --- ФУНКЦИИ ДЛЯ СОХРАНЕНИЯ/ЗАГРУЗКИ СОСТОЯНИЯ ИГРЫ ---
def load_words_games():
    """Загружает состояние активных игр из JSON-файла."""
    global active_words_games
    print(f"DEBUG: Попытка загрузить состояние игр из файла: {WORDS_GAME_FILE} (полный путь: {os.path.abspath(WORDS_GAME_FILE)})")
    
    if os.path.exists(WORDS_GAME_FILE):
        try:
            with open(WORDS_GAME_FILE, 'r', encoding='utf-8') as f:
                active_words_games = json.load(f)
            print(f"DEBUG: Состояние игр успешно загружено из {WORDS_GAME_FILE}. Загружено {len(active_words_games)} активных игр.")
        except json.JSONDecodeError as e:
            print(f"ERROR: Ошибка при чтении JSON из {WORDS_GAME_FILE}: {e}. Файл поврежден или пуст. Инициализация пустого состояния.")
            active_words_games = {}
        except Exception as e:
            print(f"ERROR: Неизвестная ошибка при загрузке {WORDS_GAME_FILE}: {e}. Инициализация пустого состояния.")
            active_words_games = {}
    else:
        active_words_games = {}
        print(f"DEBUG: Файл {WORDS_GAME_FILE} не найден по указанному пути. Инициализация пустого состояния игр. Новый файл будет создан при первом сохранении.")

def save_words_games(data):
    """Сохраняет текущее состояние активных игр в JSON-файл."""
    print(f"DEBUG: Попытка сохранить состояние игр в файл: {WORDS_GAME_FILE} (полный путь: {os.path.abspath(WORDS_GAME_FILE)})")
    try:
        with open(WORDS_GAME_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"DEBUG: Состояние игр успешно сохранено в {WORDS_GAME_FILE}. Сохранено {len(data)} активных игр.")
    except Exception as e:
        print(f"ERROR: Ошибка при сохранении состояния игр в {WORDS_GAME_FILE}: {e}")

def load_ignored_users():
    """Загружает ID игнорируемых пользователей из файла."""
    if os.path.exists(IGNORED_USERS_FILE):
        with open(IGNORED_USERS_FILE, 'r') as f:
            for line in f:
                try:
                    ignored_user_ids.add(int(line.strip()))
                except ValueError:
                    continue # Пропускаем некорректные строки
    print(f"Загружено игнорируемых пользователей: {ignored_user_ids}")

def save_ignored_users():
    """Сохраняет ID игнорируемых пользователей в файл."""
    with open(IGNORED_USERS_FILE, 'w') as f:
        for user_id in ignored_user_ids:
            f.write(f"{user_id}\n")
    print(f"Сохранено игнорируемых пользователей: {ignored_user_ids}")

load_ignored_users() # <-- Добавьте эту строку
active_words_games = load_words_games()

@dataclass
class PlayerState:
    id: int
    name: str
    hp: int = 100
    energy: int = 0
    defending: bool = False

@dataclass
class DuelGame:
    player1: PlayerState
    player2: PlayerState
    current_turn: int  # ID игрока, чей ход
    message_id: int = 0
    chat_id: int = 0

    def get_opponent(self, player_id):
        return self.player1 if self.player2.id == player_id else self.player2

    def get_player(self, player_id):
        return self.player1 if self.player1.id == player_id else self.player2

    def make_move(self, actor_id, action):
        actor = self.get_player(actor_id)
        target = self.get_opponent(actor_id)

        if action == "attack":
            damage = 10
            if target.defending:
                damage //= 2
            target.hp -= damage
            actor.energy += 1
            target.defending = False
            return f"🗡 {actor.name} атакует! Наносит {damage} урона."

        elif action == "defend":
            actor.defending = True
            return f"🛡 {actor.name} встал в защиту!"

        elif action == "super":
            if actor.energy >= 3:
                damage = 25
                if target.defending:
                    damage //= 2
                target.hp -= damage
                actor.energy = 0
                target.defending = False
                return f"💥 {actor.name} использует СУПЕР-УДАР! Наносит {damage} урона!"
            else:
                return "⚠ Недостаточно энергии для супер-удара."

        elif action == "giveup":
            actor.hp = 0
            return f"🏳 {actor.name} сдается!"

        return "⚠ Неизвестное действие."

    def is_over(self):
        return self.player1.hp <= 0 or self.player2.hp <= 0

    def get_winner(self):
        if self.player1.hp > 0:
            return self.player1
        if self.player2.hp > 0:
            return self.player2
        return None


def render_duel(game: DuelGame):
    p1 = game.player1
    p2 = game.player2
    text = (
        f"🧍‍♂️ {p1.name} [HP: {p1.hp}, 🔋 {p1.energy}]\n"
        f"🧍‍♂️ {p2.name} [HP: {p2.hp}, 🔋 {p2.energy}]\n\n"
        f"🎮 Ход: **{game.get_player(game.current_turn).name}**"
    )
    return text


def register_rp_commands(client_obj):
    for cmd_name in RP_COMMAND_TEMPLATES.keys():
        pattern = rf'^\.{cmd_name}(?:\s|$)'
        client_obj.on(events.NewMessage(pattern=pattern, outgoing=True))(
            lambda event, action_templates=RP_COMMAND_TEMPLATES: rp_command_handler(event, client_obj, action_templates)
        )
def load_nicknames():
    if os.path.exists(NICKNAMES_FILE):
        with open(NICKNAMES_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_nicknames(nicknames_data):
    with open(NICKNAMES_FILE, 'w', encoding='utf-8') as f:
        json.dump(nicknames_data, f, ensure_ascii=False, indent=4)

def get_full_name_and_mention(user_data):
    user_id = user_data['id']
    
    # --- ДОБАВЛЕНО ДЛЯ ОТЛАДКИ ---
    print(f"DEBUG: Processing user_data for mention: {user_data}")
    # --- КОНЕЦ ОТЛАДКИ ---

    if user_data.get('username'):
        username = user_data['username']
        # Возвращаем только юзернейм и ID
        return f"@{username} (ID: `{user_id}`)"
    else:
        # Если юзернейма нет, возвращаем упоминание по ID и ID
        # Это будет выглядеть как "Имя Фамилия (ID: `12345`)", но кликабельным будет только ID
        # Для случаев, где юзернейм отсутствует, Telegram автоматически покажет имя.
        return f"[Пользователь](tg://user?id={user_id}) (ID: `{user_id}`)"

def format_player_mention(player_data):
    player_id = player_data['id']
    # player_data['name'] в вашем случае уже может содержать @username, если он был установлен
    # при присоединении игрока. Мы будем использовать его, но убедимся, что формат соответствует
    # только юзернейму и ID.
    
    # Пытаемся извлечь юзернейм из player_data['name'], если он там есть
    # Например, если player_name = "Имя Фамилия (@username)"
    username_match = re.search(r'@(\w+)', player_data['name'])

    if username_match:
        username = username_match.group(1)
        return f"@{username} (ID: `{player_id}`)"
    else:
        # Если юзернейм не найден или player_data['name'] не содержит его,
        # используем стандартное упоминание по ID
        # Можно оставить player_data['name'] для отображения, но упор на ID
        # Или же можно просто написать "Пользователь"
        return f"[{player_data['name']}](tg://user?id={player_id}) (ID: `{player_id}`)"

chat_nicknames = load_nicknames()
online_status_enabled = {}

# Словарь для хранения задач keep_online, чтобы их можно было отменить
online_tasks = {}
load_words_games()

# Функция-фильтр для разрешения сообщений от ботов
def allow_bots_and_users(event):
    """
    Возвращает True, если сообщение должно быть обработано,
    включая сообщения от ботов. Переопределяет стандартное поведение юзербота,
    игнорирующее сообщения от других ботов.
    """
    # Убедимся, что отправитель существует и это не канал/чат сам по себе
    if event.sender is None:
        return False
    # Если отправитель - это пользователь или бот, разрешаем обработку
    # (event.sender.bot будет True для ботов, False для обычных пользователей)
    return True # Разрешаем любые сообщения, у которых есть отправитель

# Загружаем игры при старте скрипта
load_words_games()

async def info_handler(event, client):
    """
    Обрабатывает команду .инфо для получения информации о пользователе.
    Включает специальную защиту для номера телефона для определенных ID.
    """
    target_user = None
    input_arg = event.pattern_match.group(1)

    if input_arg:
        try:
            try:
                user_id_int = int(input_arg)
                target_user = await client.get_entity(user_id_int)
            except ValueError:
                target_user = await client.get_entity(input_arg)
        except UsernameInvalidError:
            await event.edit("Ошибка: Неверный юзернейм или ID пользователя.")
            return
        except UserNotMutualContactError:
            await event.edit("Ошибка: Не могу получить информацию о данном пользователе (возможно, приватный аккаунт).")
            return
        except Exception as e:
            await event.edit(f"Ошибка при поиске пользователя: {e}")
            return
    elif event.is_reply:
        try:
            replied_message = await event.get_reply_message()
            if replied_message and replied_message.sender:
                target_user = await replied_message.get_sender()
            else:
                await event.edit("Не удалось получить информацию о сообщении, на которое был сделан реплай.")
                return
        except Exception as e:
            await event.edit(f"Произошла ошибка при получении реплая: {e}")
            return
    else:
        target_user = await event.get_sender()

    if not target_user:
        await event.edit("Не удалось получить информацию о пользователе.")
        return

    user_id = target_user.id
    username = f"@{target_user.username}" if target_user.username else "Нет юзернейма"
    first_name = target_user.first_name if target_user.first_name else ""
    last_name = target_user.last_name if target_user.last_name else ""
    full_name = f"{first_name} {last_name}".strip() if first_name or last_name else "Нет имени"

    has_avatar = False
    try:
        photos = await client.get_profile_photos(target_user, limit=1)
        if photos:
            has_avatar = True
    except Exception:
        pass

    is_premium = "✅" if getattr(target_user, 'premium', False) else "❎"
    lang_code = getattr(target_user, 'lang_code', 'Неизвестно')

    # --- НОВАЯ ЛОГИКА ДЛЯ СКРЫТИЯ НОМЕРА ТЕЛЕФОНА ---
    if target_user.id in PROTECTED_USER_IDS:
        phone_info = "[!] Скрыт разработчиком [!]"
    else:
        phone_number = getattr(target_user, 'phone', None)
        if phone_number:
            phone_info = f"`+{phone_number}`"
        else:
            phone_info = "Скрыт"
    # --- КОНЕЦ НОВОЙ ЛОГИКИ ---

    response = (
        f"ℹ️ **Информация о пользователе:**\n"
        f"👀 ID: `{user_id}`\n"
        f"🧾 Имя: `{full_name}`\n"
        f"💾 Юзернейм: {username}\n"
        f"📞 Телефон: {phone_info}\n" # Теперь здесь используется phone_info
        f"🤳 Аватарка: {'Есть' if has_avatar else 'Нет'}\n"
        f"💎 Telegram Premium: `{is_premium}`\n"
        f"🗺️ Язык: `{lang_code}`"
    )

    await event.edit(response)

async def ping_handler(event, client):
    """
    Обрабатывает команду .пинг для проверки отклика бота.
    """
    start_time = time.time()
    message = await event.edit("🏓 Pong!")
    end_time = time.time()
    ping_time = (end_time - start_time) * 1000
    await message.edit(f"🏓 Pong!\n🕧 Время отклика: {ping_time:.2f} мс\n\n🤖 [MorganLP](t.me/sedativine)")

async def love_handler(event, client):
    """
    Обрабатывает команду .love для отображения анимированного сердца.
    """
    background_char = '❤️'
    heart_char = '🤍'

    heart_template = [
    "  🤍🤍   🤍🤍  ",
    " 🤍🤍🤍🤍 🤍🤍🤍🤍 ",
    "🤍🤍🤍🤍🤍🤍🤍🤍🤍🤍🤍",
    "🤍🤍🤍🤍🤍🤍🤍🤍🤍🤍🤍",
    " 🤍🤍🤍🤍🤍🤍🤍🤍🤍 ",
    "  🤍🤍🤍🤍🤍🤍🤍 ",
    "   🤍🤍🤍🤍🤍  ",
    "    🤍🤍🤍   ",
    "     🤍    ",
]
    
    square_height = len(heart_template)
    max_template_width = max(len(row) for row in heart_template)
    square_width = max_template_width

    grid = [[background_char for _ in range(square_width)] for _ in range(square_height)]

    def render(g):
        return "\n".join("".join(row) for row in g)

    msg = await event.respond(render(grid))

    coords = []
    for r in range(len(heart_template)):
        for c in range(len(heart_template[r])):
            if heart_template[r][c] == heart_char:
                coords.append((r, c))

    batch_size = 10
    for i in range(0, len(coords), batch_size):
        batch = coords[i:i + batch_size]
        for r, c in batch:
            if 0 <= r < square_height and 0 <= c < square_width:
                grid[r][c] = heart_char
        try:
            await msg.edit(render(grid))
        except FloodWaitError as e:
            print(f"Flood wait {e.seconds} секунд")
            await asyncio.sleep(e.seconds)
        await asyncio.sleep(0.5)

    await asyncio.sleep(0.7)
    await msg.edit(render(grid) + "\n\nВаше сердечко! ✅")



import os
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageOps
from datetime import datetime
from telethon import events
import tempfile # Импортируем модуль для временных файлов

# --- НАСТРОЙКА ФОНОВЫХ ИЗОБРАЖЕНИЙ ---
# Создайте словарь, где ключ - это номер фона, а значение - полный путь к файлу изображения.
# ОБЯЗАТЕЛЬНО ЗАМЕНИТЕ ЭТИ ПУТИ НА РЕАЛЬНЫЕ ПУТИ К ВАШИМ ИЗОБРАЖЕНИЯМ


async def quote_handler(event, client):
    """
    Обрабатывает команду .цит [номер_фона] для создания цитаты из отвеченного сообщения.
    Включает фоновое изображение, аватарку, имя пользователя и время.
    """
    if not event.is_reply:
        await event.edit("Используйте `.цит [номер_фона]` в ответ на сообщение, чтобы создать цитату.")
        return

    # --- ИЗМЕНЕНИЕ ЗДЕСЬ: Парсим аргумент команды вручную ---
    # Определяем паттерн для команды .цит [аргумент]
    # Используем re.match для сопоставления с началом строки
    import re
    command_pattern = re.compile(r'^\.(?:цит)\s*(\S*)$') # Обновленный паттерн
    match = command_pattern.match(event.text)

    background_arg = None
    if match:
        # match.group(1) будет содержать все, что идет после ".цит " (например, "2" или "" если просто ".цит")
        potential_arg = match.group(1)
        if potential_arg: # Проверяем, что аргумент не пустая строка
            background_arg = potential_arg
    # --- КОНЕЦ ИЗМЕНЕНИЯ ---

    selected_background_path = DEFAULT_BACKGROUND_PATH
    feedback_message = "Генерирую цитату..."

    if background_arg:
        try:
            background_number = int(background_arg)
            if background_number in BACKGROUND_IMAGES:
                selected_background_path = BACKGROUND_IMAGES[background_number]
                feedback_message = f"Генерирую цитату с фоном №{background_number}..."
            else:
                available_numbers = ", ".join(map(str, sorted(BACKGROUND_IMAGES.keys())))
                await event.edit(
                    f"Неверный номер фона: `{background_number}`. Доступные фоны: {available_numbers}."
                    f"\nИспользую фон по умолчанию."
                )
                await asyncio.sleep(3) # Даем время пользователю прочитать сообщение
        except ValueError:
            available_numbers = ", ".join(map(str, sorted(BACKGROUND_IMAGES.keys())))
            await event.edit(
                f"Неверный формат номера фона: `{background_arg}`. Используйте число."
                f"\nДоступные фоны: {available_numbers}."
                f"\nИспользую фон по умолчанию."
            )
            await asyncio.sleep(3) # Даем время пользователю прочитать сообщение
    
    await event.edit(feedback_message)

    try:
        replied_message = await event.get_reply_message()
        if not replied_message or not replied_message.text:
            await event.edit("Не удалось получить текст из отвеченного сообщения.")
            return

        quote_text = replied_message.text
        
        sender_display_name = None
        if replied_message.sender:
            if replied_message.sender.username:
                sender_display_name = f"@{replied_message.sender.username}"
            elif replied_message.sender.first_name and replied_message.sender.last_name:
                sender_display_name = f"{replied_message.sender.first_name} {replied_message.sender.last_name}"
            elif replied_message.sender.first_name:
                sender_display_name = replied_message.sender.first_name


        message_time = replied_message.date.strftime("%d.%m.%Y %H:%M")

        img_width = 800
        img_height = 450
        
        background_image_path = selected_background_path
        
        text_color = (255, 255, 255)
        info_color = (200, 200, 200)
        
        padding_x_content = 50 
        padding_y = 50

        try:
            background_img = Image.open(background_image_path).convert("RGBA")
            background_img = ImageOps.fit(background_img, (img_width, img_height), Image.Resampling.LANCZOS)
            overlay = Image.new('RGBA', background_img.size, (0, 0, 0, 128))
            img = Image.alpha_composite(background_img, overlay)
            img = img.convert("RGB")
        except FileNotFoundError:
            print(f"Фоновое изображение не найдено по пути: {background_image_path}. Использую черный фон.")
            img = Image.new('RGB', (img_width, img_height), color=(0, 0, 0))
        except Exception as e:
            print(f"Ошибка при загрузке/обработке фонового изображения: {e}. Использую черный фон.")
            img = Image.new('RGB', (img_width, img_height), color=(0, 0, 0))
            
        d = ImageDraw.Draw(img)

        # --- Загрузка шрифтов ---
        font_families = {
            'quote_bold': [
                "arialbd.ttf", # Windows
                "Arial Bold.ttf", # macOS common
                "DejaVuSans-Bold.ttf", # Linux common
                "LiberationSans-Bold.ttf", # Another Linux common
                "NotoSans-Bold.ttf" # Good general purpose if available
            ],
            'info_regular': [
                "arial.ttf", # Windows
                "Arial.ttf", # macOS common
                "DejaVuSans.ttf", # Linux common
                "LiberationSans-Regular.ttf", # Another Linux common
                "NotoSans-Regular.ttf" # Good general purpose if available
            ]
        }

        font_dirs = [
            "C:/Windows/Fonts/", # Windows
            "/System/Library/Fonts/", # macOS
            "/Library/Fonts/", # macOS
            "/usr/share/fonts/truetype/", # Linux
            "/usr/local/share/fonts/" # Linux
        ]

        def find_font_path(font_name):
            for font_dir in font_dirs:
                full_path = os.path.join(font_dir, font_name)
                if os.path.exists(full_path):
                    return full_path
            return None

        def load_best_font(font_family_list, default_size):
            for font_name in font_family_list:
                font_path = find_font_path(font_name)
                if font_path:
                    try:
                        return ImageFont.truetype(font_path, default_size)
                    except IOError as e:
                        print(f"Ошибка при загрузке шрифта {font_path}: {e}")
            print(f"Не найден подходящий шрифт из списка. Использую шрифт по умолчанию Pillow (размер {default_size}).")
            return ImageFont.load_default(size=default_size)

        # Attempt to load fonts
        quote_font = load_best_font(font_families['quote_bold'], 40)
        info_font = load_best_font(font_families['info_regular'], 25)

        # --- Обработка и перенос текста цитаты ---
        max_text_width = img_width - 2 * padding_x_content 
        
        wrapped_lines = []
        words = quote_text.split(' ')
        current_line_words = []
        for word in words:
            test_line = ' '.join(current_line_words + [word])
            if quote_font.getlength(test_line) <= max_text_width:
                current_line_words.append(word)
            else:
                wrapped_lines.append(' '.join(current_line_words))
                current_line_words = [word]
        wrapped_lines.append(' '.join(current_line_words))
        wrapped_text = "\n".join(wrapped_lines)

        # Вычисление размеров текста цитаты
        bbox_quote = d.textbbox((0,0), wrapped_text, font=quote_font, align="center")
        quote_w = bbox_quote[2] - bbox_quote[0]
        quote_h = bbox_quote[3] - bbox_quote[1]

        # --- Подготовка информации об отправителе и времени ---
        info_lines = []
        if sender_display_name:
            info_lines.append(sender_display_name)
        info_lines.append(message_time)
        info_text = "\n".join(info_lines)

        bbox_info = d.textbbox((0,0), info_text, font=info_font)
        info_h = bbox_info[3] - bbox_info[1]

        # --- Размещение элементов ---
        
        # Аватарка пользователя
        avatar_size = 90
        avatar_x = padding_x_content 
        avatar_y = padding_y

        avatar_temp_file = BytesIO()
        try:
            photos = await client.get_profile_photos(replied_message.sender, limit=1)
            if photos:
                await client.download_media(photos[0], file=avatar_temp_file)
                avatar_temp_file.seek(0)
                avatar_img = Image.open(avatar_temp_file).convert("RGBA")
                avatar_img = avatar_img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)

                mask = Image.new("L", avatar_img.size, 0)
                draw_mask = ImageDraw.Draw(mask)
                draw_mask.ellipse((0, 0, avatar_size, avatar_size), fill=255)
                
                rounded_avatar = ImageOps.fit(avatar_img, mask.size, centering=(0.5, 0.5))
                rounded_avatar.putalpha(mask)

                img.paste(rounded_avatar, (avatar_x, avatar_y), rounded_avatar)

        except Exception as e:
            print(f"Не удалось получить или обработать аватарку: {e}")
            pass

        # Позиция для имени/времени (справа от аватарки)
        info_block_center_y = avatar_y + avatar_size / 2
        info_y = info_block_center_y - info_h / 2
        
        info_x = avatar_x + avatar_size + 20 
        
        d.text((info_x, info_y), info_text, font=info_font, fill=info_color)

        # Позиция для текста цитаты (по центру, ниже блока с аватаром/информацией)
        top_of_info_block = min(avatar_y, info_y) if sender_display_name else avatar_y
        bottom_of_info_block = max(avatar_y + avatar_size, info_y + info_h) if sender_display_name else (avatar_y + avatar_size)

        quote_start_y_area = bottom_of_info_block + 15 

        available_height_for_quote = img_height - quote_start_y_area - padding_y 
        
        quote_y = quote_start_y_area + (available_height_for_quote - quote_h) / 2
        
        # Позиция X для текста цитаты (по центру, но relative to padding_x_content)
        quote_x = padding_x_content + (max_text_width - quote_w) / 2
        
        d.text((quote_x, quote_y), wrapped_text, font=quote_font, fill=text_color, align="center")

        # --- Сохранение в временный файл и отправка ---
        temp_file_path = None 

        try:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                img.save(temp_file.name, 'PNG')
                temp_file_path = temp_file.name 

            await client.send_file(
                event.chat_id,
                temp_file_path, 
                caption="✅ Ваша цитата:",
                force_document=False 
            )

        except Exception as e:
            await event.edit(f"Произошла ошибка при отправке цитаты: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print(f"Временный файл удален: {temp_file_path}")

    except Exception as e:
        await event.edit(f"Произошла ошибка при создании цитаты: {e}")
        import traceback
        traceback.print_exc()

async def cat_handler(event, client):
    """
    Обрабатывает команду .котики для отправки случайной фотографии кошки.
    """
    await event.edit("Ищу котика...")
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("https://api.thecatapi.com/v1/images/search")
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0 and 'url' in data[0]:
                cat_image_url = data[0]['url']
                await client.send_file(event.chat_id, cat_image_url, caption="Ваш котик!")
                
            else:
                await event.edit("Не удалось найти изображение кошки. Попробуйте еще раз.")
    except httpx.HTTPStatusError as e:
        await event.edit(f"Ошибка HTTP при получении котика: {e.response.status_code}")
    except httpx.RequestError as e:
        await event.edit(f"Ошибка сети при получении котика: {e}")
    except Exception as e:
        await event.edit(f"Произошла ошибка при получении котика: {e}")

async def dog_handler(event, client):
    """
    Обрабатывает команду .собачки для отправки случайной фотографии собаки.
    """
    await event.edit("Ищу собачку...")
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("https://dog.ceo/api/breeds/image/random")
            response.raise_for_status()
            data = response.json()
            if data and data.get('status') == 'success' and 'message' in data:
                dog_image_url = data['message']
                await client.send_file(event.chat_id, dog_image_url, caption="Ваша собачка!")
                
            else:
                await event.edit("Не удалось найти изображение собаки. Попробуйте еще раз.")
    except httpx.HTTPStatusError as e:
        await event.edit(f"Ошибка HTTP при получении собачки: {e.response.status_code}")
    except httpx.RequestError as e:
        await event.edit(f"Ошибка сети при получении собачки: {e}")
    except Exception as e:
        await event.edit(f"Произошла ошибка при получении собачки: {e}")

async def add_user_handler(event, client):
    """
    Обрабатывает команду .добавить для добавления пользователя в чат.
    Принимает юзернейм или ID пользователя.
    """
    if event.is_private:
        await event.edit("Эту команду можно использовать только в группах или каналах.")
        return

    input_arg = event.pattern_match.group(1)
    if not input_arg:
        await event.edit("🚫 Используйте: .добавить [юзернейм или ID пользователя].")
        return

    await event.edit(f"✅ Пытаюсь добавить пользователя {input_arg}...")
    target_user_entity = None
    try:
        # Попытка получить сущность пользователя по юзернейму или ID
        try:
            user_id_int = int(input_arg)
            target_user_entity = await client.get_entity(user_id_int)
        except ValueError:
            target_user_entity = await client.get_entity(input_arg)
    except UsernameInvalidError:
        await event.edit("⛔ Ошибка: Неверный юзернейм или ID пользователя.")
        return
    except Exception as e:
        await event.edit(f"Ошибка при поиске пользователя: {e}")
        return

    if not target_user_entity:
        await event.edit("Не удалось найти пользователя.")
        return

    try:
        # Получаем чат, в котором была вызвана команда
        chat = await event.get_chat()

        # CORRECTED: Use client(InviteToChannelRequest) for inviting users
        # The target_user_entity needs to be a list for InviteToChannelRequest
        await client(InviteToChannelRequest(
            channel=chat,
            users=[target_user_entity]
        ))
        
        await event.edit(f"✅ Пользователь [{target_user_entity.first_name}](tg://user?id={target_user_entity.id}) успешно добавлен в чат.")
    except ChatAdminRequiredError:
        await event.edit("🚫 Ошибка: У меня нет прав администратора для добавления пользователей в этот чат.")
    except UserPrivacyRestrictedError:
        await event.edit("🚫 Ошибка: Пользователь запретил добавление в группы через настройки приватности.")
    except PeerFloodError:
        await event.edit("🚫 Ошибка: Слишком много попыток добавления пользователей. Пожалуйста, подождите.")
    except UserNotMutualContactError:
        await event.edit("🚫 Ошибка: Не удалось добавить пользователя. Возможно, он не является взаимным контактом или имеет строгие настройки приватности.")
    except FloodWaitError as e:
        await event.edit(f"🚫 Ошибка: Превышен лимит запросов. Пожалуйста, подождите {e.seconds} секунд.")
        await asyncio.sleep(e.seconds) # Ждем, если Telethon просит
    except Exception as e:
        await event.edit(f"🚫 Произошла непредвиденная ошибка при добавлении пользователя: {e}")
        import traceback
        traceback.print_exc() # This will print the full traceback to your console

async def fire_handler(event, client):
    """
    Обрабатывает команду .огонь для отображения анимированного ASCII-арта огня.
    """
    await event.edit("Зажигаю огонь 🔥...")

    fire_frames = [
        """
🔥
""",
        """
  🔥
 🔥🔥
""",
        """
  🔥
 🔥🔥
🔥🔥🔥
""",
        """
  🔥
 🔥🔥🔥
🔥🔥🔥🔥
""",
        """
    🔥
  🔥🔥
 🔥🔥🔥
🔥🔥🔥🔥
""",
        """
    🔥
  🔥🔥
 🔥🔥🔥
🔥🔥🔥🔥🔥
""",
        """
    🔥
   🔥🔥
  🔥🔥🔥
 🔥🔥🔥🔥🔥
""",
        """
    🔥
   🔥🔥
  🔥🔥🔥
 🔥🔥🔥🔥🔥
🔥🔥🔥🔥🔥🔥
""",
        """
      🔥
    🔥🔥
   🔥🔥🔥
  🔥🔥🔥🔥
 🔥🔥🔥🔥🔥
🔥🔥🔥🔥🔥🔥
""",
        """
      🔥
     🔥🔥
    🔥🔥🔥
   🔥🔥🔥🔥
  🔥🔥🔥🔥🔥
  🔥🔥🔥🔥🔥🔥
🔥🔥🔥🔥🔥🔥
""",
        """
        🔥
      🔥🔥
     🔥🔥🔥
    🔥🔥🔥🔥
   🔥🔥🔥🔥🔥
  🔥🔥🔥🔥🔥🔥
 🔥🔥🔥🔥🔥🔥🔥
🔥🔥🔥🔥🔥🔥🔥🔥
"""
    ]

    msg = await event.edit(fire_frames[0].strip())

    num_loops = 3 
    for _ in range(num_loops):
        for i, frame in enumerate(fire_frames):
            current_frame_content = frame.strip()

            # Добавим небольшой маркер, чтобы даже одинаковые кадры были разными для API
            unique_content = f"{current_frame_content}\n` {i % 2}`" 

            try:
                if msg.text != unique_content: 
                    await msg.edit(unique_content)
                else:
                    await msg.edit(f"{current_frame_content}\n` {time.time()}`") 

                await asyncio.sleep(0.15) 
            except FloodWaitError as e:
                print(f"Flood wait {e.seconds} секунд при анимации огня")
                await asyncio.sleep(e.seconds)
            except Exception as e:
                print(f"Ошибка при обновлении анимации огня: {e}")
                break
        await asyncio.sleep(0.5) 

    await msg.edit("🔥 **Огонь потушен!** 🔥")

# Новая команда: Калькулятор
async def calculator_handler(event, client):
    """
    Обрабатывает команду .калькулятор для вычисления математических выражений.
    """
    expression = event.pattern_match.group(1)
    if not expression:
        await event.edit("⛔ Используйте: `.калькулятор [выражение]`\nПример: .калькулятор 2+2*3")
        return

    try:
        # Безопасная оценка выражения
        # Используем eval с осторожностью. Можно использовать библиотеку like `numexpr` для большей безопасности
        # Для простых операций eval достаточно, но нужно фильтровать ввод.
        result = eval(expression)
        await event.edit(f"🔢 Результат: `{expression}` = `{result}`")
    except SyntaxError:
        await event.edit("❌ Ошибка: Неверное математическое выражение.")
    except NameError:
        await event.edit("❌ Ошибка: Выражение содержит недопустимые символы или функции.")
    except Exception as e:
        await event.edit(f"❌ Произошла ошибка при вычислении: {e}")

# ОБНОВЛЕННАЯ КОМАНДА: Погода (использует Wttr.in для изображения)
async def weather_handler(event, client):
    """
    Обрабатывает команду .погода для получения информации о погоде с Wttr.in в виде изображения.
    """
    city = event.pattern_match.group(1)
    if not city:
        await event.edit("Использование: `.погода [город]`\nПример: .погода Киев")
        return

    # Заменяем пробелы на '+' для URL, а также обрабатываем кириллицу (Wttr.in её понимает)
    city_encoded = city.replace(" ", "+") 

    await event.edit(f"Запрашиваю погоду в {city} с Wttr.in...")
    try:
        async with httpx.AsyncClient() as http_client:
            # Запрашиваем PNG изображение погоды
            # ?.png для получения картинки, &lang=ru для русского языка, &0 для текущей погоды без прогноза
            url_png = f"https://wttr.in/{city_encoded}_0.png?lang=ru&0" # Добавлен _0 для более компактного вида, если доступно

            response_png = await http_client.get(url_png, follow_redirects=True)
            response_png.raise_for_status() # Вызовет исключение для ошибок HTTP

            # Проверяем, что ответ действительно является изображением
            if 'image' in response_png.headers.get('Content-Type', ''):
                img_bytes = BytesIO(response_png.content)
                # Отправляем изображение как файл
                await client.send_file(event.chat_id, img_bytes, caption=f"☀️ Погода в {city} (Wttr.in)", file_name="weather.png")
                await event.delete() # Удаляем промежуточное сообщение "Запрашиваю погоду..."
            else:
                # Если wttr.in вернул не изображение (например, ошибку в виде текста)
                # Попробуем запросить текстовый вариант для диагностики, если изображение не получено
                text_url = f"https://wttr.in/{city_encoded}?lang=ru&0"
                text_response = await http_client.get(text_url, follow_redirects=True)
                text_response.raise_for_status()
                weather_text_fallback = text_response.text

                if "Unknown location" in weather_text_fallback or "Sorry, we don't have weather data for" in weather_text_fallback:
                    await event.edit(f"Не удалось найти погоду для города: `{city}`. Пожалуйста, проверьте название.")
                else:
                    await event.edit(f"Не удалось получить изображение погоды. Возможно, wttr.in вернул ошибку в текстовом виде:\n```\n{weather_text_fallback}\n```")


    except httpx.HTTPStatusError as e:
        await event.edit(f"❌ Ошибка HTTP при получении погоды с Wttr.in: {e.response.status_code}")
    except httpx.RequestError as e:
        await event.edit(f"❌ Ошибка сети при получении погоды с Wttr.in: {e}")
    except Exception as e:
        await event.edit(f"❌ Произошла ошибка при получении погоды с Wttr.in: {e}")
        import traceback
        traceback.print_exc()




async def chat_info_handler(event, client, session_name):
    """
    Обрабатывает команду .чатинфо для получения информации о чате.
    """
    
    print(f"[{session_name}] Получена команда .чатинфо в чате {event.peer_id}.")
    
    status_message = await event.reply("⏳ Собираю информацию о чате...")

    try:
        chat = await event.get_chat()
        chat_id = chat.id
        chat_title = chat.title
        chat_type = "Канал" if event.is_channel else "Группа"
        
        participants_count = await client.get_participants(chat, limit=0)
        
        link = f"https://t.me/{chat.username}" if chat.username else "Нет публичной ссылки"

        admin_list = []
        try:
            async for participant in client.iter_participants(chat, filter=ChannelParticipantsAdmins):
                
                user_obj = None
                if isinstance(participant, (ChannelParticipantCreator, ChannelParticipantAdmin)):
                    user_obj = participant.user
                elif isinstance(participant, User):
                    user_obj = participant
                else:
                    try:
                        user_obj = await client.get_entity(participant.id)
                    except Exception as e:
                        print(f"[{session_name}] Ошибка получения user_obj для {participant.id}: {e}")
                        continue
                        
                if user_obj:
                    # Изменение здесь: используем username, если доступен, иначе first_name
                    admin_display_name = f"@{user_obj.username}" if user_obj.username else user_obj.first_name
                    if user_obj.last_name and not user_obj.username: # Добавляем фамилию только если нет юзернейма
                        admin_display_name += f" {user_obj.last_name}"
                    
                    admin_status = ""
                    if isinstance(participant, ChannelParticipantCreator):
                        admin_status = " (Создатель)"
                    elif isinstance(participant, ChannelParticipantAdmin) and participant.rank:
                        admin_status = f" ({participant.rank})"
                    elif isinstance(participant, ChannelParticipantAdmin):
                        admin_status = " (Админ)"
                    
                    admin_list.append(
                        f"• {admin_display_name} | ID: `{user_obj.id}`{admin_status} {'[Бот]' if user_obj.bot else '[Админ]'}"
                    )

        except ChatAdminRequiredError:
            admin_list.append("Не удалось получить список администраторов (юзербот не является администратором в этом чате).")
        except Exception as e:
            admin_list.append(f"Ошибка при получении администраторов: {e} (пожалуйста, убедитесь, что юзербот является администратором).")
            print(f"[{session_name}] Ошибка при получении администраторов для {chat_title} ({chat_id}): {e}")

        admins_str = "\n".join(admin_list) if admin_list else "Нет администраторов или не удалось получить."

        response_message = (
            f"**🧾 Информация о чате:**\n"
            f"**ℹ️ Название:** `{chat_title}`\n"
            f"**💾 ID чата:** `{chat_id}`\n"
            f"**💬 Тип:** `{chat_type}`\n"
            f"**🗃️ Количество участников:** `{participants_count.total}`\n"
            f"**🔗 Ссылка:** {link}\n\n"
            f"**👑 Администраторы:**\n{admins_str}"
        )

        await status_message.edit(response_message)
        print(f"[{session_name}] Информация о чате {chat_title} успешно отправлена.")

    except Exception as e:
        print(f"[{session_name}] Общая ошибка в chat_info_handler для чата {event.peer_id}: {e}")
        await status_message.edit(f"❌ Произошла ошибка при получении информации о чате: {e}")


# --- Обработчики для команды .игнора и колбэка кнопки ---

from telethon import Button
from telethon.tl.types import User, Channel, Chat

# Global cache to store the full unread messages for each user
full_unread_messages_cache = {}

async def ignore_handler(event, client):
    """
    Counts and reports the number of unread chats, including those with mentions.
    This version reports the count and provides instructions to use a new command.
    """
    print("Executing ignore_handler...") # Debugging output
    try:
        unread_chats = []

        async for dialog in client.iter_dialogs():
            if dialog.unread_count > 0 or dialog.unread_mentions_count > 0:
                unread_chats.append(dialog)

        unread_count = len(unread_chats)
        print(f"Found {unread_count} unread chats.") # Debugging output

        if unread_count > 0:
            response_message_short = (
                f"⁉️У вас **{unread_count}** непрочитанных чатов.\n"
                f"‼️ Чтобы получить полный список в Избранное, используйте команду `.посмотретьчаты`."
            )

            response_message_full = "📜 **Список всех непрочитанных чатов:**\n\n"
            if unread_chats:
                for dialog in unread_chats:
                    title = dialog.title if dialog.title else "Скрытый чат"
                    try:
                        if isinstance(dialog.entity, User):
                            chat_link = f"tg://user?id={dialog.entity.id}"
                        elif isinstance(dialog.entity, (Channel, Chat)):
                            if dialog.entity.username:
                                chat_link = f"https://t.me/{dialog.entity.username}"
                            else:
                                # For private chats (without a username), use tg://resolve?domain=c<chat_id>
                                chat_link = f"tg://resolve?domain=c{abs(dialog.entity.id)}"
                        else:
                            chat_link = title # If chat type is not defined, just use the title

                        response_message_full += (
                            f"- [{title}]({chat_link}) "
                            f"(Непрочитанных: {dialog.unread_count}, Упоминаний: {dialog.unread_mentions_count})\n"
                        )
                    except Exception as e:
                        response_message_full += (
                            f"- {title} (Непрочитанных: {dialog.unread_count}, Упоминаний: {dialog.unread_mentions_count}) "
                            f"- Ошибка ссылки ({e})\n"
                        )
            else:
                response_message_full += "Нет непрочитанных чатов."

            # Send the short message to the chat
            await client.send_message(
                entity=event.chat_id, # Send to the same chat where the command was issued
                message=response_message_short
            )
            print("Unread count message sent successfully with instructions.") # Debugging output

            # Store the full message in the temporary cache.
            global full_unread_messages_cache
            full_unread_messages_cache[event.sender_id] = response_message_full

        else:
            await client.send_message(event.chat_id, "У вас нет непрочитанных чатов. 🎉")
            print("No unread chats message sent.") # Debugging output

    except Exception as e:
        print(f"Error in ignore_handler: {e}") # Debugging output for error
        await client.send_message(event.chat_id, f"Произошла ошибка при подсчёте непрочитанных чатов: {e}")
        import traceback
        traceback.print_exc()

# This function handles the new command to send the full list to "Saved Messages"
async def show_chats_command_handler(event, client):
    """
    Sends the full list of unread chats to the user's "Saved Messages" (Избранное).
    """
    print("Executing show_chats_command_handler...") # Debugging output
    sender_id = event.sender_id

    global full_unread_messages_cache
    if sender_id in full_unread_messages_cache:
        full_message = full_unread_messages_cache[sender_id]

        try:
            # Get the "Saved Messages" entity ('me' always points to "Saved Messages")
            saved_messages_entity = await client.get_entity('me')
            await client.send_message(saved_messages_entity, full_message, link_preview=False) # Send the message
            await event.reply("Список непрочитанных чатов отправлен в Избранное! ✅") # Confirm sending in the original chat

            # Clear the cache after sending to avoid storing old data
            del full_unread_messages_cache[sender_id]
        except Exception as e:
            await event.reply(f"Не удалось отправить список в Избранное: {e}")
            import traceback
            traceback.print_exc()
    else:
        await event.reply("⛔ Ошибка: Список не найден или устарел. Пожалуйста, сначала используйте команду .игнор.")

import re  # В начале файла, если не импортировал

import re
import time  # для измерения времени

async def ai_handler(event, client):
    """
    Команда /ai [вопрос] — отвечает с помощью Mistral AI (без памяти), с измерением времени и токенов.
    """
    prompt = event.text.split(" ", 1)
    if len(prompt) < 2 or not prompt[1].strip():
        await event.reply("❌ Пожалуйста, укажите вопрос после /ai")
        return

    question = prompt[1].strip()
    thinking_msg = await event.reply("🤖 Принял твой вопрос! Думаю над ответом..")

    # 🔍 Ответ на "кто ты?"
    if re.search(r"\b(кто\s+ты|что\s+ты\s+такое|ты\s+кто|ты\s+что)\b", question.lower()):
        await thinking_msg.edit("Привет! Я - умный ЮзерБот. У меня есть множество полезных функций. Мой разработчик - @sedativine. Если имеются вопросы, я тебя слушаю!")
        return

    try:
        start = time.time()
        async with aiohttp.ClientSession() as session:
            headers = {
                "Authorization": f"Bearer {MISTRAL_API_KEY}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "mistral-tiny",
                "messages": [
                    {"role": "user", "content": question}
                ]
            }
            async with session.post("https://api.mistral.ai/v1/chat/completions", headers=headers, json=data) as resp:
                resp.raise_for_status()
                res_json = await resp.json()
        end = time.time()

        reply = res_json["choices"][0]["message"]["content"]
        usage = res_json.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", "—")
        completion_tokens = usage.get("completion_tokens", "—")
        total_tokens = usage.get("total_tokens", "—")
        elapsed_ms = int((end - start) * 1000)

        final_msg = (
            f"{reply}\n\n"
            f"🧠 Ответ за {elapsed_ms}мс\n🔢 Затрачено токенов: {total_tokens} "
        )

        await thinking_msg.edit(final_msg)

    except aiohttp.ClientResponseError as e:
        await thinking_msg.edit(f"❌ Ошибка HTTP: {e.status}")
    except Exception as e:
        await thinking_msg.edit(f"❌ Ошибка запроса к AI: {e}")


async def test_button_handler(event, client):
    """
    Тестовая команда для проверки работы inline-кнопок.
    """
    print("Executing test_button_handler...") # Отладочный вывод
    try:
        await event.delete() # Удаляем команду, чтобы отправить новое сообщение

        buttons = [
            Button.inline("Нажми меня!", data="test_data_123"),
            Button.url("Google", "https://google.com")
        ]

        await client.send_message(
            event.chat_id,
            "Это тестовое сообщение с кнопками:",
            buttons=buttons
        )
        print("Test message with buttons sent successfully.") # Отладочный вывод
    except Exception as e:
        print(f"Error in test_button_handler: {e}") # Отладочный вывод ошибки
        import traceback
        traceback.print_exc()

async def test_button_callback(event):
    """
    Обработчик для тестовой inline-кнопки.
    """
    print(f"Test button callback received: {event.data.decode()}") # Отладочный вывод
    await event.answer("Ты нажал тестовую кнопку!", alert=True) # Всплывающее уведомление

# --- Ваш help_handler (замените им текущий) ---
async def help_handler(event, client):
    """
    Обрабатывает команду .помощь для вывода первой страницы списка команд.
    """
    # Здесь мы не будем добавлять кнопку "Далее", если хотим использовать отдельную команду
    # Если вы все же хотите кнопку, которая ведет на help_handler_page2,
    # то измените эту часть:
    buttons = [
        Button.inline("Показать вторую страницу ➡️", data="go_to_help_page_2_via_button")
    ]
    await event.edit(HELP_TEXT_PAGE_1, buttons=buttons, link_preview=False)


# --- НОВАЯ ФУНКЦИЯ для команды .помощь2 ---
async def help_handler_page2(event, client):
    """
    Обрабатывает команду .помощь2 для вывода второй страницы списка команд.
    """
    await event.edit(HELP_TEXT_PAGE_2, link_preview=False)

from PIL import Image, ImageDraw, ImageFont
import os

async def generate_image_handler(event, client):
    args = event.raw_text.split(" ", 1)
    prompt = args[1] if len(args) > 1 else "красивый закат над морем"

    # Отвечаем новым сообщением, не редактируем старое
    msg = await event.respond("🎨 Генерирую изображение по описанию...")

    try:
        image_url = await(prompt)

        if image_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    img_bytes = await resp.read()

            await client.send_file(event.chat_id, BytesIO(img_bytes), caption=f"🖼 По запросу: {prompt}", file_name="gen.png")
        else:
            await msg.edit("❌ Не удалось сгенерировать изображение.")
    except Exception as e:
        await msg.edit(f"❌ Ошибка генерации: {e}")


# --- И если вы хотите, чтобы кнопка из .помощь все же работала, вам нужна функция для нее ---
async def go_to_help_page_2_via_button_callback(event, client):
    """
    Обрабатывает нажатие кнопки для перехода на вторую страницу помощи.
    """
    # Здесь вы можете просто вызвать help_handler_page2, чтобы избежать дублирования текста
    await help_handler_page2(event, client)

async def wiki_handler(event, client):
    """
    Обрабатывает команду .wiki для поиска информации в Wikipedia.
    """
    query = event.pattern_match.group(1)
    if not query:
        await event.edit("Использование: `.wiki <запрос>`")
        return

    await event.edit(f"Ищу информацию на Wikipedia по запросу: `{query}`...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            # Поиск страницы
            search_url = "https://ru.wikipedia.org/w/api.php"
            search_params = {
                "action": "opensearch",
                "search": query,
                "limit": "1",
                "namespace": "0",
                "format": "json"
            }
            search_response = await http_client.get(search_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()

            if not search_data[1]: # Если нет результатов поиска
                await event.edit(f"По запросу `{query}` ничего не найдено на Wikipedia.")
                return

            page_title = search_data[1][0]
            page_url = search_data[3][0]

            # Получение краткого содержания
            summary_url = "https://ru.wikipedia.org/w/api.php"
            summary_params = {
                "action": "query",
                "format": "json",
                "prop": "extracts",
                "exintro": True,  # Только введение
                "explaintext": True, # Обычный текст без HTML
                "titles": page_title,
                "exsentences": "3" # Только 3 предложения
            }
            summary_response = await http_client.get(summary_url, params=summary_params)
            summary_response.raise_for_status()
            summary_data = summary_response.json()

            page_id = list(summary_data['query']['pages'].keys())[0]
            extract = summary_data['query']['pages'][page_id].get('extract', 'Краткое содержание не найдено.')

            # Ограничиваем длину сообщения для Telegram
            if len(extract) > 800: # Примерное ограничение
                extract = extract[:797] + "..."

            response_message = (
                f"📚 **Wikipedia: {page_title}**\n\n"
                f"{extract}\n\n"
                f"🔗 Подробнее: {page_url}"
            )
            await event.edit(response_message, link_preview=False) # Отключаем предпросмотр ссылки

    except httpx.HTTPStatusError as e:
        await event.edit(f"❌ Ошибка HTTP при обращении к Wikipedia: {e.response.status_code}")
    except httpx.RequestError as e:
        await event.edit(f"❌ Ошибка сети при обращении к Wikipedia: {e}")
    except json.JSONDecodeError:
        await event.edit("❌ Ошибка обработки ответа от Wikipedia.")
    except Exception as e:
        await event.edit(f"❌ Произошла непредвиденная ошибка при поиске Wikipedia: {e}")
        import traceback
        traceback.print_exc()

async def botinfo_handler(event, client):
    """
    Обрабатывает команду .botinfo для вывода информации о юзерботе и его создателе.
    """

    message = (
        f"🤖 **Информация о юзерботе:**\n"
        f"✨ Название: MorganLP\n"
        f"👑 Создатель: @sedativine\n"
        f"🛠️ Версия: Beta\n" # Можете изменить или удалить
        f"💡 Описание: Этот юзербот предоставляет различные полезные функции как: .калькулятор, .чатинфо, .погода, и др. (Более подробно - .помощь)"
    )
    await event.edit(message)

# --- ИГРА "СЛОВА" ---

# Словарь для отслеживания активных игр (перенесено наверх как глобальная переменная)
# active_words_games = {} # {chat_id: {'organizer_id': int, 'players': [], 'current_player_index': int, 'last_word': str, 'used_words': [], 'game_id': str}}

import uuid


# Assuming these are defined elsewhere in your actual code

# Assuming these are defined elsewhere in your actual code

# Import necessary Telethon types for buttons
from telethon import Button
from telethon.tl.types import ReplyInlineMarkup, KeyboardButtonCallback


async def start_words_game_setup(event, client):
    """Начинает подбор игроков для игры 'Слова'."""
    chat_id = str(event.chat_id)
    organizer_id = event.sender_id

    # Safely get the organizer's name
    if event.sender: # Check if sender exists
        organizer_name = event.sender.first_name
    else:
        # Fallback if event.sender is None (e.g., channel post, service message)
        # You might want to log this or handle it based on your bot's logic
        print(f"WARNING: event.sender is None for chat {chat_id}, sender_id {organizer_id}")
        organizer_name = "Пользователь" # Default name
        # Alternatively, you could return here if you only want user-initiated commands
        # await client.send_message(event.chat_id, "Эта команда может быть использована только пользователями.")
        # return


    print(f"DEBUG: .слподбор received in chat {chat_id} by {organizer_name} ({organizer_id})")

    if chat_id in active_words_games:
        if active_words_games[chat_id]['organizer_id'] == organizer_id:
            await client.send_message(event.chat_id, "⛔ Игра уже начата вами. Используйте .слстарт, когда готовы.")
        else:
            await client.send_message(event.chat_id, "❎ В этом чате уже идёт подбор игроков для другой игры. Подождите, пока она завершится.")
        return

    game_id = str(uuid.uuid4()) # Генерируем уникальный ID для игры
    active_words_games[chat_id] = {
        'organizer_id': organizer_id,
        'organizer_name': organizer_name,
        'players': [{'id': organizer_id, 'name': organizer_name, 'words_count': 0}],
        'current_player_index': 0,
        'last_word': '',
        'used_words': [],
        'state': 'setup',
        'game_id': game_id
    }
    save_words_games(active_words_games)

    organizer_mention = format_player_mention({'id': organizer_id, 'name': organizer_name})

    await client.send_message(
        event.chat_id,
        f"**✅ Игра 'Слова (на последнюю букву)'**: Подбор игроков начат!\n"
        f"Организатор: {organizer_mention}\n"
        f"Чтобы присоединиться, напишите .слвойти"
    )
    print(f"DEBUG: Game setup started in chat {chat_id} by {organizer_name}. Game ID: {game_id}")

async def join_words_game(event, client):
    """Позволяет игроку присоединиться к игре 'Слова'."""
    chat_id = str(event.chat_id)
    player_id = event.sender_id
    player_name = event.sender.first_name if event.sender.first_name else "Неизвестный"
    if event.sender.username:
        player_name += f" (@{event.sender.username})"

    print(f"[{datetime.now()}] DEBUG: .слвойти received in chat {chat_id} by {player_name} ({player_id})")

    # Проверяем, есть ли активная игра в состоянии "setup"
    if chat_id not in active_words_games or active_words_games[chat_id]['state'] != 'setup':
        # Если нет, запускаем новую игру с текущим игроком как организатором
        print(f"[{datetime.now()}] DEBUG: No active setup in chat {chat_id} for .слвойти. Starting new game setup.")
        game_id = str(uuid.uuid4())
        active_words_games[chat_id] = {
            'organizer_id': player_id, # Отправитель становится организатором
            'organizer_name': player_name,
            'players': [], # Начнем с пустого списка, затем добавим текущего игрока
            'current_player_index': 0,
            'last_word': '',
            'used_words': [],
            'state': 'setup',
            'game_id': game_id
        }
        save_words_games(active_words_games)
        
        # Use the new helper for player/organizer mention
        organizer_mention = format_player_mention({'id': player_id, 'name': player_name})
        
        await client.send_message( # Отправляем сообщение о начале подбора
            event.chat_id,
            f"**📣 Игра 'Слова (на последнюю букву)'**: Подбор игроков начат автоматически командой .слвойти!\n"
            f"Организатор: {organizer_mention}\n"
            f"Вы уже в игре. Другие игроки могут присоединиться, написав `.слвойти`."
        )
        # Добавляем текущего игрока после создания новой игры
        active_words_games[chat_id]['players'].append({'id': player_id, 'name': player_name, 'words_count': 0})
        save_words_games(active_words_games)
        print(f"[{datetime.now()}] DEBUG: Player {player_name} joined (as organizer) game {game_id} in chat {chat_id}.")
        return # Выходим, так как игрок уже обработан
            
    game_data = active_words_games[chat_id]
    if any(p['id'] == player_id for p in game_data['players']):
        await event.delete() # Удаляем команду
        await client.send_message(event.chat_id, "ℹ️ Вы уже в игре.")
        print(f"[{datetime.now()}] DEBUG: Player {player_name} already in game {game_data['game_id']}.")
        return

    # Добавляем 'words_count' для присоединяющегося игрока
    game_data['players'].append({'id': player_id, 'name': player_name, 'words_count': 0})
    save_words_games(active_words_games) # Сохраняем состояние

    # Use the new helper for formatting all player names
    player_mentions = [format_player_mention(p) for p in game_data['players']]
    player_list_str = ", ".join(player_mentions)
    
    # Use the new helper for the joining player
    joining_player_mention = format_player_mention({'id': player_id, 'name': player_name})

    await client.send_message( # Отправляем НОВОЕ сообщение
        event.chat_id,
        f"🎉 {joining_player_mention} присоединился к игре! Текущие игроки: {player_list_str}"
    )
    print(f"[{datetime.now()}] DEBUG: Player {player_name} joined game {game_data['game_id']} in chat {chat_id}.")


async def generate_image_by_prompt(prompt: str) -> str:
    # Placeholder for Replicate API call
    # You would need to define 'replicate' object and its 'run' method
    # For this example, we'll just return a dummy URL.
    print(f"DEBUG: Generating image for prompt: '{prompt}' (Replicate call placeholder)")
    return "https://example.com/generated_image.jpg"


async def return_to_words_game(event, client):
    """Позволяет игроку вернуться в игру 'Слова', если он ранее вышел."""
    chat_id = str(event.chat_id)
    player_id = event.sender_id
    player_name = event.sender.first_name

    if chat_id not in active_words_games:
        await event.reply("🤷 В этом чате нет активной игры, в которую можно вернуться.")
        return

    game_data = active_words_games[chat_id]

    if any(p['id'] == player_id for p in game_data['players']):
        await event.reply("Вы уже участвуете в этой игре.")
        return

    if game_data['state'] != 'active':
        await event.reply("👀 Сейчас идёт подбор игроков. Используйте .слвойти, чтобы присоединиться.")
        return

    game_data['players'].insert(game_data['current_player_index'], {'id': player_id, 'name': player_name})
    save_words_games(active_words_games)

    # Use the new helper for the returning player
    returning_player_mention = format_player_mention({'id': player_id, 'name': player_name})
    await event.reply(f"🎉 {returning_player_mention} вернулся в игру!")


async def start_words_game_actual(event, client):
    """Начинает игру 'Слова' после подбора игроков."""
    chat_id = str(event.chat_id)
    organizer_id = event.sender_id

    print(f"DEBUG: .слстарт received in chat {chat_id} by {organizer_id}.")

    if chat_id not in active_words_games:
        await client.send_message(event.chat_id, "🤷 В этом чате нет активной игры или подбора игроков для 'Слова'.")
        return

    game_data = active_words_games[chat_id]

    if game_data['organizer_id'] != organizer_id:
        await client.send_message(event.chat_id, "⛔ Только организатор игры может её начать.")
        return

    if game_data['state'] == 'active':
        await client.send_message(event.chat_id, "ℹ️Игра 'Слова' уже идёт.")
        return

    if len(game_data['players']) < 2: # Минимум 2 игрока (организатор + 1)
        await client.send_message(event.chat_id, "🚫 Недостаточно игроков для начала игры. Нужно минимум 2 игрока.")
        return

    game_data['state'] = 'active'
    
    # Перемешиваем игроков
    random.shuffle(game_data['players'])
    game_data['current_player_index'] = 0

    # Выбираем случайную первую букву (без ъ, ь, ы, й, щ, э, ю, я)
    russian_alphabet = "абвгдежзиклмнопрстуфхцчш"
    first_letter = random.choice(russian_alphabet).upper() # Большая буква

    game_data['last_word'] = f"@{first_letter}" # Используем @ чтобы обозначить букву
    game_data['used_words'] = [] # Сбрасываем использованные слова для новой игры
    save_words_games(active_words_games) # Сохраняем состояние

    current_player = game_data['players'][game_data['current_player_index']]
    
    # Use the new helper for current player mention
    current_player_mention = format_player_mention(current_player)

    await client.send_message( # Отправляем НОВОЕ сообщение
        event.chat_id,
        f"✅ **Игра 'Слова' началась!** (ID игры: `{game_data['game_id']}`)\n"
        f"Первый ход: {current_player_mention}\n"
        f"Вам нужно назвать слово на букву **{first_letter}**."
    )
    print(f"DEBUG: Game {game_data['game_id']} started in chat {chat_id}. First letter: {first_letter}")


async def process_word_turn(event, client):
    """
    Обрабатывает ход игрока в игре 'Слова'.
    Эта функция будет реагировать на *любое* сообщение, если игра активна,
    но будет игнорировать сообщения, которые являются командами игры.
    """
    chat_id = str(event.chat_id)
    sender_id = event.sender_id
    word = event.text.strip().lower()

    print(f"DEBUG: Processing potential word turn: '{word}' from {sender_id} in chat {chat_id}")

    # Список команд, которые должны быть проигнорированы в процессе игры
    game_commands = [
        '.слподбор', '.слвойти', '.слстарт', '.слстоп', '.слвыйти'
    ]

    # Проверяем, является ли сообщение одной из игровых команд
    if any(word.startswith(cmd) for cmd in game_commands):
        print(f"DEBUG: Message '{word}' is a game command, skipping process_word_turn.")
        return # Если это игровая команда, просто выходим, она будет обработана своим хэндлером


    if chat_id not in active_words_games or active_words_games[chat_id]['state'] != 'active':
        print(f"DEBUG: Game not active in chat {chat_id}.")
        return # Игра не активна в этом чате

    game_data = active_words_games[chat_id]
    current_player_index = game_data['current_player_index']
    current_player = game_data['players'][current_player_index]

    # Проверяем, что ход делает текущий игрок
    if sender_id != current_player['id']:
        print(f"DEBUG: Sender {sender_id} is not current player {current_player['id']}. Ignoring.")
        # await event.reply("Сейчас не ваш ход!") # Можно добавить это, но может быть спамно
        return

    # Проверка слова:
    # 1. Должно быть только русскими буквами
    if not re.fullmatch(r'[а-яё]+', word):
        await event.reply("❌ Некорректное слово. Используйте только русские буквы.")
        print(f"DEBUG: Invalid word '{word}' (non-russian characters).")
        return

    # 2. Не должно быть короче 2 символов
    if len(word) < 2:
        await event.reply("❌ Слово должно быть не короче 2 букв.")
        print(f"DEBUG: Invalid word '{word}' (too short).")
        return

    last_word_info = game_data['last_word']
    required_letter = last_word_info[-1] # Последняя буква предыдущего слова
    if last_word_info.startswith('@'): # Если это первый ход и last_word = @БУКВА
        required_letter = last_word_info[1].lower() # Берем букву после @

    # Обработка исключений для букв ъ, ь, ы
    if required_letter in 'ъьы':
        if len(last_word_info) > 1 and not last_word_info.startswith('@'):
            required_letter = last_word_info[-2].lower() # Берем предпоследнюю букву
        else:
            pass # Если бот выбирает первую букву, он должен избегать ъ, ь, ы


    if not word.startswith(required_letter):
        await event.reply(f"❌ Слово должно начинаться на букву **{required_letter.upper()}**.")
        print(f"DEBUG: Invalid word '{word}' (does not start with '{required_letter}').")
        return

    if word in game_data['used_words']:
        await event.reply("❌ Это слово уже было использовано в этой игре.")
        print(f"DEBUG: Invalid word '{word}' (already used).")
        return

    # Слово принято!
    game_data['last_word'] = word
    game_data['used_words'].append(word)
    
    # УВЕЛИЧИВАЕМ СЧЁТЧИК СЛОВ ДЛЯ ТЕКУЩЕГО ИГРОКА
    game_data['players'][current_player_index]['words_count'] += 1

    # Переход хода к следующему игроку
    game_data['current_player_index'] = (game_data['current_player_index'] + 1) % len(game_data['players'])
    next_player = game_data['players'][game_data['current_player_index']]

    save_words_games(active_words_games) # Сохраняем состояние

    # Определяем букву для следующего хода
    next_required_letter = word[-1].lower()
    # Если последняя буква ъ, ь, ы - ищем предпоследнюю
    if next_required_letter in 'ъьы':
        if len(word) > 1:
            next_required_letter = word[-2].lower()
        else:
            await event.reply(f"⁉️ Слово '{word}' оканчивается на '{next_required_letter.upper()}'. Кажется, произошла ошибка. Следующее слово должно начинаться на любую букву.")
            print(f"WARNING: Word '{word}' ends with '{next_required_letter}', which is a problematic letter for game rules. Next letter will be based on second to last character.")
            return

    # ИСПРАВЛЕНИЕ ОШИБКИ ValueError: Cannot find any entity corresponding to "-1002236998585"
    current_chat_entity = await event.get_chat() # Получаем сущность чата
    
    # Use the new helper for next player mention
    next_player_mention = format_player_mention(next_player)

    await client.send_message(
        current_chat_entity, # Используем полученную сущность чата
        f"✅ Засчитано! **{word.capitalize()}**\n"
        f"Счёт {format_player_mention(current_player)}: **{current_player['words_count']}** слов.\n" # Показываем счёт
        f"Следующий ход: {next_player_mention}\n"
        f"Вам на букву **{next_required_letter.upper()}**."
    )
    print(f"DEBUG: Game {game_data['game_id']}: Player {current_player['name']} played '{word}'. Next turn for {next_player['name']} on '{next_required_letter}'.")

    
async def stop_words_game(event, client):
    """Останавливает игру 'Слова'."""
    chat_id = str(event.chat_id)
    sender_id = event.sender_id

    print(f"DEBUG: .слстоп received in chat {chat_id} by {sender_id}.")

    if chat_id not in active_words_games:
        await client.send_message(event.chat_id, "🤷 В этом чате нет активной игры 'Слова'.")
        return

    game_data = active_words_games[chat_id]

    # Только организатор или человек, который использовал команду .слвойти (если он стал организатором по факту)
    # может остановить игру. Если организатор ушел, то игру может остановить новый организатор.
    # Для простоты, оставим, что только изначальный организатор может остановить игру,
    # или можно добавить проверку, что если текущий организатор (в active_words_games) совпадает с sender_id.
    if game_data['organizer_id'] != sender_id:
        await client.send_message(event.chat_id, "⛔ Только организатор игры может её остановить.")
        return

    game_id = game_data['game_id']
    
    winning_message = ""
    # Если игра была активна и есть игроки, объявляем текущего игрока "победителем"
    if game_data['state'] == 'active' and game_data['players']:
        last_active_player = game_data['players'][game_data['current_player_index']]
        player_mention = format_player_mention(last_active_player)
        winning_message = f"🎉 **{player_mention} победил(а)!** Поздравляем!"
    else:
        winning_message = "Игра была остановлена до начала или в ней не было активных игроков."

    del active_words_games[chat_id]
    save_words_games(active_words_games)  # Сохраняем состояние

    await client.send_message(
        event.chat_id, 
        f"**✅ Игра 'Слова' с уникальным ID: `{game_id}` - завершена!**\n{winning_message}"
    )
    print(f"DEBUG: Game {game_id} stopped in chat {chat_id}. Winner declared: {winning_message}")


async def leave_words_game(event, client):
    """Позволяет игроку выйти из активной игры 'Слова'."""
    chat_id = str(event.chat_id)
    player_id = event.sender_id
    player_name = event.sender.first_name

    print(f"DEBUG: .слвыйти received in chat {chat_id} by {player_name} ({player_id}).")

    if chat_id not in active_words_games:
        await client.send_message(event.chat_id, "🤷 В этом чате нет активной игры 'Слова', из которой можно выйти.")
        return

    game_data = active_words_games[chat_id]

    initial_player_count = len(game_data['players'])
    
    # Remove the player who left
    game_data['players'] = [p for p in game_data['players'] if p['id'] != player_id]

    if len(game_data['players']) == initial_player_count:
        await client.send_message(event.chat_id, "🚫 Вы не участвуете в этой игре.")
        return

    # Use the new helper for the leaving player
    leaving_player_mention = format_player_mention({'id': player_id, 'name': player_name})

    # Check player count *after* removing the player
    if len(game_data['players']) == 1 and game_data['state'] == 'active':
        remaining_player = game_data['players'][0]
        game_id = game_data['game_id']
        
        del active_words_games[chat_id]
        save_words_games(active_words_games) # Save state before ending the game
        
        # Use the new helper for the remaining player
        remaining_player_mention = format_player_mention(remaining_player)
        
        await client.send_message(
            event.chat_id,
            f"✅ {leaving_player_mention} вышел из игры.\n"
            f"🎉 Поздравляем, {remaining_player_mention}! Вы единственный оставшийся игрок и **вы выиграли** игру 'Слова' с уникальным ID: `{game_id}`!"
        )
        print(f"DEBUG: Player {player_name} left game {game_id} in chat {chat_id}. Player {remaining_player['name']} won.")
        return
    
    elif len(game_data['players']) < 2 and game_data['state'] == 'active': # This handles 0 players or if it becomes 0 after this
        organizer_name = game_data.get('organizer_name', 'Организатор') # Fallback in case organizer_name is missing
        organizer_id = game_data.get('organizer_id', 'Неизвестно') # Fallback
        game_id = game_data['game_id']
        
        del active_words_games[chat_id]
        save_words_games(active_words_games) # Save state before ending the game
        
        await client.send_message(
            event.chat_id,
            f"✅ {leaving_player_mention} вышел из игры. "
            f"ℹ️ Недостаточно игроков для продолжения, игра с ID: `{game_id}` завершена."
        )
        print(f"DEBUG: Player {player_name} left game {game_id} in chat {chat_id}. Game ended due to insufficient players.")
        return
    
    # If the current player left, move to the next player
    if game_data['state'] == 'active' and game_data['players']: # Ensure there are still players
        # Adjust current_player_index if the removed player was the current one
        # The modulo operation handles wrapping around to the start of the list
        game_data['current_player_index'] = game_data['current_player_index'] % len(game_data['players'])
        next_player = game_data['players'][game_data['current_player_index']]
        
        # Use the new helper for the next player
        next_player_mention = format_player_mention(next_player)

        await client.send_message(
            event.chat_id,
            f"✅ {leaving_player_mention} вышел из игры.\n"
            f"📣 Теперь ход: {next_player_mention} на букву **{game_data['last_word'][-1].upper()}**."
        )
    else: # If game is not active or no players left (handled by previous block but good for safety)
        await client.send_message(event.chat_id, f"{leaving_player_mention} вышел из игры.")

    save_words_games(active_words_games) # Save state
    print(f"DEBUG: Player {player_name} left game {game_data.get('game_id', 'N/A')} in chat {chat_id}. Game continues.")

from telethon import events

async def multicolor_heart_handler(event, client):
    """
    Команда .разноцветноесердце — рисует сердце, которое постепенно заполняется разными цветами.
    """
    outline = "🤍"
    heart_symbol = "X"
    fill_colors = ["❤️", "💙", "💚", "💜", "🧡", "💛", "🖤", "🤎", "💗"]

    heart_template = [
        "  XX   XX  ",
        " XXXX XXXX ",
        "XXXXXXXXXXX",
        "XXXXXXXXXXX",
        " XXXXXXXXX ",
        "  XXXXXXX  ",
        "   XXXXX   ",
        "    XXX    ",
        "     X    ",
    ]

    height = len(heart_template)
    width = max(len(row) for row in heart_template)

    grid = [[outline for _ in range(width)] for _ in range(height)]
    coords = []

    for r in range(height):
        for c in range(len(heart_template[r])):
            if heart_template[r][c] == heart_symbol:
                coords.append((r, c))

    random.shuffle(coords)

    def render():
        return "\n".join("".join(row) for row in grid)

    msg = await event.respond(render())

    # Количество "пикселей", заполняемых за один раз
    batch_size = 10 
    
    for i in range(0, len(coords), batch_size):
        # Заполняем порцию "пикселей"
        for r, c in coords[i:i + batch_size]:
            grid[r][c] = random.choice(fill_colors)
        
        try:
            await msg.edit(render())
        except Exception:
            # Обработка исключений, если сообщение не может быть изменено
            break
        await asyncio.sleep(0.05)  # скорость заливки

    await msg.edit(render() + "\n\n🌈 Сердце готово!")

# Пример регистрации хэндлера, если вы используете Telethon:
# client.on(events.NewMessage(pattern=r'\.разноцветноесердце'))(multicolor_heart_handler)



async def multicolor_heart_generator(from_user: str, to_user: str, event) -> None:
    """
    Генерирует и отправляет анимированное разноцветное сердце с информацией об отправителе и получателе.
    """
    outline = "🤍"
    heart_symbol = "X"
    fill_colors = ["❤️", "💙", "💚", "💜", "🧡", "💛", "🖤", "🤎", "💗"]

    heart_template = [
        "  XX   XX  ",
        " XXXX XXXX ",
        "XXXXXXXXXXX",
        "XXXXXXXXXXX",
        " XXXXXXXXX ",
        "  XXXXXXX  ",
        "   XXXXX   ",
        "    XXX    ",
        "     X     ",
    ]

    height = len(heart_template)
    width = max(len(row) for row in heart_template)

    grid = [[outline for _ in range(width)] for _ in range(height)]
    coords = []

    for r in range(height):
        for c in range(len(heart_template[r])):
            if heart_template[r][c] == heart_symbol:
                coords.append((r, c))

    random.shuffle(coords)

    def render(current_text=""):
        return "\n".join("".join(row) for row in grid) + current_text

    msg = await event.respond(render())

    # Количество "пикселей", заполняемых за один раз
    batch_size = 10 
    
    for i in range(0, len(coords), batch_size):
        # Заполняем порцию "пикселей"
        for r, c in coords[i:i + batch_size]:
            grid[r][c] = random.choice(fill_colors)
        
        try:
            await msg.edit(render())
        except MessageNotModifiedError:
            # Это нормально, если сообщение не изменилось достаточно, чтобы Telegram его обновил.
            pass
        except Exception as e:
            print(f"Ошибка при редактировании сообщения сердца: {e}")
            break # Прерываем, если не можем редактировать
        await asyncio.sleep(0.05)   # скорость заливки

    final_message = f"\n\nОт: {from_user}\nКому: {to_user}"
    await msg.edit(render(final_message))

async def send_heart_command(event):
            sender_id = event.sender_id
            chat_id = event.chat_id
            current_time = time.time()

            if sender_id in last_message_times and (current_time - last_message_times[sender_id] < COMMAND_COOLDOWN):
                await event.reply(f"Подождите {COMMAND_COOLDOWN - (current_time - last_message_times[sender_id]):.1f} секунд перед использованием команды снова.")
                return
            last_message_times[sender_id] = current_time

            try:
                target_username_or_id = event.pattern_match.group(1).strip()
                
                # Получаем информацию об отправителе
                sender_user = await event.get_sender()
                from_name = sender_user.first_name if sender_user.first_name else "Неизвестный"
                if sender_user.username:
                    from_name += f" (@{sender_user.username})"
                
                # Пытаемся получить пользователя по юзернейму или ID
                target_user = None
                try:
                    target_user = await client.get_entity(target_username_or_id)
                except UsernameInvalidError:
                    await event.reply("Неверный юзернейм или ID пользователя.")
                    return
                except ValueError:
                     # Если не удалось преобразовать в int для ID
                    await event.reply("Неверный юзернейм или ID пользователя.")
                    return
                except Exception as e:
                    print(f"Ошибка при получении сущности пользователя: {e}")
                    await event.reply("Не удалось найти указанного пользователя. Убедитесь, что это действительный юзернейм или ID.")
                    return

                if isinstance(target_user, User):
                    to_name = target_user.first_name if target_user.first_name else "Неизвестный"
                    if target_user.username:
                        to_name += f" (@{target_user.username})"
                else:
                    # Если target_user не является User (например, это Channel или Chat)
                    await event.reply("Можно отправлять сердца только пользователям, а не чатам или каналам.")
                    return

                # Удаляем команду, чтобы не засорять чат до начала анимации
                await event.delete() 

                # Запускаем генератор разноцветного сердца
                await multicolor_heart_generator(from_name, to_name, event)

            except Exception as e:
                print(f"Ошибка в команде .отправитьсердце: {e}")
                await event.reply("Произошла ошибка при выполнении команды.")






async def userbots_info_handler(event, client):
    """
    Обрабатывает команду .юзерботы — показывает информацию о всех подключённых аккаунтах с нумерацией.
    """
    responses = []
    for idx, acc in enumerate(clients, start=1):
        try:
            me = await acc.get_me()
            username = f"@{me.username}" if me.username else "Нет юзернейма"
            full_name = f"{me.first_name or ''} {me.last_name or ''}".strip() or "Нет имени"
            user_id = me.id
            phone = getattr(me, 'phone', 'Скрыт')
            is_premium = "✅" if getattr(me, 'premium', False) else "❎"
            lang_code = getattr(me, 'lang_code', 'Неизвестно')

            responses.append(
                f"{idx}. 🤖 **Аккаунт:** `{user_id}`\n"
                f"   • Имя: `{full_name}`\n"
                f"   • Юзернейм: {username}\n"
                f"   • Телефон: `+{phone}`\n"
                f"   • Premium: {is_premium}\n"
                f"   • Язык: `{lang_code}`\n"
            )
        except Exception as e:
            responses.append(f"{idx}. ⚠️ Ошибка при получении данных: {e}")

    full_message = "📱 **Подключённые юзерботы:**\n\n" + "\n".join(responses)
    await event.edit(full_message)



async def pin_message_handler(event, client): # Добавлен client
    if not event.reply_to_msg_id:
        await event.edit("`Ответьте на сообщение, которое нужно закрепить.`")
        return

    try:
        chat = await event.get_chat()
        
        # Проверяем, являемся ли мы администратором чата (необходимо для закрепления)
        if isinstance(chat, (Channel, Chat)): # Работает для супергрупп/каналов и обычных групп
            me_in_chat = await client.get_permissions(chat, await client.get_me())
            if me_in_chat.pin_messages:
                replied_message = await event.get_reply_message()
                if replied_message:
                    await client.pin_message(chat, replied_message, notify=False) # notify=False чтобы не уведомлять всех
                    await event.edit("`Сообщение успешно закреплено.`")
                    await asyncio.sleep(2) # Даем время на прочтение
                    await event.delete()
                else:
                    await event.edit("`Не удалось найти сообщение для закрепления.`")
            else:
                await event.edit("`У меня нет прав для закрепления сообщений в этом чате/канале.`")
        else: # Приватный чат или неизвестный тип
            await event.edit("`Эту команду можно использовать только в группах или каналах.`")

    except ChatAdminRequiredError:
        await event.edit("`У меня нет прав администратора для закрепления сообщений в этом чате. Убедитесь, что я являюсь администратором с правом 'Закреплять сообщения'.`")
    except MessageIdInvalidError:
        await event.edit("`Не удалось найти сообщение для закрепления.`")
    except Exception as e:
        print(f"Ошибка при закреплении сообщения: {e}")
        await event.edit(f"`Произошла ошибка при закреплении сообщения: {type(e).__name__}: {e}`")

async def dice_roll_handler(event, client): # Добавлен client
    await event.edit("✅ Бросаю кубик...")
    await asyncio.sleep(1) # Задержка для эффекта
    result = random.randint(1, 6)
    await event.edit(f"🎲 Выпало: {result}")

async def colorful_heart_handler(event, client):
    """
    Команда .цветасердца — рисует сердце в рамке, заливка которого меняется цветами.
    """
    outline = "🤍"  # Рамка
    fill_colors = ["❤️", "💙", "💚", "💜", "🧡", "💛", "🖤"]

    # Шаблон сердца (X — заливка, остальное — пустота)
    heart_template = [
        "  XX   XX  ",
        " XXXX XXXX ",
        "XXXXXXXXXXX",
        "XXXXXXXXXXX",
        " XXXXXXXXX ",
        "  XXXXXXX  ",
        "   XXXXX   ",
        "    XXX    ",
        "     X     ",
    ]

    # Размеры сетки
    height = len(heart_template)
    width = max(len(row) for row in heart_template)

    def render(fill_char):
        grid = []
        for r in range(height):
            row = ""
            for c in range(width):
                if c < len(heart_template[r]) and heart_template[r][c] == "X":
                    row += fill_char
                else:
                    row += outline
            grid.append(row)
        return "\n".join(grid)

    msg = await event.respond("🔁 Рисую сердце...")

    for color in fill_colors:
        await asyncio.sleep(0.6)
        try:
            await msg.edit(render(color))
        except Exception:
            break

    await msg.edit(render(fill_colors[-1]) + "\n\n💖 Цветное сердце готово!")



async def keep_online(client, session_name): # <-- Добавляем session_name как аргумент
    """
    Периодически отправляет 'read acknowledge', чтобы поддерживать статус 'онлайн',
    если флаг online_status_enabled для данного клиента установлен в True.
    """
    print(f"[{session_name}] Задача поддержания онлайна запущена.")

    while True:
        if online_status_enabled.get(session_name, False):
            try:
                # В этой части ничего не меняем, просто даем asyncio работать
                pass

            except FloodWaitError as e:
                print(f"[{session_name}] FloodWait во время поддержания онлайна: {e.seconds} секунд.")
                await asyncio.sleep(e.seconds + 5)
            except asyncio.CancelledError:
                print(f"[{session_name}] Задача поддержания онлайна отменена.")
                break
            except Exception as e:
                print(f"[{session_name}] Ошибка при поддержании онлайна: {e}")
                
        await asyncio.sleep(60)

# --- Команды для управления вечным онлайном ---
async def enable_online_handler(event, client, session_name): # <--- ДОБАВЬТЕ 'session_name' сюда
    # --- Проверка отправителя (чтобы команду обработал только тот бот, который ее отправил) ---
    me = await event.client.get_me()
    my_id = me.id
    sender_id = event.sender_id

    if sender_id != my_id:
        return
    # --- Конец проверки отправителя ---

    online_status_enabled[session_name] = True
    print(f"[{session_name}] Вечный онлайн включен.")
    # Убедитесь, что здесь используете client.send_message, а не event.edit
    await event.delete() # Удаляем команду
    await client.send_message(event.chat_id, "✅ Вечный онлайн **включен**.")


async def disable_online_handler(event, client, session_name): # <--- ДОБАВЬТЕ 'session_name' сюда
    # --- Проверка отправителя ---
    me = await event.client.get_me()
    my_id = me.id
    sender_id = event.sender_id

    if sender_id != my_id:
        return
    # --- Конец проверки отправителя ---

    online_status_enabled[session_name] = False
    print(f"[{session_name}] Вечный онлайн выключен.")
    # Убедитесь, что здесь используете client.send_message, а не event.edit
    await event.delete() # Удаляем команду
    await client.send_message(event.chat_id, "❌ Вечный онлайн **выключен**.")
    
# Убедитесь, что эта функция определена выше в вашем коде,
# например, рядом с load_nicknames и save_nicknames.
async def get_user_display_name(user_id, chat_id, client):
    """
    Возвращает никнейм пользователя, если установлен для ЭТОГО ЧАТА (для userbot'а),
    иначе возвращает его имя пользователя (@username) или полное имя,
    форматируя его как Markdown-ссылку на профиль.
    """
    global chat_nicknames

    try:
        current_chat_entity = await client.get_entity(chat_id)
        chat_id_key = await _get_normalized_chat_id(current_chat_entity)
    except Exception:
        # Если не можем получить entity чата, возможно, это личный чат, где chat_id == user_id
        # или просто сбой. В этом случае, попробуем использовать сам chat_id как ключ.
        chat_id_key = str(chat_id) 

    user_id_int = int(user_id)
    me = await client.get_me()

    if user_id_int == me.id:
        if chat_id_key in chat_nicknames:
            display_name = chat_nicknames[chat_id_key]
            return f"[{display_name}](tg://user?id={user_id_int})"
        else:
            pass # Проходим к обычной логике получения имени ниже

    try:
        user_entity = await client.get_entity(user_id_int)
        
        display_name = user_entity.username
        if not display_name:
            display_name = f"{user_entity.first_name or ''} {user_entity.last_name or ''}".strip()
            if not display_name:
                display_name = "Неизвестный пользователь"

        return f"[{display_name}](tg://user?id={user_entity.id})"
    except Exception as e:
        print(f"Ошибка при получении информации о пользователе {user_id_int}: {e}")
        return f"[пользователь_{user_id_int}](tg://user?id={user_id_int})"

    
# --- Ваш обновленный rp_command_handler ---

async def rp_command_handler(event, client, action_templates):
    # --- Проверка отправителя (чтобы команду обработал только тот бот, который ее отправил) ---
    me = await event.client.get_me()
    my_id = me.id
    sender_id = event.sender_id

    if sender_id != my_id:
        return # Если сообщение отправлено не нашим ботом, выходим
    # --- Конец проверки отправителя ---

    args = event.raw_text.split(maxsplit=1)
    command = args[0].lower()
    action_name = command[1:] # Например, 'обнять' из '.обнять'
    
    chat = await event.get_chat()
    chat_id = chat.id # Используем event.chat.id для передачи в get_user_display_name

    target_user_obj = None
    
    sender_user_obj = await event.get_sender()
    sender_name_formatted = await get_user_display_name(sender_user_obj.id, chat_id, client)

    target_name_formatted = ""
    if len(args) > 1:
        target_input = args[1].strip()
        if target_input.startswith('@'):
            try:
                target_user_obj = await client.get_entity(target_input)
            except (UsernameInvalidError, ValueError):
                pass
        elif event.is_reply:
            reply_msg = await event.get_reply_message()
            if reply_msg and reply_msg.sender:
                target_user_obj = reply_msg.sender
        
        if target_user_obj:
            target_name_formatted = await get_user_display_name(target_user_obj.id, chat_id, client)
        elif target_input:
            target_name_formatted = f"**{target_input}**"
    
    templates = action_templates.get(action_name)
    if not templates:
        await event.edit(f"Ошибка: Не найдены шаблоны для RP-команды `{command}`.")
        return 

    chosen_template = random.choice(templates)

    message_text = ""
    if target_name_formatted:
        message_text = chosen_template.format(sender=sender_name_formatted, target=target_name_formatted)
    else:
        if '{target}' in chosen_template:
            # Если шаблон требует цель, но ее нет, используем отправителя как цель (действие над собой)
            message_text = chosen_template.format(sender=sender_name_formatted, target=sender_name_formatted)
        else:
            # Если шаблон не требует отдельной цели
            message_text = chosen_template.format(sender=sender_name_formatted)

    # --- НОВАЯ ЛОГИКА ДЛЯ ОТПРАВКИ GIF ---
    gif_urls = RP_ACTION_GIFS.get(action_name)
    if gif_urls:
        chosen_gif_url = random.choice(gif_urls)
        try:
            # Отправляем GIF с отформатированным текстом как подписью
            await client.send_file(event.chat_id, chosen_gif_url, caption=message_text, parse_mode='md')
        except Exception as e:
            print(f"Ошибка при отправке GIF для команды '{action_name}': {e}")
            # В случае ошибки отправки GIF, просто отправляем текст
            await client.send_message(event.chat_id, message_text, parse_mode='md')
    else:
        # Если для действия нет GIF-изображений, отправляем только текст
        await event.delete() # Удаляем команду
        await client.send_message(event.chat_id, message_text, parse_mode='md')

async def _get_normalized_chat_id(entity):
    """
    Возвращает нормализованный ID чата (строку), который будет использоваться как ключ.
    Для групп/каналов это обычно отрицательный ID.
    Для личных чатов - ID пользователя.
    """
    if isinstance(entity, Channel):
        return str(-1000000000000 + entity.id) # Стандартный способ Telethon для Channel ID
    elif isinstance(entity, Chat):
        return str(-entity.id) # Для обычных групп (Chat)
    else: # Для личных чатов (User)
        return str(entity.id)

async def quote_of_the_day_handler(event, client): # Добавлен client
    await event.edit("`Получаю цитату дня...`")
    try:
        async with httpx.AsyncClient() as http_client:
            response = await http_client.get("https://quotes.rest/qod?language=ru") # Запрос цитаты на русском
            response.raise_for_status() # Вызовет исключение для ошибок HTTP (4xx или 5xx)
            data = response.json()
            
            if data and 'contents' in data and 'quotes' in data['contents'] and data['contents']['quotes']:
                quote = data['contents']['quotes'][0]
                text = quote.get('quote')
                author = quote.get('author')
                
                if text and author:
                    formatted_quote = f"**Цитата дня:**\n\n_«{text}»_\n\n**— {author}**"
                    await event.edit(formatted_quote)
                else:
                    await event.edit("`Не удалось получить цитату. Отсутствует текст или автор.`")
            else:
                await event.edit("`Не удалось получить цитату. Неверный формат ответа API.`")

    except httpx.HTTPStatusError as e:
        await event.edit(f"❎ Временно недоступно.")
    except httpx.RequestError as e:
        await event.edit(f"`Ошибка сети при получении цитаты: {e}.`")
    except json.JSONDecodeError:
        await event.edit("`Ошибка при обработке ответа API (неверный JSON).`")
    except Exception as e:
        print(f"Ошибка при получении цитаты дня: {e}")
        await event.edit(f"`Произошла непредвиденная ошибка: {type(e).__name__}: {e}`")

async def probability_handler(event, client): # Добавлен client
    # Изменен паттерн регистрации для захвата необязательного аргумента
    question_match = event.pattern_match.group(1)
    question = question_match.strip() if question_match else ""
    
    # Получаем информацию о пользователе, который отправил команду
    sender = await event.get_sender()
    sender_mention = f"@{sender.username}" if sender.username else sender.first_name

    probability = random.randint(0, 100)
    
    response_phrases = [
        f"{sender_mention}, я думаю, что вероятность - {probability}%\n❓Вопрос: {question}",
        f"{sender_mention}, мои вычисления показывают: {probability}%\n❓Вопрос: {question}",
        f"По моим данным, {sender_mention}, вероятность составляет {probability}%\n❓Вопрос: {question}",
        f"Хм, {sender_mention}... {probability}%\n❓Вопрос: {question}",
    ]
    
    if question: # Если был задан вопрос, добавляем фразу с вопросом
        response_phrases.append(f"Вероятность '{question}' по моей оценке, {sender_mention}, равна {probability}%")
    
    await event.edit(random.choice(response_phrases))

async def love2_handler(event, client):
    """
    Новая анимация сердечка.
    """
    hearts = ["💓", "💗", "💖", "💘", "💕", "💞", "❤️", "❤️‍🔥"]
    msg = await event.edit("❤️")
    for i in range(3):
        for h in hearts:
            await msg.edit(h)
            await asyncio.sleep(0.3)
    await msg.edit("💘 Сердечки отправлены!")

LOG_FILE_PATH = "usage_logs.txt"

async def log_command_usage(command: str, user_id: int, username: str = None):
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now()} — {command} от {username or user_id}\n")

async def send_logs_to_favorites(event, client):
    try:
        if not os.path.exists(LOG_FILE_PATH):
            await event.edit("❌ Лог-файл пока не создан.")
            return

        await event.edit("📤 Отправляю лог в Избранное...")
        await client.send_file("me", LOG_FILE_PATH, caption="📄 Лог использования команд")
        await event.delete()

    except Exception as e:
        await event.edit(f"❌ Ошибка отправки логов: {e}")

async def log_command_usage(command: str, user_id: int, username: str = None):
    with open(LOG_FILE_PATH, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} — {command} от @{username or user_id}\n")

async def set_nickname(event):
    global chat_nicknames
    
    chat_entity = await event.get_chat() # Получаем объект чата
    chat_id_key = await _get_normalized_chat_id(chat_entity) # <-- Используем нормализованный ID для ключа

    args = event.pattern_match.group(1)

    if args:
        if args.lower() == 'сброс':
            if chat_id_key in chat_nicknames: # <-- Используем нормализованный ID
                del chat_nicknames[chat_id_key]
                save_nicknames(chat_nicknames)
                await event.edit("✅ Никнейм для этой беседы сброшен.")
            else:
                await event.edit("ℹ️ Никнейм для этой беседы не был установлен.")
        else:
            new_nickname = args.strip()
            chat_nicknames[chat_id_key] = new_nickname # <-- Используем нормализованный ID
            save_nicknames(chat_nicknames)
            await event.edit(f"✅ Никнейм для этой беседы установлен: **{new_nickname}**")
    else:
        if chat_id_key in chat_nicknames: # <-- Используем нормализованный ID
            current_nickname = chat_nicknames[chat_id_key]
            await event.edit(f"ℹ️ Текущий никнейм для этой беседы: **{current_nickname}**")
        else:
            await event.edit("🚫 Никнейм для этой беседы не установлен. Используйте .ник [ваш_ник], чтобы установить его.")


async def list_nicknames(event):
    global chat_nicknames
    chat_entity = await event.get_chat()
    chat_id_key = await _get_normalized_chat_id(chat_entity) # Нормализованный ID

    message = "ℹ️ **Список никнеймов для этой беседы:**\n\n"
    
    # 1. Получаем ID нашего бота
    me = await event.client.get_me()
    my_user_id_str = str(me.id)

    # 2. Проверяем, установлен ли для ЭТОГО ЧАТА никнейм для нашего бота
    if chat_id_key in chat_nicknames:
        current_nickname = chat_nicknames[chat_id_key]
        message += f"🗺️ Твой никнейм в этом чате: **{current_nickname}**\n"
        # Для полноты, можем добавить и его стандартное имя/юзернейм, если нужно
        display_name_default = me.username if me.username else me.first_name
        message += f"(Юзернейм: @{display_name_default if me.username else display_name_default})\n"
    else:
        message += "🤷 Твой никнейм для этой беседы: не установлен.\n"

    # !!! Здесь, вероятно, у вас добавлена логика, которая проходит по всем участникам чата
    # и пытается вывести их имена/ники. Эта часть кода НЕ была мной предоставлена
    # и приводит к выводу "1. [ываплдварпо]..." и т.д.
    # Если вы хотите только свой ник, УДАЛИТЕ ЭТУ ЛОГИКУ.

    await event.edit(message)

async def start_duel(event, client):
    chat_id = str(event.chat_id)
    sender = await event.get_sender()
    sender_id = sender.id
    sender_name = sender.first_name

    if chat_id in active_duels:
        duel = active_duels[chat_id]
        if isinstance(duel, DuelGame):
            await event.reply("⚔ В этом чате уже идёт бой.")
            return
        if duel['p2'] is None:
            duel['p2'] = PlayerState(id=sender_id, name=sender_name)
            game = DuelGame(duel['p1'], duel['p2'], current_turn=duel['p1'].id, chat_id=event.chat_id)
            msg = await client.send_message(
    event.chat_id,
    render_duel(game),
    buttons=[
        [
            Button.inline("🗡 Атаковать", b"attack"),
            Button.inline("🛡 Защититься", b"defend"),
        ],
        [
            Button.inline("💥 Супер-удар", b"super"),
            Button.inline("🏳 Сдаться", b"giveup"),
        ]
    ]
)

            game.message_id = msg.id
            active_duels[chat_id] = game
        else:
            await event.reply("❌ Уже идет бой между двумя игроками.")
    else:
        active_duels[chat_id] = {
            'p1': PlayerState(id=sender_id, name=sender_name),
            'p2': None
        }
        await event.reply("⚔ Ожидание второго игрока... Напиши `.битва`, чтобы вступить.")

async def duel_button_callback(event, client):
    chat_id = str(event.chat_id)
    user_id = event.sender_id
    data = event.data.decode("utf-8")

    if chat_id not in active_duels or not isinstance(active_duels[chat_id], DuelGame):
        await event.answer("Бой не найден", alert=True)
        return

    game = active_duels[chat_id]
    if user_id != game.current_turn:
        await event.answer("❌ Не ваш ход!", alert=True)
        return

    msg = game.make_move(user_id, data)

    if game.is_over():
        winner = game.get_winner()
        result = f"\n\n🏆 Победил: **{winner.name}**!" if winner else "\n\n🤝 Ничья!"
        await event.edit(render_duel(game) + "\n\n" + msg + result, buttons=None)
        del active_duels[chat_id]
        return

    game.current_turn = game.get_opponent(user_id).id

    await event.edit(render_duel(game) + "\n\n" + msg, buttons=[
        [
            Button.inline("🗡 Атаковать", b"attack"),
            Button.inline("🛡 Защититься", b"defend"),
        ],
        [
            Button.inline("💥 Супер-удар", b"super"),
            Button.inline("🏳 Сдаться", b"giveup"),
        ]
    ])

# --- Команда .спам ---
async def spam_command_handler(event, client, session_name):
    """
    Обработчик команды .спам [сообщение] [количество].
    Спамит указанным сообщением заданное количество раз.
    """
    match = re.match(r'\.спам (.+) (\d+)', event.text)
    if match:
        message_to_spam = match.group(1)
        count = int(match.group(2))
        chat_id = event.chat_id if event.chat_id else event.peer_id

        print(f"[{session_name}] Получена команда .спам: '{message_to_spam}' {count} раз в чате {chat_id}")

        if count <= 0:
            await event.reply("Количество спама должно быть положительным числом.")
            print(f"[{session_name}] Ошибка: Количество спама должно быть положительным числом.")
            return

        if count > 100:
            await event.reply("Максимальное количество спама за раз - 100.")
            print(f"[{session_name}] Ошибка: Превышено максимальное количество спама (100).")
            return


        # --- ОТПРАВКА СООБЩЕНИЯ ПЕРЕД НАЧАЛОМ СПАМА ---
        try:
            # Используем форматированный текст для сообщения в чат
            await client.send_message(event.peer_id, f'✅ Начинаю спамить сообщением: "`{message_to_spam}`"')
            print(f"[{session_name}] Отправлено уведомление о начале спама в чат {chat_id}.")
            await asyncio.sleep(0.3) # Небольшая задержка после уведомления
        except Exception as e:
            print(f"[{session_name}] Ошибка при отправке уведомления о начале спама: {e}")
            # Не прерываем выполнение, если не удалось отправить уведомление, просто логируем ошибку

        successful_sends = 0
        for i in range(count):
            try:
                await client.send_message(event.peer_id, message_to_spam)
                successful_sends += 1
                print(f"[{session_name}] Отправлено сообщение {successful_sends}/{count}: '{message_to_spam}' в чат {chat_id}")
                await asyncio.sleep(0.15) # Задержка 0.15 секунды между сообщениями
            except FloodWaitError as e:
                print(f"[{session_name}] Ошибка флуд-контроля при спаме: {e.seconds} секунд. Ожидание...")
                await asyncio.sleep(e.seconds + 0.15) # Добавляем 0.15 к времени ожидания
                try:
                    await client.send_message(event.peer_id, message_to_spam)
                    successful_sends += 1
                    print(f"[{session_name}] Повторно отправлено сообщение {successful_sends}/{count}: '{message_to_spam}' после FloodWait.")
                except Exception as retry_e:
                    print(f"[{session_name}] Ошибка при повторной отправке после FloodWait: {retry_e}. Спам остановлен.")
                    await event.reply(f"Ошибка при повторной отправке после FloodWait: {retry_e}. Спам остановлен.")
                    break
            except PeerFloodError:
                print(f"[{session_name}] Ошибка PeerFloodError при спаме. Прекращение спама.")
                await event.reply("Произошла ошибка флуда. Спам остановлен.")
                break
            except Exception as e:
                print(f"[{session_name}] Неизвестная ошибка при спаме: {e}")
                await event.reply(f"Произошла ошибка при спаме: {e}")
                break
        
        if successful_sends == count:
            print(f"[{session_name}] **Спам сообщением '{message_to_spam}' успешно завершен ({successful_sends} из {count} раз) в чате {chat_id}.**")
        else:
            print(f"[{session_name}] **Спам сообщением '{message_to_spam}' завершен с ошибками ({successful_sends} из {count} раз) в чате {chat_id}.**")
 
async def handle_autoreply_command(event):
    args = event.pattern_match.group(1).strip()
    command_parts = args.split(' ', 1)

    if len(command_parts) == 1 and command_parts[0].lower() == 'list':
        if not autoreplies:
            await event.edit('📭 Список автоответов пуст.')
            return

        response = '📭 **Ваши автоответы:**\n\n'
        for trigger, reply_text in autoreplies.items():
            response += f'• Триггер: `{trigger}`\n• Ответ: `{reply_text}`\n\n'
        await event.edit(response)
        return

    if command_parts[0].lower() == 'remove':
        if len(command_parts) < 2:
            await event.edit('❌ Укажите триггер для удаления. Пример: `.автоответ remove привет`')
            return
        trigger_to_remove = command_parts[1].lower()
        if trigger_to_remove in autoreplies:
            del autoreplies[trigger_to_remove]
            save_autoreplies()
            await event.edit(f'✅ Автоответ на `{trigger_to_remove}` удален.')
        else:
            await event.edit(f'🤷‍♂️ Автоответа на `{trigger_to_remove}` не найдено.')
        return

    if len(command_parts) < 2:
        await event.edit('❌ Неверный формат команды. Используйте: `.автоответ [триггер][ответ]` или `.автоответ remove [триггер]` или `.автоответ list`')
        return

    trigger = command_parts[0].lower()
    reply_text = command_parts[1]

    autoreplies[trigger] = reply_text
    save_autoreplies()
    await event.edit(f'✅ Настроен автоответ: если кто-то скажет `{trigger}`, бот ответит `{reply_text}`.')

async def check_for_autoreply(event):
    # Используем глобальную переменную MY_USER_ID
    global MY_USER_ID # Объявляем, что будем использовать глобальную переменную

    if event.raw_text:
        message_text = event.raw_text.lower()
        
        if MY_USER_ID is None:
            # Если MY_USER_ID ещё не установлен (например, бот только запускается
            # и первое сообщение пришло до завершения main), пропустим проверку.
            # Это должно быть очень редко, если main() завершается успешно.
            return

        # Теперь MY_USER_ID точно не None, можно безопасно сравнивать
        if event.from_id == MY_USER_ID:
            # Если отправитель - сам юзербот, игнорируем
            return

        for trigger, reply_text in autoreplies.items():
            if trigger in message_text:
                await event.reply(reply_text)
                return

async def handle_google_command(event):
    """
    Обрабатывает команду .google для поиска в Google.
    Пример: .google что такое телеграм
    """
    query = event.pattern_match.group(1).strip()
    await event.edit(f'🔍 Ищу в Google: `{query}`...')

    try:
        # Это очень упрощенный пример. Для реального Google поиска
        # нужен Google Custom Search API или парсинг.
        # Здесь мы просто создаем прямую ссылку на поиск Google.
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        response_text = (
            f"Вот что я нашел по запросу `{query}`:\n\n"
            f"🔗 [Открыть результаты поиска в Google]({search_url})"
        )
        await event.edit(response_text, link_preview=True) # link_preview=True для отображения предпросмотра ссылки

    except Exception as e:
        await event.edit(f'❌ Ошибка при поиске: {e}')

import random

# Assuming RPS_CHOICES and RPS_RULES are defined elsewhere in your code like this:

async def handle_rps_command(event):
    """
    Обрабатывает команду .rps для игры Камень, Ножницы, Бумага.
    Пример: .rps камень
    """
    player_choice_raw = event.pattern_match.group(1).strip().lower()

    # Проверяем, что выбор пользователя корректен
    if player_choice_raw not in RPS_CHOICES:
        await event.reply('❌ Неверный ход. Выберите `камень`, `ножницы` или `бумага`.')
        return

    player_choice = player_choice_raw
    player_emoji = RPS_CHOICES[player_choice]

    # Бот делает случайный выбор
    bot_choice = random.choice(list(RPS_CHOICES.keys()))
    bot_emoji = RPS_CHOICES[bot_choice]

    result_text = f"Твой ход: {player_emoji} **{player_choice.capitalize()}**\n"
    result_text += f"Мой ход: {bot_emoji} **{bot_choice.capitalize()}**\n\n"

    # Определяем победителя
    if player_choice == bot_choice:
        result_text += "🤝 **Ничья!**"
    # Если ход игрока побеждает ход бота
    elif RPS_RULES[player_choice] == bot_choice:  # Твой ход побеждает мой
        result_text += "🎉 **Ты победил!**"
    # Если ход бота побеждает ход игрока
    elif RPS_RULES[bot_choice] == player_choice:  # Мой ход побеждает твой
        result_text += "🤖 **Я победил!**"
    # Это "else" на самом деле не должно быть достигнуто, если правила и выборы корректны
    else:
        result_text += "🤔 Кажется, что-то пошло не так... Ничья?"  # На всякий случай

    await event.reply(result_text)

from telethon import events

async def ignore_user_handler(event, client):
    """
    .+игнор [юзернейм/ID] или в ответ на сообщение - добавляет пользователя в список игнора.
    Бот не будет обрабатывать сообщения от игнорируемых пользователей.
    """
    target_user_id = None
    user_info = None

    # Попытка получить юзера из аргумента
    parts = event.text.split(maxsplit=1)
    if len(parts) > 1:
        arg = parts[1].strip()
        try:
            # Попробуем разобрать как числовой ID
            target_user_id = int(arg)
            # Если это числовой ID, попытаемся получить информацию о пользователе
            try:
                user_entity = await client.get_entity(target_user_id)
                if isinstance(user_entity, User):
                    user_info = user_entity
            except Exception:
                # Если ID не найден или не является пользователем
                pass
        except ValueError:
            # Если это не число, значит, это, вероятно, юзернейм
            if arg.startswith('@'):
                username = arg[1:]
                try:
                    user_entity = await client.get_entity(username)
                    if isinstance(user_entity, User):
                        target_user_id = user_entity.id
                        user_info = user_entity
                except Exception:
                    await event.edit(f"🚫 **Ошибка:** Пользователь `{arg}` не найден или недоступен.")
                    return
            else:
                await event.edit("🚫 **Используйте:** `.+игнор [@юзернейм/ID]` или ответьте на сообщение пользователя.")
                return
    elif event.is_reply:
        # Если команда в ответ на сообщение
        replied_message = await event.get_reply_message()
        if replied_message and replied_message.sender_id:
            target_user_id = replied_message.sender_id
            user_info = replied_message.sender
        else:
            await event.edit("🚫 Не удалось получить информацию об отправителе из отвеченного сообщения.")
            return
    else:
        await event.edit("🚫 **Используйте:** `.+игнор [@юзернейм/ID]` или ответьте на сообщение пользователя.")
        return

    if target_user_id is None:
        await event.edit("🚫 Не удалось определить пользователя для игнорирования.")
        return

    # Проверка, не пытается ли пользователь игнорировать самого себя
    if target_user_id == event.sender_id:
        await event.edit("😅 Вы не можете игнорировать самого себя.")
        return

    if target_user_id in ignored_user_ids:
        await event.edit(f"✅ Пользователь {'@' + user_info.username if user_info and user_info.username else target_user_id} уже в списке игнора.")
    else:
        ignored_user_ids.add(target_user_id)
        save_ignored_users()
        await event.edit(f"✅ Пользователь {'@' + user_info.username if user_info and user_info.username else target_user_id} добавлен в список игнора.")
    
    await asyncio.sleep(3)

# --- Команда .-игнор ---
async def unignore_user_handler(event, client):
    """
    .-игнор [юзернейм/ID] или в ответ на сообщение - удаляет пользователя из списка игнора.
    """
    target_user_id = None
    user_info = None

    # Попытка получить юзера из аргумента
    parts = event.text.split(maxsplit=1)
    if len(parts) > 1:
        arg = parts[1].strip()
        try:
            target_user_id = int(arg)
            try:
                user_entity = await client.get_entity(target_user_id)
                if isinstance(user_entity, User):
                    user_info = user_entity
            except Exception:
                pass
        except ValueError:
            if arg.startswith('@'):
                username = arg[1:]
                try:
                    user_entity = await client.get_entity(username)
                    if isinstance(user_entity, User):
                        target_user_id = user_entity.id
                        user_info = user_entity
                except Exception:
                    await event.edit(f"🚫 **Ошибка:** Пользователь `{arg}` не найден или недоступен.")
                    return
            else:
                await event.edit("🚫 **Используйте:** `.-игнор [@юзернейм/ID]` или ответьте на сообщение пользователя.")
                return
    elif event.is_reply:
        replied_message = await event.get_reply_message()
        if replied_message and replied_message.sender_id:
            target_user_id = replied_message.sender_id
            user_info = replied_message.sender
        else:
            await event.edit("🚫 Не удалось получить информацию об отправителе из отвеченного сообщения.")
            return
    else:
        await event.edit("🚫 **Используйте:** `.-игнор [@юзернейм/ID]` или ответьте на сообщение пользователя.")
        return

    if target_user_id is None:
        await event.edit("🚫 Не удалось определить пользователя для раз-игнорирования.")
        return

    if target_user_id not in ignored_user_ids:
        await event.edit(f"✅ Пользователь {'@' + user_info.username if user_info and user_info.username else target_user_id} не был в списке игнора.")
    else:
        ignored_user_ids.remove(target_user_id)
        save_ignored_users()
        await event.edit(f"✅ Пользователь {'@' + user_info.username if user_info and user_info.username else target_user_id} удален из списка игнора.")
    
    await asyncio.sleep(3)

# REMOVE THIS LINE: @client.on(events.NewMessage(pattern=r'^\.zov(?: (.+))?$', outgoing=True))
async def zov_handler(event, client):
    """
    .zov [сообщение] — упоминает всех пользователей с никнеймами в чате и добавляет сообщение
    """
    parts = event.text.split(maxsplit=1)
    if len(parts) < 2:
        await event.edit("🚫 **Используйте:** .zov [сообщение]")
        return

    user_message = parts[1]
    # Capitalize the first letter of user_message
    user_message = user_message.capitalize() 

    chat = await event.get_chat()
    sender = await event.get_sender()
    sender_username = sender.username

    mentions = []
    try:
        async for member in client.iter_participants(chat):
            if member.username and member.username != sender_username:
                mentions.append(f"@{member.username}")
    except Exception as e:
        await event.edit(
            f"❌ **Ошибка при получении участников:** `{e}`\n"
            "Убедись, что чат не скрывает список участников и бот — админ."
        )
        return

    if not mentions:
        await event.edit("🤷‍♂️ В чате нет пользователей с юзернеймами (кроме вас, если есть).")
        return

    notification_header = f"**‼️ ВАЖНОЕ ОПОВЕЩЕНИЕ ОТ @{sender_username if sender_username else sender.first_name}:**"
    
    if mentions:
        mentions_line = f"{', '.join(mentions)}"
    else:
        mentions_line = ""

    final_message = f"{notification_header}\n{mentions_line}\n\n✅ Оповещение:\n{user_message}."

    try:
        await client.send_message(chat, final_message)
    except Exception as e:
        await event.edit(f"❗ **Ошибка при отправке:** `{e}`")


from bs4 import BeautifulSoup
from urllib.parse import quote_plus

async def lyrics_handler(event, client):
    args = event.raw_text.split(" ", 1)
    if len(args) < 2:
        await event.reply("⛔ Использование: `.текстпесни [название]`")
        return

    query = args[1].strip()
    await event.reply(f"🔍 Ищу текст песни: `{query}`...")

    try:
        # Шаг 1: поиск в Google
        search_query = f"{query} site:genius.com lyrics"
        search_url = f"https://www.google.com/search?q={quote_plus(search_query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        async with httpx.AsyncClient(headers=headers, timeout=10.0) as client_http:
            search_resp = await client_http.get(search_url)
            soup = BeautifulSoup(search_resp.text, "html.parser")

            # Находим первую ссылку на genius
            link_tag = soup.find("a", href=True)
            genius_link = None
            for a in soup.find_all("a", href=True):
                href = a['href']
                if "genius.com" in href:
                    genius_link = href.split("&")[0].replace("/url?q=", "")
                    break

            if not genius_link:
                await event.reply("❌ Не удалось найти текст песни.")
                return

            # Шаг 2: Парсим страницу Genius
            genius_resp = await client_http.get(genius_link)
            soup = BeautifulSoup(genius_resp.text, "html.parser")

            lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})
            lyrics = "\n".join(div.get_text(separator="\n") for div in lyrics_divs)

            if not lyrics.strip():
                await event.reply("❌ Не удалось получить текст с Genius.")
                return

            if len(lyrics) > 4000:
                lyrics = lyrics[:3800] + "\n\n... (текст обрезан)"

            await event.reply(f"🎵 **{query}**\n\n" + lyrics)

    except Exception as e:
        await event.reply(f"❌ Ошибка при получении текста: {e}")


# --- Функция для запуска и управления каждым клиентом ---
async def start_client(account_config):
    """
    Инициализирует и запускает один клиент Telegram на основе предоставленной конфигурации.
    """
    session_name = account_config['session_name']
    api_id = account_config['api_id']
    api_hash = account_config['api_hash']
    
    online_status_enabled[session_name] = False # Инициализация флага для текущей сессии

    print(f"Запуск клиента для сессии: {session_name}...")
    client = TelegramClient(session_name, api_id, api_hash)

    # Регистрация обработчиков команд
    # (лямбда-функции используются для передачи объекта client и session_name в обработчик)
    
    # Общие команды
    client.add_event_handler(lambda e: info_handler(e, client), events.NewMessage(pattern=r'\.инфо(?: (.+))?'))
    client.add_event_handler(lambda e: ping_handler(e, client), events.NewMessage(pattern=r'\.пинг', outgoing=True)) # outgoing=True для ваших команд
    client.add_event_handler(lambda e: love_handler(e, client), events.NewMessage(pattern=r'\.love', outgoing=True))
    client.add_event_handler(lambda e: quote_handler(e, client), events.NewMessage(pattern=r'\.цит'))
    client.add_event_handler(lambda e: cat_handler(e, client), events.NewMessage(pattern=r'\.котики'))
    client.add_event_handler(lambda e: dog_handler(e, client), events.NewMessage(pattern=r'\.собачки',))
    client.add_event_handler(lambda e: add_user_handler(e, client), events.NewMessage(pattern=r'\.добавить(?: (.+))?'))
    client.add_event_handler(lambda e: help_handler(e, client), events.NewMessage(pattern=r'\.помощь', outgoing=True))
    client.add_event_handler(lambda e, c=client: ai_handler(e, c), events.NewMessage(pattern=r'^.ai\s+.*')) # Замените если ai_handler тоже outgoing=True
    client.add_event_handler(lambda e: help_handler_page2(e, client), events.NewMessage(pattern=r'\.помощь2', outgoing=True))
    client.add_event_handler(lambda e: fire_handler(e, client), events.NewMessage(pattern=r'\.огонь', outgoing=True))
    client.add_event_handler(lambda e: wiki_handler(e, client), events.NewMessage(pattern=r'\.wiki(?: (.+))?', outgoing=True))
    client.add_event_handler(lambda e: calculator_handler(e, client), events.NewMessage(pattern=r'\.калькулятор(?: (.+))?'))
    client.add_event_handler(lambda e: weather_handler(e, client), events.NewMessage(pattern=r'\.погода(?: (.+))?'))
    client.add_event_handler(lambda e: chat_info_handler(e, client, session_name), events.NewMessage(pattern=r'\.чатинфо', outgoing=True))
    client.add_event_handler(lambda e: botinfo_handler(e, client), events.NewMessage(pattern=r'\.botinfo', outgoing=True))
    client.add_event_handler(lambda e: dice_roll_handler(e, client), events.NewMessage(pattern=r'\.кубик', outgoing=True))
    client.add_event_handler(lambda e: quote_of_the_day_handler(e, client), events.NewMessage(pattern=r'\.цитатадня', outgoing=True))
    client.add_event_handler(lambda e: probability_handler(e, client), events.NewMessage(pattern=r'\.вероятность(?: (.+))?', outgoing=True))
    
    # Игнор и кнопки
    client.add_event_handler(lambda e: ignore_handler(e, client),events.NewMessage(pattern=r'^\.игнор$', outgoing=True))
    client.add_event_handler(lambda e: show_chats_command_handler(e, client),events.NewMessage(pattern=r'^\.посмотретьчаты$', outgoing=True))

    client.add_event_handler(lambda e: test_button_handler(e, client), events.NewMessage(pattern=r'\.тесткнопка', outgoing=True))
    client.add_event_handler(test_button_callback, events.CallbackQuery(pattern=r'test_data_123'))

    # Игровые команды (слова)
    client.add_event_handler(lambda e: start_words_game_setup(e, client), events.NewMessage(pattern=r'\.слподбор'))
    client.add_event_handler(lambda e: join_words_game(e, client), events.NewMessage(pattern=r'\.слвойти'))
    client.add_event_handler(lambda e: start_words_game_actual(e, client), events.NewMessage(pattern=r'\.слстарт'))
    client.add_event_handler(lambda e: stop_words_game(e, client), events.NewMessage(pattern=r'\.слстоп'))
    client.add_event_handler(lambda e: leave_words_game(e, client), events.NewMessage(pattern=r'\.слвыйти'))
    client.add_event_handler(lambda e: return_to_words_game(e, client), events.NewMessage(pattern=r'\.слвернутся'))
    client.add_event_handler(lambda e: pin_message_handler(e, client), events.NewMessage(pattern=r'\.закрепи', outgoing=True))
    
    # Другие специальные команды
    client.add_event_handler(lambda e: generate_image_handler(e, client), events.NewMessage(pattern=r"\.сгенерируйкартинку", outgoing=True))
    client.add_event_handler(lambda e: send_logs_to_favorites(e, client), events.NewMessage(pattern=r"\.логиспользования", outgoing=True))
    client.add_event_handler(lambda e: love2_handler(e, client), events.NewMessage(pattern=r"\.сердце2", outgoing=True))
    client.add_event_handler(lambda e: colorful_heart_handler(e, client), events.NewMessage(pattern=r"\.цветноесердце", outgoing=True))
    client.add_event_handler(lambda e: multicolor_heart_handler(e, client), events.NewMessage(pattern=r"\.разноцветноесердце", outgoing=True))
    client.add_event_handler(lambda e: userbots_info_handler(e, client), events.NewMessage(pattern=r'\.юзерботы', outgoing=True))
    client.add_event_handler(lambda e: multicolor_heart_generator(e, client), events.NewMessage(pattern=r'\.отправитьсердце\s+(.+)$', outgoing=True))

    # Команды .ник и .ники (если они outgoing=True)
    client.add_event_handler(lambda e: set_nickname(e), events.NewMessage(pattern=r"^\.ник(?: (.+))?$", outgoing=True))
    client.add_event_handler(lambda e: list_nicknames(e), events.NewMessage(pattern=r"^\.ники$", outgoing=True))

    # Команды для управления вечным онлайном (теперь с передачей session_name)
    client.add_event_handler(lambda e: enable_online_handler(e, client, session_name), events.NewMessage(pattern=r"^\.онлайнвкл$", outgoing=True))
    client.add_event_handler(lambda e: disable_online_handler(e, client, session_name), events.NewMessage(pattern=r"^\.онлайнвыкл$", outgoing=True))
    client.add_event_handler(lambda e: start_duel(e, client), events.NewMessage(pattern=r'^\.битва$', outgoing=True))
    client.add_event_handler(lambda e: duel_button_callback(e, client), events.CallbackQuery())
    client.add_event_handler(lambda e: spam_command_handler(e, client, session_name), events.NewMessage(pattern=r'\.спам (.+) (\d+)', outgoing=True))
    client.add_event_handler(lambda e: handle_autoreply_command(e), events.NewMessage(pattern=r'\.автоответ\s+(.+)', outgoing=True))
    client.add_event_handler(handle_google_command, events.NewMessage(pattern=r'\.google\s+(.+)', outgoing=True))
    client.add_event_handler(handle_rps_command, events.NewMessage(pattern=r'\.цуефа\s+(.+)'))
    client.add_event_handler(lambda e: zov_handler(e, client), events.NewMessage(pattern=r'^\.(?:zov|вызов)(?: (.+))?$'))
    client.add_event_handler(lambda e: ignore_user_handler(e, client), events.NewMessage(pattern=r'^\.(.+)игнор(?: (.+))?$', outgoing=True))
    client.add_event_handler(lambda e: unignore_user_handler(e, client), events.NewMessage(pattern=r'^\.-игнор(?: (.+))?$', outgoing=True))
    client.on(events.NewMessage(pattern=r'^\.текстпесни', outgoing=True))(lambda e: lyrics_handler(e, client))


    # Регистрация RP-команд
    register_rp_commands(client) # Эта функция уже должна быть определена и регистрировать команды

    # Обработчик слов (если он должен срабатывать на *любое* сообщение, а не только исходящие команды)
    # Если process_word_turn должен обрабатывать только входящие слова, уберите outgoing=True
    # Если он должен обрабатывать все сообщения, оставьте без outgoing=True
    # Если он должен игнорировать команды, добавьте проверку на pattern или на то, является ли это командой
    client.add_event_handler(lambda e: process_word_turn(e, client), events.NewMessage()) 
    client.add_event_handler(check_for_autoreply, events.NewMessage(incoming=True))

    try:
        await client.start()
        user_info = await client.get_me()
        print(f"Клиент '{session_name}' подключен как @{user_info.username if user_info.username else user_info.first_name}")
        
        # --- ВОТ ЭТА СТРОКА ОТСУТСТВУЕТ В ВАШЕМ ФРАГМЕНТЕ И ДОЛЖНА БЫТЬ ДОБАВЛЕНА ---
        online_tasks[session_name] = asyncio.create_task(keep_online(client, session_name))
        # -------------------------------------------------------------------------
        
        await client.run_until_disconnected()
    except FloodWaitError as e:
        print(f"[{session_name}] Ошибка флуд-контроля: {e.seconds} секунд. Ожидание...")
        await asyncio.sleep(e.seconds)
    except Exception as e:
        print(f"Ошибка при запуске клиента '{session_name}': {e}")
    finally:
        if client.is_connected():
            print(f"Клиент '{session_name}' отключен.")
            # Важно: также убедитесь, что задача отменяется при отключении
            if session_name in online_tasks and not online_tasks[session_name].done():
                online_tasks[session_name].cancel()
                try:
                    await online_tasks[session_name] # Ждем, пока задача завершится
                except asyncio.CancelledError:
                    pass
            await client.disconnect()

async def main():
    """
    Основная функция для одновременного запуска всех настроенных клиентов Telegram.
    """
    if not ACCOUNTS:
        print("В списке 'ACCOUNTS' не настроено ни одного аккаунта. Пожалуйста, добавьте ваши данные API.")
        return
    
    tasks = []
    for account_config in ACCOUNTS:
        tasks.append(start_client(account_config))

    await asyncio.gather(*tasks)

if __name__ == '__main__':
    print("Запуск многопользовательского юзербота...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Многопользовательский юзербот остановлен пользователем.")
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
