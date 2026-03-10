from nicegui import ui
from pages import login, registeration, dashboard


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(native=True, title='Flashcard App')