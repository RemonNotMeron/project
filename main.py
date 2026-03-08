from nicegui import ui
from auth import users, pwd_context, login_success, login_failed

from pages import login, registeration, dashboard


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(native=True, title='Flashcard App')