from nicegui import ui
import auth


@ui.page('/dashboard')
def dashboard_page():
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    ui.label(f"Welcome to your dashboard, {auth.current_user['full_name']}!").classes('text-2xl font-bold mb-4')