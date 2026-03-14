from passlib.context import CryptContext
from nicegui import ui
from pathlib import Path
import json
from datetime import datetime, timedelta

# Path to persistent users file
USERS_FILE = Path(__file__).with_name('users.json')

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_default_decks():
    """Generate 5 preset Japanese-learning decks for new users."""
    today = datetime.now()

    def card(front, back, reps=0, interval=0, ef=2.5, delta_days=0):
        return {
            "front": front,
            "back": back,
            "repetitions": reps,
            "interval": interval,
            "ef": ef,
            "due_date": (today + timedelta(days=delta_days)).isoformat()
        }

    return [
        {
            "name": "Hiragana あ行",
            "description": "The 5 vowels — the very first row of hiragana every learner starts with",
            "cards": [
                card("あ", "a  —  as in 'f-a-ther'",            reps=2, interval=3, ef=2.5, delta_days=-1),
                card("い", "i  —  as in 'mach-i-ne'",            reps=1, interval=1, ef=2.5, delta_days=0),
                card("う", "u  —  short 'oo', lips unrounded",   reps=0, interval=0, ef=2.5, delta_days=0),
                card("え", "e  —  as in 'b-e-d'",                reps=0, interval=0, ef=2.5, delta_days=0),
                card("お", "o  —  as in 'b-o-ne'",               reps=0, interval=0, ef=2.5, delta_days=0),
            ]
        },
        {
            "name": "Hiragana か行",
            "description": "K-row — ka, ki, ku, ke, ko",
            "cards": [
                card("か", "ka  —  as in 'c-a-r'",   reps=2, interval=3, ef=2.5, delta_days=-3),
                card("き", "ki  —  as in 'k-ee-p'",  reps=2, interval=3, ef=2.5, delta_days=1),
                card("く", "ku  —  as in 'c-oo-l' (short u)", reps=1, interval=1, ef=2.5, delta_days=0),
                card("け", "ke  —  as in 'k-e-t'",   reps=0, interval=0, ef=2.5, delta_days=0),
                card("こ", "ko  —  as in 'c-o-at'",  reps=0, interval=0, ef=2.5, delta_days=0),
            ]
        },
        {
            "name": "Hiragana さ行",
            "description": "S-row — sa, shi, su, se, so  (note: 'si' becomes 'shi' in Japanese)",
            "cards": [
                card("さ", "sa  —  as in 's-a-d'",                    reps=2, interval=3, ef=2.5, delta_days=1),
                card("し", "shi  —  as in 'sh-ee-p'  (NOT 'si')",     reps=1, interval=1, ef=2.5, delta_days=0),
                card("す", "su  —  as in 's-oo-n' (very short u)",    reps=0, interval=0, ef=2.5, delta_days=0),
                card("せ", "se  —  as in 's-e-t'",                    reps=0, interval=0, ef=2.5, delta_days=0),
                card("そ", "so  —  as in 's-o-ap'",                   reps=0, interval=0, ef=2.5, delta_days=0),
            ]
        },
        {
            "name": "Kanji: Nature",
            "description": "Common nature kanji — all appear in everyday words and day names",
            "cards": [
                card("日", "にち / ひ  (nichi / hi)  —  sun; day\nEx: 今日 (きょう) = today",           reps=3, interval=5, ef=2.6, delta_days=-2),
                card("月", "つき / げつ  (tsuki / getsu)  —  moon; month\nEx: 今月 (こんげつ) = this month", reps=2, interval=3, ef=2.5, delta_days=1),
                card("山", "やま  (yama)  —  mountain\nEx: 富士山 (ふじさん) = Mt Fuji",                reps=1, interval=1, ef=2.5, delta_days=0),
                card("川", "かわ  (kawa)  —  river\nEx: 川口 (かわぐち) = Kawaguchi city",             reps=0, interval=0, ef=2.5, delta_days=0),
                card("火", "ひ / か  (hi / ka)  —  fire\nEx: 火山 (かざん) = volcano",                 reps=0, interval=0, ef=2.5, delta_days=0),
                card("木", "き / もく  (ki / moku)  —  tree; wood\nEx: 木々 (きぎ) = trees",           reps=0, interval=0, ef=2.5, delta_days=0),
                card("水", "みず / すい  (mizu / sui)  —  water\nEx: 水道 (すいどう) = tap water",     reps=0, interval=0, ef=2.5, delta_days=0),
                card("土", "つち / ど  (tsuchi / do)  —  earth; soil\nEx: 土地 (とち) = land",         reps=0, interval=0, ef=2.5, delta_days=0),
                card("空", "そら / くう  (sora / kuu)  —  sky; empty\nEx: 青空 (あおぞら) = blue sky", reps=0, interval=0, ef=2.5, delta_days=0),
                card("花", "はな  (hana)  —  flower\nEx: 花火 (はなび) = fireworks",                   reps=0, interval=0, ef=2.5, delta_days=0),
            ]
        },
        {
            "name": "Kanji: People & Daily Life",
            "description": "High-frequency kanji for people, time, and everyday objects",
            "cards": [
                card("人", "ひと / じん  (hito / jin)  —  person\nEx: 日本人 (にほんじん) = Japanese person", reps=3, interval=5, ef=2.6, delta_days=-2),
                card("子", "こ / し  (ko / shi)  —  child\nEx: 子供 (こども) = child",                      reps=2, interval=3, ef=2.5, delta_days=1),
                card("女", "おんな / じょ  (onna / jo)  —  woman\nEx: 女の子 (おんなのこ) = girl",           reps=1, interval=1, ef=2.5, delta_days=0),
                card("男", "おとこ / だん  (otoko / dan)  —  man\nEx: 男の子 (おとこのこ) = boy",            reps=0, interval=0, ef=2.5, delta_days=0),
                card("年", "とし / ねん  (toshi / nen)  —  year\nEx: 今年 (ことし) = this year",            reps=0, interval=0, ef=2.5, delta_days=0),
                card("時", "とき / じ  (toki / ji)  —  time; hour\nEx: 何時 (なんじ) = what time?",         reps=0, interval=0, ef=2.5, delta_days=0),
                card("食", "たべる / しょく  (taberu / shoku)  —  eat; food\nEx: 食事 (しょくじ) = meal",   reps=0, interval=0, ef=2.5, delta_days=0),
                card("本", "ほん / もと  (hon / moto)  —  book; origin\nEx: 日本 (にほん) = Japan",         reps=0, interval=0, ef=2.5, delta_days=0),
                card("大", "おお / だい  (oo / dai)  —  big; great\nEx: 大学 (だいがく) = university",      reps=0, interval=0, ef=2.5, delta_days=0),
                card("小", "ちい / しょう  (chii / shou)  —  small\nEx: 小学校 (しょうがっこう) = primary school", reps=0, interval=0, ef=2.5, delta_days=0),
            ]
        },
    ]


