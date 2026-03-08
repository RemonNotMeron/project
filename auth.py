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
    """Generate 5 preset decks with sample cards for testing"""
    today = datetime.now()
    return [
        {
            "name": "Biology 101",
            "description": "Basic biology terms and concepts",
            "cards": [
                {
                    "front": "What is photosynthesis?",
                    "back": "Process by which plants convert light energy into chemical energy",
                    "repetitions": 2,
                    "interval": 3,
                    "ef": 2.5,
                    "due_date": (today - timedelta(days=1)).isoformat()
                },
                {
                    "front": "What are mitochondria?",
                    "back": "Powerhouse of the cell; responsible for producing energy (ATP)",
                    "repetitions": 1,
                    "interval": 1,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "Define osmosis",
                    "back": "Movement of water molecules across a semipermeable membrane",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "What is the function of ribosomes?",
                    "back": "Protein synthesis; translation of mRNA into proteins",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                }
            ]
        },
        {
            "name": "Spanish Vocabulary",
            "description": "Common Spanish words and phrases",
            "cards": [
                {
                    "front": "Hello",
                    "back": "Hola",
                    "repetitions": 3,
                    "interval": 5,
                    "ef": 2.6,
                    "due_date": (today - timedelta(days=3)).isoformat()
                },
                {
                    "front": "Thank you",
                    "back": "Gracias",
                    "repetitions": 2,
                    "interval": 3,
                    "ef": 2.5,
                    "due_date": (today + timedelta(days=1)).isoformat()
                },
                {
                    "front": "Water",
                    "back": "Agua",
                    "repetitions": 1,
                    "interval": 1,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "Good morning",
                    "back": "Buenos días",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                }
            ]
        },
        {
            "name": "World History",
            "description": "Historical events and dates",
            "cards": [
                {
                    "front": "What year did World War II end?",
                    "back": "1945",
                    "repetitions": 2,
                    "interval": 3,
                    "ef": 2.5,
                    "due_date": (today + timedelta(days=1)).isoformat()
                },
                {
                    "front": "Who was the first President of the United States?",
                    "back": "George Washington",
                    "repetitions": 1,
                    "interval": 1,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "In what year did the Titanic sink?",
                    "back": "1912",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "What ancient wonder is still standing?",
                    "back": "The Great Pyramid of Giza",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                }
            ]
        },
        {
            "name": "Chemistry",
            "description": "Chemical elements and reactions",
            "cards": [
                {
                    "front": "What is the chemical symbol for Gold?",
                    "back": "Au",
                    "repetitions": 2,
                    "interval": 3,
                    "ef": 2.5,
                    "due_date": (today + timedelta(days=2)).isoformat()
                },
                {
                    "front": "What is the atomic number of Carbon?",
                    "back": "6",
                    "repetitions": 1,
                    "interval": 1,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "What does pH measure?",
                    "back": "The acidity or alkalinity of a solution",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "What is the chemical formula for salt?",
                    "back": "NaCl",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                }
            ]
        },
        {
            "name": "French Vocabulary",
            "description": "Common French words and expressions",
            "cards": [
                {
                    "front": "Yes",
                    "back": "Oui",
                    "repetitions": 3,
                    "interval": 5,
                    "ef": 2.6,
                    "due_date": (today - timedelta(days=2)).isoformat()
                },
                {
                    "front": "No",
                    "back": "Non",
                    "repetitions": 2,
                    "interval": 3,
                    "ef": 2.5,
                    "due_date": (today + timedelta(days=1)).isoformat()
                },
                {
                    "front": "I love you",
                    "back": "Je t'aime",
                    "repetitions": 1,
                    "interval": 1,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                },
                {
                    "front": "Excuse me",
                    "back": "Excusez-moi",
                    "repetitions": 0,
                    "interval": 0,
                    "ef": 2.5,
                    "due_date": today.isoformat()
                }
            ]
        }
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
