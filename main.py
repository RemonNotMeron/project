from nicegui import ui
from pages import login, registeration, dashboard, flashcard_library


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(native=True, title='Flashcard App', window_size=(1200, 800))