_default_users = {
    "alice": {
        "password_hash": pwd_context.hash("aliceSecret2025"),
        "full_name": "John Pork",
        "role": "admin",
        "decks": get_default_decks()
    },
    "bob": {
        "password_hash": pwd_context.hash("bob123!letmein"),
        "full_name": "Bob Builder",
        "role": "user",
        "decks": get_default_decks()
    }
}

users = {}


def load_users():
    global users
    if USERS_FILE.exists():
        try:
            users = json.loads(USERS_FILE.read_text(encoding='utf-8'))
            for username in users:
                if 'decks' not in users[username]:
                    users[username]['decks'] = get_default_decks()
                    save_users()
        except Exception:
            users = _default_users.copy()
    else:
        users = _default_users.copy()


def save_users():
    try:
        USERS_FILE.write_text(json.dumps(users, indent=2), encoding='utf-8')
    except Exception as e:
        ui.notify(f"Failed to save users: {e}", type='negative')


def add_user(username: str, full_name: str, password: str, role: str = 'user') -> bool:
    username = username.strip().lower()
    if not username or username in users:
        return False
    users[username] = {
        'password_hash': pwd_context.hash(password),
        'full_name': full_name,
        'role': role,
        'decks': get_default_decks()
    }
    save_users()
    return True


load_users()

current_user = None
current_username = None


def is_authenticated():
    return current_user is not None


def login_success(username: str):
    global current_user
    global current_username
    current_user = users.get(username)
    current_username = username
    ui.notify(f"Welcome back, {current_user['full_name']}!", type='positive')
    ui.navigate.to('/dashboard')


def login_failed():
    ui.notify("Invalid username or password", type='negative', position='top')


def logout():
    global current_user
    global current_username
    current_user = None
    current_username = None
    ui.navigate.to('/')


# ---------------------------------------------------------------------------
# Dashboard background image
# ---------------------------------------------------------------------------
# The image is stored as a base64 data URL directly in users.json.
# get_bg_css() returns '' when no image is set so callers can skip
# injecting a <style> tag entirely.
# 5 MB raw → ~6.7 MB after base64; acceptable for a desktop single-user app.
# ---------------------------------------------------------------------------

MAX_IMAGE_BYTES = 5 * 1024 * 1024   # 5 MB


def get_bg_css() -> str:
    """Return a full <style> block for the dashboard background, or ''.

    The image is placed on body::before with filter:brightness() applied to
    that pseudo-element alone.  This dims the background without affecting
    the cards, text, or any other page content sitting on top of it.
    """
    if not current_user:
        return ''
    data_url = current_user.get('bg_image', '')
    if not data_url:
        return ''
    brightness = round(float(current_user.get('bg_brightness', 1.0)), 3)
    return (
        'body { margin: 0; }\n'
        'body::before {\n'
        '  content: "";\n'
        '  position: fixed;\n'
        '  inset: 0;\n'
        f' background-image: url("{data_url}");\n'
        '  background-size: cover;\n'
        '  background-position: center;\n'
        '  background-attachment: fixed;\n'
        f' filter: brightness({brightness});\n'
        '  z-index: -1;\n'
        '}\n'
    )


def get_bg_brightness() -> float:
    """Return the stored brightness value (0.0-1.0), defaulting to 1.0."""
    if not current_user:
        return 1.0
    return float(current_user.get('bg_brightness', 1.0))


def set_bg_brightness(value: float) -> None:
    """Persist a brightness value clamped to [0.0, 1.0]."""
    if current_user:
        current_user['bg_brightness'] = round(max(0.0, min(1.0, value)), 3)
        save_users()


def set_bg_image(data_url: str) -> None:
    """Persist a base64 data URL as the custom dashboard background.

    Brightness is always reset to 1.0 on upload so a fresh image starts
    at full brightness regardless of any previously stored value.
    """
    if current_user:
        current_user['bg_image'] = data_url
        current_user['bg_brightness'] = 1.0
        save_users()


def clear_bg_image() -> None:
    """Remove the custom background image."""
    if current_user:
        current_user.pop('bg_image', None)
        save_users()
