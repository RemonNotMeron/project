from nicegui import ui
import auth
from datetime import date, datetime

@ui.page('/progress_visualiser')
def progress_visualiser():
    # Redirect to login if not authenticated
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return
    
    ui.label('Progress Visualiser').classes('text-2xl font-bold mb-4')
    ui.label('Here you can see your learning progress and statistics.').classes('mb-2')
    # Add progress visualisation features here (e.g., charts, stats)