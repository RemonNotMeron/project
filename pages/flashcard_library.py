from nicegui import ui
import auth
import datetime
from datetime import date, datetime


@ui.page('/flashcard_library')
def flashcard_library_page():
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    # ── header ──────────────────────────────────────────────────────────────
    with ui.row().classes('w-full items-center gap-3 mb-1'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')) \
            .props('flat round').classes('text-grey-6')
        ui.label('Flashcard Library').classes('text-2xl font-bold')

    ui.label('Here you can browse and manage your flashcards.').classes('mb-2')

    flashgrid = ui.grid(columns=5).classes('w-full gap-5 mt-2')

    def render_decks():
        flashgrid.clear()
        user = None
        if hasattr(auth, 'current_username') and auth.current_username in auth.users:
            user = auth.users[auth.current_username]
        else:
            for k, v in auth.users.items():
                if v is auth.current_user:
                    user = v
                    break
        decks = user.get('decks', []) if user else []

        with flashgrid:
            with ui.card().classes('cursor-pointer bg-grey-2 p-6 flex flex-col items-center justify-center min-h-[120px]'):
                ui.button('Create new', on_click=lambda: ui.navigate.to('/create_new_deck')).classes('text-center').props('flat')

            if decks:
                today = date.today()
                for d in decks:
                    def card_is_due(card):
                        dd = card.get('due_date')
                        if not dd:
                            return True
                        try:
                            if 'T' in str(dd):
                                due_date = datetime.fromisoformat(dd).date()
                            else:
                                due_date = date.fromisoformat(dd)
                            return due_date <= today
                        except Exception:
                            return True

                    def get_scheduled_breakdown(deck_cards):
                        scheduled = {}
                        for c in deck_cards:
                            dd = c.get('due_date')
                            if dd:
                                try:
                                    if 'T' in str(dd):
                                        due_date = datetime.fromisoformat(dd).date()
                                    else:
                                        due_date = date.fromisoformat(dd)
                                    if due_date > today:
                                        scheduled[due_date] = scheduled.get(due_date, 0) + 1
                                except Exception:
                                    pass
                        return scheduled

                    due_count = sum(1 for c in d.get('cards', []) if card_is_due(c))
                    scheduled = get_scheduled_breakdown(d.get('cards', []))

                    with ui.button().classes('cursor-pointer hover:scale-105 transition-transform bg-white dark:bg-grey-8 flex flex-col items-center justify-center p-8 gap-4 shadow-sm hover:shadow-md bg-grey-2 dark:bg-grey-7') \
                        .on('click', lambda d=d: ui.navigate.to(f'/flashcard_deck/{d.get("name", "Untitled")}')):
                        ui.label(d.get('name', 'Untitled')).classes('text-lg font-medium text-center text-grey-7')
                        if due_count:
                            ui.label(f"{due_count} due today").classes('text-sm text-red-600')
                        if scheduled:
                            dates_str = ', '.join(f"{count} on {dt.strftime('%b %d')}" for dt, count in sorted(scheduled.items())[:3])
                            ui.label(f"Upcoming: {dates_str}").classes('text-xs text-gray-500 italic')
            else:
                ui.label('All flashcard decks will be displayed here').classes('text-center text-green-700 mt-4')

    render_decks()
