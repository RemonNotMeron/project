from nicegui import ui
import uuid
import auth
from datetime import datetime


# ---------------------------------------------------------------------------
# /create_new_deck
# ---------------------------------------------------------------------------

@ui.page('/create_new_deck')
def create_new_deck_page():
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    # ── page-level state ───────────────────────────────────────────────────
    # Each card is stored as a plain dict with a temporary 'id' used only
    # to identify which row to delete — the id is stripped before saving.
    current_cards = []  # list of {'id': str, 'front': str, 'back': str}
    selected      = {'id': None}   # which card is open in the editor

    # ── helpers ────────────────────────────────────────────────────────────

    def add_card():
        card = {'id': str(uuid.uuid4()), 'front': '', 'back': ''}
        current_cards.append(card)
        selected['id'] = card['id']
        _refresh()

    def remove_card(card_id):
        nonlocal current_cards
        current_cards = [c for c in current_cards if c['id'] != card_id]
        # If the deleted card was selected, select the last remaining one
        if selected['id'] == card_id:
            selected['id'] = current_cards[-1]['id'] if current_cards else None
        _refresh()

    def select_card(card_id):
        selected['id'] = card_id
        _refresh()

    def _get_selected():
        return next((c for c in current_cards if c['id'] == selected['id']), None)

    # ── save ───────────────────────────────────────────────────────────────

    def save_deck():
        name = deck_name_input.value.strip()
        if not name:
            ui.notify('Please enter a deck name.', type='warning')
            return
        if not current_cards:
            ui.notify('Add at least one card.', type='warning')
            return

        # Validate no empty cards
        for c in current_cards:
            if not c['front'].strip() or not c['back'].strip():
                ui.notify('All cards must have both a front and a back.', type='warning')
                return

        username = auth.current_username
        if not username:
            ui.notify('Not logged in.', type='negative')
            return

        existing = auth.users[username].setdefault('decks', [])
        if any(d['name'].lower() == name.lower() for d in existing):
            ui.notify('A deck with that name already exists.', type='warning')
            return

        # Build cards with fresh SRS metadata — identical defaults to
        # get_default_decks() so new cards integrate cleanly with the
        # existing SM-2 scheduling in flashcard_deck.py.
        now = datetime.now().isoformat()
        saved_cards = [
            {
                'front':       c['front'].strip(),
                'back':        c['back'].strip(),
                'repetitions': 0,
                'interval':    0,
                'ef':          2.5,
                'due_date':    now,
            }
            for c in current_cards
        ]

        existing.append({'name': name, 'description': '', 'cards': saved_cards})
        auth.save_users()
        ui.notify(f'Deck "{name}" saved!', type='positive')
        ui.navigate.to('/flashcard_library')

    # ── UI refresh ─────────────────────────────────────────────────────────
    # Both the card list (left) and the editor (right) are rebuilt together
    # whenever state changes. This keeps the two panels in sync without
    # needing separate refresh paths.

    def _refresh():
        _build_list()
        _build_editor()

    def _build_list():
        card_list.clear()
        with card_list:
            for i, card in enumerate(current_cards, 1):
                is_sel = card['id'] == selected['id']
                row_classes = (
                    'w-full items-center gap-2 px-3 py-2 rounded-lg cursor-pointer '
                    + ('bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700'
                       if is_sel else
                       'hover:bg-grey-2 dark:hover:bg-grey-8')
                )
                with ui.row().classes(row_classes) \
                        .on('click', lambda _, cid=card['id']: select_card(cid)):
                    ui.label(str(i)).classes('text-xs text-grey-5 w-5 text-right shrink-0')
                    ui.label(card['front'] or '(empty front)') \
                        .classes('flex-1 truncate text-sm ' + ('font-medium text-blue-700 dark:text-blue-300' if is_sel else 'text-grey-7'))
                    ui.label('↔').classes('text-grey-4 text-xs shrink-0')
                    ui.label(card['back'] or '(empty back)') \
                        .classes('flex-1 truncate text-sm text-grey-5')
                    ui.button(icon='close') \
                        .props('flat dense round size=xs') \
                        .classes('text-grey-4 hover:text-red-500 shrink-0') \
                        .on('click', lambda _, cid=card['id']: remove_card(cid))

    def _build_editor():
        editor_area.clear()
        card = _get_selected()

        with editor_area:
            if not current_cards:
                with ui.column().classes('items-center justify-center w-full h-full py-16 gap-3'):
                    ui.icon('style', size='3rem').classes('text-grey-4')
                    ui.label('No cards yet.').classes('text-grey-5')
                    ui.label('Click "Add card" to get started.').classes('text-xs text-grey-4')
                return

            if card is None:
                ui.label('Select a card on the left to edit it.').classes('text-grey-5 italic py-10')
                return

            # Card number badge
            idx = next((i for i, c in enumerate(current_cards, 1) if c['id'] == card['id']), '?')
            with ui.row().classes('items-center gap-2 mb-4'):
                ui.label(f'Card {idx}').classes('text-base font-semibold text-grey-7')
                ui.label(f'of {len(current_cards)}').classes('text-sm text-grey-5')

            # Front input
            ui.label('Front').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-1')
            front_in = ui.input(
                placeholder='Character, word, or question…',
                value=card['front']
            ).props('outlined').classes('w-full text-lg mb-4')

            # Back textarea
            ui.label('Back').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-1')
            back_in = ui.textarea(
                placeholder='Reading, meaning, or answer…',
                value=card['back']
            ).props('outlined autogrow').classes('w-full mb-2')

            # Live-bind inputs → card dict so the list preview stays current
            def _on_front(e, c=card):
                c['front'] = e.value
                _build_list()   # refresh just the list for live previews

            def _on_back(e, c=card):
                c['back'] = e.value
                _build_list()

            front_in.on('update:model-value', _on_front)
            back_in.on('update:model-value', _on_back)

            # Mini preview of how the card looks
            ui.separator().classes('my-4')
            ui.label('Preview').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-2')
            with ui.card().classes(
                'w-full p-6 text-center rounded-xl '
                'bg-gradient-to-br from-blue-50 to-indigo-50 '
                'dark:from-grey-8 dark:to-grey-9 '
                'border border-blue-100 dark:border-grey-7'
            ):
                ui.label(card['front'] or '—').classes('text-4xl font-light text-grey-8 dark:text-grey-2 mb-3')
                ui.separator().classes('opacity-30')
                ui.label(card['back'] or '—').classes('text-sm text-grey-6 mt-3 whitespace-pre-line')

    # ── layout ─────────────────────────────────────────────────────────────

    # Header
    with ui.row().classes('w-full items-center gap-3 mb-1'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/flashcard_library')) \
            .props('flat round').classes('text-grey-6')
        ui.label('Create new deck').classes('text-2xl font-semibold text-grey-8 dark:text-grey-2')

    ui.separator().classes('mb-5')

    # Deck name
    with ui.row().classes('items-center gap-3 mb-6 w-full max-w-lg'):
        ui.label('Deck name').classes('text-sm font-medium text-grey-7 w-24 shrink-0')
        deck_name_input = ui.input(placeholder='e.g. Hiragana た行') \
            .props('outlined dense').classes('flex-1')

    # Two-column body
    with ui.row().classes('w-full gap-6 items-start'):

        # LEFT — card list
        with ui.card().classes('w-5/12 p-4 gap-3 flex flex-col'):
            with ui.row().classes('w-full items-center justify-between mb-1'):
                ui.label('Cards').classes('font-medium text-grey-7')
                card_count = ui.label('').classes('text-xs text-grey-5')

            card_list = ui.column().classes('w-full gaDp-1 min-h-[260px] max-h-[520px] overflow-y-auto')

            ui.separator().classes('my-2')

            ui.button('Add card', icon='add') \
                .props('unelevated no-caps') \
                .classes('w-full bg-primary text-white rounded-lg') \
                .on('click', add_card)

        # RIGHT — editor + preview
        with ui.card().classes('flex-1 p-5 gap-0 flex flex-col'):
            editor_area = ui.column().classes('w-full gap-0')

    # Save bar
    ui.separator().classes('mt-8 mb-4')
    with ui.row().classes('w-full justify-end gap-3'):
        ui.button('Cancel', on_click=lambda: ui.navigate.to('/flashcard_library')) \
            .props('flat no-caps').classes('text-grey-6')
        ui.button('Save deck', icon='save') \
            .props('unelevated no-caps') \
            .classes('bg-green-600 text-white px-8 rounded-lg') \
            .on('click', save_deck)

    # ── initial render ─────────────────────────────────────────────────────
    add_card()   # open with one empty card ready to fill in
