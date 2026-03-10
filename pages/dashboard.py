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

    with ui.card().classes('w-full bg-grey-2 dark:bg-grey-9'):
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


    ui.label(f"Welcome to your dashboard, {auth.current_user['full_name']}!").classes('text-2xl font-bold mb-4')