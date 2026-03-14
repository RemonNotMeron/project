from nicegui import ui
import auth
from datetime import datetime, date, timedelta


# ---------------------------------------------------------------------------
# SM-2 algorithm (manual implementation — no external library)
# ---------------------------------------------------------------------------
# quality: 0–5 rating from the user
#   0–1 = complete failure / wrong
#   2   = wrong but answer felt familiar
#   3   = correct with serious difficulty
#   4   = correct with some hesitation
#   5   = perfect recall
#
# ef   = easiness factor (starts at 2.5, floor of 1.3)
# interval = days until next review
# ---------------------------------------------------------------------------

def sm2(card: dict, quality: int) -> dict:
    """Apply one SM-2 repetition to a card dict and return the updated card."""
    ef        = card.get('ef', 2.5)
    reps      = card.get('repetitions', 0)
    interval  = card.get('interval', 0)

    if quality >= 3:
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        reps += 1
    else:
        # Failed — reset to the beginning
        reps     = 0
        interval = 1

    # Update easiness factor (floor 1.3)
    ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    ef = max(1.3, round(ef, 4))

    due = (datetime.now() + timedelta(days=interval)).isoformat()

    return {**card, 'ef': ef, 'repetitions': reps, 'interval': interval, 'due_date': due}


# ---------------------------------------------------------------------------
# Helper — find the current user's deck by name
# ---------------------------------------------------------------------------

def _get_deck(deck_name: str):
    username = auth.current_username
    if not username or username not in auth.users:
        return None
    for deck in auth.users[username].get('decks', []):
        if deck.get('name') == deck_name:
            return deck
    return None


def _save_deck(deck_name: str, updated_deck: dict):
    username = auth.current_username
    if not username or username not in auth.users:
        return
    decks = auth.users[username].get('decks', [])
    for i, d in enumerate(decks):
        if d.get('name') == deck_name:
            decks[i] = updated_deck
            break
    auth.save_users()


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

