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
    """Generate 5 preset Japanese-learning decks for new users.

    The decks follow a natural beginner progression:
      1. Hiragana vowel row (あ行)   — the absolute starting point
      2. Hiragana か行 & さ行        — next two gojuon rows
      3. Kanji: Nature               — high-frequency nature kanji (JLPT N5)
      4. Kanji: People & Daily Life  — common people/time/object kanji (JLPT N5)

    SRS metadata (repetitions, interval, ef, due_date) is seeded with a
    spread of values so the library page shows a realistic mix of due,
    upcoming, and fresh cards right from first login.
    """
    today = datetime.now()

    def card(front, back, reps=0, interval=0, ef=2.5, delta_days=0):
        """Helper to build a card dict with a relative due_date offset."""
        return {
            "front": front,
            "back": back,
            "repetitions": reps,
            "interval": interval,
            "ef": ef,
            "due_date": (today + timedelta(days=delta_days)).isoformat()
        }

    return [
        # ------------------------------------------------------------------ #
        # Deck 1 – Hiragana あ行 (the 5 vowels)
        # Every Japanese learner starts here. These 5 characters underpin
        # every other hiragana and katakana sound.
        # ------------------------------------------------------------------ #
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
        # ------------------------------------------------------------------ #
        # Deck 2 – Hiragana か行 (K-row)
        # ------------------------------------------------------------------ #
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
        # ------------------------------------------------------------------ #
        # Deck 3 – Hiragana さ行 (S-row)
        # Note: 'si' does not exist in Japanese — it becomes 'shi'.
        # ------------------------------------------------------------------ #
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
        # ------------------------------------------------------------------ #
        # Deck 4 – Kanji: Nature  (JLPT N5)
        # All 10 appear in everyday vocabulary and the days of the week.
        # ------------------------------------------------------------------ #
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
        # ------------------------------------------------------------------ #
        # Deck 5 – Kanji: People & Daily Life  (JLPT N5)
        # ------------------------------------------------------------------ #
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


# Default users (used when no users.json exists)
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

# users will be loaded from USERS_FILE if present
users = {}


def load_users():
    global users
    if USERS_FILE.exists():
        try:
            # Load users from file
            users = json.loads(USERS_FILE.read_text(encoding='utf-8'))
            # Add default decks to users that don't have any
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


# Load users on import
load_users()

# Session / logged-in state
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
