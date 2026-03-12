from nicegui import ui
import auth



@ui.page('/flashcard-library')
def flashcard_library_page():
    # Redirect to login if not authenticated
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return
    
    ui.label('Flashcard Library').classes('text-2xl font-bold mb-4')
    ui.label('Here you can browse and manage your flashcards.').classes('mb-2')
    # Add flashcard library features here (e.g., view, create, edit flashcards)