@ui.page('/flashcard_deck/{deck_name}')
def flashcard_deck_page(deck_name: str):
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    # ── inject flip-card CSS + JS ──────────────────────────────────────────
    ui.add_head_html('''
    <style>
      .flip-scene {
        width: 100%;
        perspective: 1200px;
      }
      .flip-card {
        position: relative;
        width: 100%;
        min-height: 260px;
        transform-style: preserve-3d;
        transition: transform 0.55s cubic-bezier(.4,0,.2,1);
        cursor: pointer;
      }
      .flip-card.flipped {
        transform: rotateY(180deg);
      }
      .flip-face {
        position: absolute;
        inset: 0;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2.5rem;
        box-shadow: 0 4px 32px rgba(0,0,0,0.10);
      }
      .flip-front {
        background: linear-gradient(135deg, #f0f4ff 0%, #e8f0fe 100%);
        border: 1.5px solid #c7d7f8;
      }
      .dark .flip-front {
        background: linear-gradient(135deg, #1e2a3a 0%, #1a2332 100%);
        border: 1.5px solid #2d3f5a;
      }
      .flip-back {
        background: linear-gradient(135deg, #f0fff4 0%, #e6f9ef 100%);
        border: 1.5px solid #b7e4c7;
        transform: rotateY(180deg);
      }
      .dark .flip-back {
        background: linear-gradient(135deg, #1a2e22 0%, #162419 100%);
        border: 1.5px solid #2a4a35;
      }
      .card-character {
        font-size: 5rem;
        line-height: 1.1;
        font-weight: 300;
        letter-spacing: -0.02em;
        color: #1a1a2e;
        text-align: center;
      }
      .dark .card-character {
        color: #e8eaf6;
      }
      .card-hint {
        font-size: 0.85rem;
        color: #6b7280;
        margin-top: 1.2rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
      }
      .card-back-text {
        font-size: 1.35rem;
        font-weight: 500;
        color: #1a3a2e;
        text-align: center;
        white-space: pre-line;
        line-height: 1.65;
      }
      .dark .card-back-text {
        color: #c8e6c9;
      }
      .rating-btn {
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.04em !important;
        transition: transform 0.15s, box-shadow 0.15s !important;
      }
      .rating-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
      }
      .progress-bar-fill {
        height: 6px;
        border-radius: 3px;
        background: linear-gradient(90deg, #4ade80, #22c55e);
        transition: width 0.4s ease;
      }
    </style>
    <script>
      function flipCard() {
        const card = document.getElementById('the-flip-card');
        if (card) card.classList.toggle('flipped');
      }
      function resetFlip() {
        const card = document.getElementById('the-flip-card');
        if (card) card.classList.remove('flipped');
      }
    </script>
    ''')

    # ── state ──────────────────────────────────────────────────────────────
    deck = _get_deck(deck_name)
    if not deck:
        ui.label('Deck not found.').classes('text-red-500 text-lg mt-8')
        ui.button('← Back', on_click=lambda: ui.navigate.to('/flashcard_library')).classes('mt-4')
        return

    all_cards   = deck.get('cards', [])
    today       = date.today()

    def is_due(card):
        dd = card.get('due_date')
        if not dd:
            return True
        try:
            d = datetime.fromisoformat(dd).date() if 'T' in str(dd) else date.fromisoformat(dd)
            return d <= today
        except Exception:
            return True

    due_cards   = [c for c in all_cards if is_due(c)]
    state       = {
        'queue'    : list(due_cards),   # cards left this session
        'index'    : 0,
        'done'     : 0,
        'total'    : len(due_cards),
        'revealed' : False,
    }

    # ── layout ─────────────────────────────────────────────────────────────
    with ui.column().classes('w-full max-w-2xl mx-auto px-4 pt-6 pb-10 gap-5'):

        # header row
        with ui.row().classes('w-full items-center gap-3'):
            ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/flashcard_library')) \
                .props('flat round').classes('text-grey-6')
            ui.label(deck_name).classes('text-xl font-semibold text-grey-8 dark:text-grey-2 flex-1')
            session_label = ui.label('').classes('text-sm text-grey-5')

        # progress bar
        progress_wrap = ui.element('div').classes('w-full bg-grey-3 dark:bg-grey-7 rounded-full')
        with progress_wrap:
            progress_bar = ui.element('div').classes('progress-bar-fill').style('width: 0%')

        # flip card
        with ui.element('div').classes('flip-scene w-full'):
            with ui.element('div').classes('flip-card').props('id="the-flip-card"') \
                    .on('click', lambda: (
                        ui.run_javascript('flipCard()'),        # trigger the CSS flip animation
                        state.update({'revealed': True}),       # mark card as revealed in state
                        rating_row.set_visibility(True),        # show the rating buttons
                        flip_hint.set_visibility(False),        # hide the "tap to reveal" hint
                    )):
                # front face
                front_face = ui.element('div').classes('flip-face flip-front')
                with front_face:
                    front_char = ui.label('').classes('card-character')
                    ui.label('tap to reveal').classes('card-hint')

                # back face
                back_face = ui.element('div').classes('flip-face flip-back')
                with back_face:
                    back_text = ui.label('').classes('card-back-text')

        flip_hint = ui.label('Click the card to flip it').classes(
            'text-xs text-grey-5 text-center w-full mt-1'
        )

        # rating buttons (hidden until card is flipped)
        with ui.column().classes('w-full gap-3') as rating_row:
            ui.label('Did you remember it?').classes('text-sm text-grey-6 text-center w-full')
            with ui.row().classes('w-full justify-center gap-4'):
                ui.button('✗  Forgot', on_click=lambda: _apply_rating(0)) \
                    .classes('rating-btn bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-200 px-8 py-3') \
                    .props('flat no-caps')
                ui.button('✓  Remembered', on_click=lambda: _apply_rating(5)) \
                    .classes('rating-btn bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-200 px-8 py-3') \
                    .props('flat no-caps')

        rating_row.set_visibility(False)

        # done panel (hidden initially)
        with ui.card().classes(
            'w-full items-center text-center p-8 gap-4 '
            'bg-green-50 dark:bg-green-900 border border-green-200 dark:border-green-700 rounded-2xl'
        ) as done_panel:
            ui.icon('check_circle', size='3rem').classes('text-green-500 mx-auto')
            ui.label("Session complete! 🎉").classes('text-xl font-bold text-green-800 dark:text-green-100')
            done_sub = ui.label('').classes('text-sm text-green-700 dark:text-green-300')
            ui.button('← Back to Library', on_click=lambda: ui.navigate.to('/flashcard_library')) \
                .classes('mt-2 bg-green-600 text-white rounded-xl').props('no-caps')

        done_panel.set_visibility(False)

    # ── helper: load a card into the UI ────────────────────────────────────
    def _load_card():
        q = state['queue']
        idx = state['index']
        if idx >= len(q):
            _show_done()
            return

        card = q[idx]
        front_char.set_text(card.get('front', ''))
        back_text.set_text(card.get('back', ''))
        state['revealed'] = False
        rating_row.set_visibility(False)
        flip_hint.set_visibility(True)
        ui.run_javascript('resetFlip()')
        _update_progress()

    def _update_progress():
        done  = state['done']
        total = state['total']
        pct   = int((done / total) * 100) if total else 100
        progress_bar.style(f'width: {pct}%')
        remaining = len(state['queue']) - state['index']
        session_label.set_text(f'{done} done · {remaining} left')

    def _apply_rating(quality: int):
        q   = state['queue']
        idx = state['index']
        if idx >= len(q):
            return

        card        = q[idx]
        updated     = sm2(card, quality)
        q[idx]      = updated

        # Write back into the deck
        deck_ref = _get_deck(deck_name)
        for i, c in enumerate(deck_ref['cards']):
            if c.get('front') == card.get('front') and c.get('back') == card.get('back'):
                deck_ref['cards'][i] = updated
                break
        _save_deck(deck_name, deck_ref)

        state['index'] += 1
        state['done']  += 1
        _load_card()

    def _show_done():
        front_face.set_visibility(False)
        back_face.set_visibility(False)
        rating_row.set_visibility(False)
        flip_hint.set_visibility(False)
        progress_bar.style('width: 100%')
        session_label.set_text(f'{state["total"]} done · 0 left')
        done_sub.set_text(f'You reviewed {state["total"]} card{"s" if state["total"] != 1 else ""} in this session.')
        done_panel.set_visibility(True)

    # ── handle empty queue ──────────────────────────────────────────────────
    if not due_cards:
        front_face.set_visibility(False)
        back_face.set_visibility(False)
        flip_hint.set_visibility(False)
        session_label.set_text('0 due · 0 left')
        progress_bar.style('width: 100%')

        # Find next due date
        future = []
        for c in all_cards:
            dd = c.get('due_date')
            if dd:
                try:
                    d = datetime.fromisoformat(dd).date() if 'T' in str(dd) else date.fromisoformat(dd)
                    if d > today:
                        future.append(d)
                except Exception:
                    pass

        with done_panel:
            pass  # already built above

        done_panel.set_visibility(True)
        done_sub.set_text(
            f'Next review: {min(future).strftime("%d %b %Y")}' if future else 'No upcoming cards scheduled.'
        )
        ui.run_javascript('document.querySelector(".progress-bar-fill").style.width="100%"')
        return

    # ── initial load ────────────────────────────────────────────────────────
    _load_card()
