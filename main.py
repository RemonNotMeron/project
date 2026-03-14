from nicegui import ui
from pages import login, registeration, dashboard, flashcard_library, progress_visualiser, create_new_deck, flashcard_deck, preference_settings, teacher_dashboard


if __name__ in {'__main__', '__mp_main__'}:
    ui.run(native=True, title='Flashcard App', window_size=(1400, 800))