from nicegui import ui
import auth
from datetime import datetime




def get_user_icon():
    """Get user's custom icon or default"""
    if auth.current_user and 'icon' in auth.current_user:
        return auth.current_user['icon']
    return '👤'



@ui.page('/dashboard')
def dashboard_page():
    # Redirect to login if not authenticated
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return
    
    # Check if user is admin
    is_admin = auth.current_user.get('role') == 'admin'
    
    if is_admin:
        show_admin_dashboard()
    else:
        show_user_dashboard()

def show_admin_dashboard():
    ui.label(f"Welcome to the admin dashboard, {auth.current_user['full_name']}!").classes('text-2xl font-bold mb-4')
    ui.label("Here you can manage users and view analytics.").classes('mb-2')
    # Add admin-specific features here (e.g., user management, analytics)

def show_user_dashboard():

    with ui.card().classes('w-full max-w-5xl mx-auto bg-grey-2 dark:bg-grey-9'):
                with ui.row().classes('items-center w-full'):
                    # User avatar with custom icon
                    with ui.avatar(size='lg', color='primary'):
                        ui.label(get_user_icon()).classes('text-2xl')

                    ui.label(f'Welcome back, {auth.current_user["full_name"]}!').classes('text-2xl font-medium align-left')


                    #display time and date at the right hand side of the row
                    ui.label(datetime.now().strftime('%A, %d %B %Y')).classes('ml-auto opacity-70 align-center text-lg font-medium')


                    #digital clock  at the right hand side of the row
                    clock = ui.label('Waiting...').classes('ml-2 opacity-70 align-right text-2xl font-medium')

                    ui.timer(1.0, lambda: clock.set_text(datetime.now().strftime('%H:%M')))

    with ui.card().classes('w-full max-w-5xl mx-auto p-6 gap-8'):
        #placeholder for due cards, will be replaced with actual due cards in the future
        with ui.column().classes('gap-2 w-full max-h-48 overflow-y-auto'):
            ui.label('cards due today will be displayed here').classes('text-lg text-grey-7 mt-0')

            # Check for due cards from all decks
            has_due_cards = False
            for deck in auth.current_user.get('decks', []):
                due_cards = [c for c in deck.get('cards', []) if 'due_date' in c and datetime.fromisoformat(c['due_date']) <= datetime.now()]
                if due_cards:
                    has_due_cards = True
                    ui.label(f'You have {len(due_cards)} cards due for review in "{deck["name"]}"').classes('text-lg text-grey-7 mt-0')
            
            if not has_due_cards:
                ui.label('You are done for today! 🎉').classes('text-lg text-grey-7 mt-0 font-semibold')

    # Navigation tiles
    with ui.card().props('rounded').classes('w-full max-w-5xl mx-auto p-6 gap-8'):
        ui.label('Navigate to different functions').classes('text-lg text-grey-7 mt-0')

        with ui.grid(columns=3).classes('w-full gap-5'):
            with ui.button(on_click=lambda: ui.navigate.to('/flashcard_library')).classes('cursor-pointer hover:scale-105 transition-transform bg-white dark:bg-grey-8 flex flex-col items-center justify-center p-8 gap-4 shadow-sm hover:shadow-md bg-grey-2 dark:bg-grey-7'):
                ui.icon('library_books', size='4rem').classes('text-teal-600 dark:text-teal-400 bg-grey-2 dark:bg-grey-7 rounded-full p-2')
                ui.label('Flashcard library').classes('text-lg font-medium text-center text-grey-7')

            with ui.button(on_click=lambda: ui.navigate.to('/progress_visualiser')).classes('cursor-pointer hover:scale-105 transition-transform bg-white dark:bg-grey-8 flex flex-col items-center justify-center p-8 gap-4 shadow-sm hover:shadow-md bg-grey-2 dark:bg-grey-7'):
                ui.icon('trending_up', size='4rem').classes('text-purple-600 dark:text-purple-400 bg-grey-2 dark:bg-grey-7 rounded-full p-2')
                ui.label('Progress visualiser').classes('text-lg font-medium text-center text-grey-7')

            with ui.button(on_click=lambda: ui.navigate.to('/preference_settings')).classes('cursor-pointer hover:scale-105 transition-transform bg-white dark:bg-grey-8 flex flex-col items-center justify-center p-8 gap-4 shadow-sm hover:shadow-md bg-grey-2 dark:bg-grey-7'):
                ui.icon('settings', size='4rem').classes('text-orange-600 dark:text-orange-400 bg-grey-2 dark:bg-grey-7 rounded-full p-2')
                ui.label('Preference Settings').classes('text-lg font-medium text-center text-grey-7')

    