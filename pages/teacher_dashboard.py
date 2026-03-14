from nicegui import ui
import auth
from datetime import datetime, date, timedelta


# ---------------------------------------------------------------------------
# Shared helper
# ---------------------------------------------------------------------------

def get_user_icon() -> str:
    if auth.current_user and 'icon' in auth.current_user:
        return auth.current_user['icon']
    return '👤'


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@ui.page('/dashboard')
def dashboard_page():
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    # Apply the user's chosen background gradient, if any.
    # get_bg_css() returns '' for the default theme, so we only inject
    # the style tag when there is actually something to apply.
    bg_css = auth.get_bg_css()
    if bg_css:
        ui.add_head_html(f'<style>{bg_css}</style>')

    if auth.current_user.get('role') == 'admin':
        show_teacher_dashboard()
    else:
        show_user_dashboard()


# ===========================================================================
# TEACHER DASHBOARD
# ===========================================================================

def _student_stats(user: dict) -> dict:
    """Derive summary statistics from a student's card data."""
    today = date.today()
    total = mastered = learning = new = due = 0
    weak_cards = []   # cards where ef has dropped below 2.0

    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            total += 1
            reps = int(card.get('repetitions', 0))
            ef   = float(card.get('ef', 2.5))

            if reps >= 5:
                mastered += 1
            elif reps > 0:
                learning += 1
            else:
                new += 1

            dd = card.get('due_date', '')
            if dd:
                try:
                    if datetime.fromisoformat(dd).date() <= today:
                        due += 1
                except Exception:
                    pass

            # A card is considered weak if ef has fallen below 2.0.
            # The SM-2 floor is 1.3, so 2.0 represents noticeable difficulty.
            if ef < 2.0 and reps > 0:
                weak_cards.append({
                    'deck':  deck.get('name', 'Unknown'),
                    'front': card.get('front', ''),
                    'back':  card.get('back', ''),
                    'ef':    ef,
                    'reps':  reps,
                })

    # Sort weakest first (lowest ef = most struggled)
    weak_cards.sort(key=lambda c: c['ef'])

    return {
        'total':      total,
        'mastered':   mastered,
        'learning':   learning,
        'new':        new,
        'due':        due,
        'weak_cards': weak_cards,
        'pct_mastered': round((mastered / total) * 100) if total else 0,
    }


def show_teacher_dashboard():
    # ── state ──────────────────────────────────────────────────────────────
    selected = {'username': None}

    # ── header — matches student dashboard card style ───────────────────────
    with ui.card().classes('w-full bg-grey-2 dark:bg-grey-9 mb-5'):
        with ui.row().classes('items-center w-full'):
            with ui.avatar(size='lg', color='primary'):
                ui.label(get_user_icon()).classes('text-2xl')
            ui.label(f'Welcome, {auth.current_user["full_name"]}!') \
                .classes('text-2xl font-medium')
            ui.badge('Teacher').classes('ml-2 bg-purple-600 text-white text-xs')
            ui.label(datetime.now().strftime('%A, %d %B %Y')) \
                .classes('ml-auto opacity-70 text-lg font-medium')
            clock = ui.label('Waiting...').classes('ml-2 opacity-70 text-2xl font-medium')
            ui.timer(1.0, lambda: clock.set_text(datetime.now().strftime('%H:%M')))
            ui.button(icon='settings', on_click=lambda: ui.navigate.to('/preference_settings')) \
                .props('flat round').classes('ml-2 text-grey-6')

    # ── two-column layout ───────────────────────────────────────────────────
    with ui.row().classes('w-full gap-6 items-start'):

        # ── LEFT: student roster ────────────────────────────────────────────
        with ui.card().classes('w-5/12 p-4'):
            ui.label('Students').classes('font-semibold text-grey-7 mb-3')

            students = {
                uname: udata
                for uname, udata in auth.users.items()
                if udata.get('role') != 'admin'
            }

            if not students:
                ui.label('No student accounts yet.').classes('text-grey-5 italic')
            else:
                for uname, udata in students.items():
                    stats = _student_stats(udata)
                    is_sel = uname == selected['username']

                    row_classes = (
                        'w-full items-center gap-3 px-3 py-3 rounded-xl cursor-pointer '
                        + ('bg-blue-50 dark:bg-blue-900 border border-blue-200 dark:border-blue-700'
                           if is_sel else
                           'hover:bg-grey-2 dark:hover:bg-grey-8 border border-transparent')
                    )

                    def _select(u=uname):
                        selected['username'] = u
                        _rebuild_detail()

                    with ui.row().classes(row_classes).on('click', _select):
                        with ui.avatar(size='md', color='primary' if is_sel else 'grey-4'):
                            ui.label(udata.get('icon', '👤')).classes('text-lg')
                        with ui.column().classes('flex-1 gap-0'):
                            ui.label(udata.get('full_name', uname)) \
                                .classes('font-medium text-grey-8 dark:text-grey-2 text-sm')
                            ui.label(f'@{uname}').classes('text-xs text-grey-5')
                        with ui.column().classes('items-end gap-0'):
                            # Mastery progress pill
                            pct = stats['pct_mastered']
                            colour = 'text-green-600' if pct >= 50 else 'text-orange-500' if pct >= 20 else 'text-red-500'
                            ui.label(f'{pct}% mastered').classes(f'text-xs font-semibold {colour}')
                            if stats['weak_cards']:
                                ui.label(f'⚠ {len(stats["weak_cards"])} weak').classes('text-xs text-red-400')
                            if stats['due']:
                                ui.label(f'{stats["due"]} due').classes('text-xs text-orange-500')

        # ── RIGHT: student detail ────────────────────────────────────────────
        detail_panel = ui.column().classes('flex-1 gap-4')

        def _rebuild_detail():
            detail_panel.clear()
            with detail_panel:
                uname = selected['username']
                if not uname:
                    with ui.card().classes('w-full p-8 items-center text-center'):
                        ui.icon('person_search', size='3rem').classes('text-grey-4 mx-auto')
                        ui.label('Select a student to view their profile.') \
                            .classes('text-grey-5 mt-2')
                    return

                udata = auth.users.get(uname, {})
                stats = _student_stats(udata)

                # ── summary stat chips ──────────────────────────────────────
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('person').classes('text-grey-5')
                        ui.label(udata.get('full_name', uname)) \
                            .classes('font-semibold text-grey-8')
                        ui.label(f'@{uname}').classes('text-sm text-grey-5')

                    with ui.grid(columns=4).classes('w-full gap-3'):
                        for label, value, colour in [
                            ('Total cards',  stats['total'],    'text-grey-7'),
                            ('Mastered',     stats['mastered'], 'text-green-600'),
                            ('Learning',     stats['learning'], 'text-yellow-600'),
                            ('Due today',    stats['due'],      'text-orange-500'),
                        ]:
                            with ui.card().classes('p-3 text-center'):
                                ui.label(str(value)).classes(f'text-2xl font-bold {colour}')
                                ui.label(label).classes('text-xs text-grey-5')

                # ── weakness analysis ───────────────────────────────────────
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('warning', color='orange').classes('')
                        ui.label('Weak Cards').classes('font-semibold text-grey-8')
                        ui.label('(easiness factor < 2.0 — student is struggling)') \
                            .classes('text-xs text-grey-5')

                    if not stats['weak_cards']:
                        ui.label('No weak cards — all cards are performing well.') \
                            .classes('text-green-600 text-sm italic')
                    else:
                        # Group by deck
                        by_deck: dict[str, list] = {}
                        for wc in stats['weak_cards']:
                            by_deck.setdefault(wc['deck'], []).append(wc)

                        for deck_name, cards in by_deck.items():
                            ui.label(deck_name).classes(
                                'text-xs font-medium text-grey-6 uppercase tracking-wide mt-2 mb-1'
                            )
                            for wc in cards:
                                ef_pct = round(((wc['ef'] - 1.3) / (2.5 - 1.3)) * 100)
                                bar_colour = (
                                    'bg-red-400' if ef_pct < 30 else
                                    'bg-orange-400' if ef_pct < 60 else
                                    'bg-yellow-400'
                                )
                                with ui.row().classes('w-full items-center gap-3 py-1'):
                                    ui.label(wc['front']).classes(
                                        'text-lg font-light w-12 text-center shrink-0'
                                    )
                                    with ui.column().classes('flex-1 gap-0'):
                                        ui.label(wc['back']).classes('text-xs text-grey-6 truncate')
                                        # EF progress bar
                                        with ui.element('div').classes(
                                            'w-full bg-grey-3 rounded-full h-1.5 mt-1'
                                        ):
                                            ui.element('div').classes(
                                                f'{bar_colour} h-1.5 rounded-full'
                                            ).style(f'width: {ef_pct}%')
                                    ui.label(f'EF {wc["ef"]:.2f}').classes(
                                        'text-xs text-grey-5 shrink-0'
                                    )
                                    ui.label(f'{wc["reps"]}× reviewed').classes(
                                        'text-xs text-grey-5 shrink-0'
                                    )

                # ── deck overview ───────────────────────────────────────────
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('library_books').classes('text-grey-5')
                        ui.label('Deck Overview').classes('font-semibold text-grey-8')

                    today = date.today()
                    for deck in udata.get('decks', []):
                        cards = deck.get('cards', [])
                        d_total    = len(cards)
                        d_mastered = sum(1 for c in cards if int(c.get('repetitions', 0)) >= 5)
                        d_new      = sum(1 for c in cards if int(c.get('repetitions', 0)) == 0)
                        d_due      = sum(1 for c in cards if _is_due_today(c, today))
                        d_weak     = sum(
                            1 for c in cards
                            if float(c.get('ef', 2.5)) < 2.0 and int(c.get('repetitions', 0)) > 0
                        )

                        with ui.row().classes('w-full items-center gap-2 py-2 border-b border-grey-2'):
                            ui.label(deck.get('name', 'Untitled')) \
                                .classes('flex-1 text-sm font-medium text-grey-7')
                            for txt, col in [
                                (f'{d_mastered}/{d_total}', 'text-green-600'),
                                (f'{d_due} due',            'text-orange-500'),
                                (f'{d_new} new',            'text-blue-500'),
                                (f'{d_weak} weak',          'text-red-400' if d_weak else 'text-grey-4'),
                            ]:
                                ui.label(txt).classes(f'text-xs font-medium {col} shrink-0')

                # ── intervention: add a card to a student's deck ────────────
                with ui.card().classes('w-full p-4'):
                    with ui.row().classes('items-center gap-2 mb-3'):
                        ui.icon('add_card').classes('text-grey-5')
                        ui.label('Add a Card').classes('font-semibold text-grey-8')
                        ui.label('Push a targeted card directly to a student\'s deck') \
                            .classes('text-xs text-grey-5')

                    deck_names = [d.get('name', '') for d in udata.get('decks', [])]
                    deck_select = ui.select(
                        options=deck_names,
                        label='Select deck',
                        value=deck_names[0] if deck_names else None
                    ).props('outlined dense').classes('w-full mb-3')

                    front_in = ui.input(placeholder='Front (character / question)') \
                        .props('outlined dense').classes('w-full mb-2')
                    back_in  = ui.textarea(placeholder='Back (reading / answer)') \
                        .props('outlined autogrow dense').classes('w-full mb-3')

                    def _add_card_to_student(u=uname):
                        deck_name = deck_select.value
                        front     = front_in.value.strip()
                        back      = back_in.value.strip()

                        if not deck_name or not front or not back:
                            ui.notify('Please fill in all fields.', type='warning')
                            return

                        student = auth.users.get(u)
                        if not student:
                            return

                        target_deck = next(
                            (d for d in student.get('decks', []) if d.get('name') == deck_name),
                            None
                        )
                        if not target_deck:
                            ui.notify('Deck not found.', type='negative')
                            return

                        # New card is immediately due so the student sees it today
                        new_card = {
                            'front':       front,
                            'back':        back,
                            'repetitions': 0,
                            'interval':    0,
                            'ef':          2.5,
                            'due_date':    datetime.now().isoformat(),
                        }
                        target_deck['cards'].append(new_card)
                        auth.save_users()
                        ui.notify(
                            f'Card added to "{deck_name}" for {student.get("full_name", u)}.',
                            type='positive'
                        )
                        front_in.set_value('')
                        back_in.set_value('')
                        # Rebuild to reflect updated stats
                        _rebuild_detail()

                    ui.button('Add card', icon='add') \
                        .props('unelevated no-caps') \
                        .classes('bg-primary text-white rounded-lg w-full') \
                        .on('click', _add_card_to_student)

        # Initial empty state
        _rebuild_detail()


# ---------------------------------------------------------------------------
# Helper used inside teacher dashboard
# ---------------------------------------------------------------------------

def _is_due_today(card: dict, today: date) -> bool:
    dd = card.get('due_date', '')
    if not dd:
        return True
    try:
        return datetime.fromisoformat(dd).date() <= today
    except Exception:
        return True


# ===========================================================================
# STUDENT DASHBOARD
# ===========================================================================

def show_user_dashboard():
    with ui.card().classes('w-full max-w-5xl mx-auto bg-grey-2 dark:bg-grey-9'):
        with ui.row().classes('items-center w-full'):
            with ui.avatar(size='lg', color='primary'):
                ui.label(get_user_icon()).classes('text-2xl')
            ui.label(f'Welcome back, {auth.current_user["full_name"]}!') \
                .classes('text-2xl font-medium align-left')
            ui.label(datetime.now().strftime('%A, %d %B %Y')) \
                .classes('ml-auto opacity-70 align-center text-lg font-medium')
            clock = ui.label('Waiting...').classes('ml-2 opacity-70 align-right text-2xl font-medium')
            ui.timer(1.0, lambda: clock.set_text(datetime.now().strftime('%H:%M')))

    with ui.card().classes('w-full max-w-5xl mx-auto p-6 gap-8'):
        with ui.column().classes('gap-2 w-full max-h-48 overflow-y-auto'):
            ui.label('Cards due today').classes('text-sm font-medium text-grey-6 uppercase tracking-wide mb-1')

            has_due_cards = False
            for deck in auth.current_user.get('decks', []):
                due_cards = [
                    c for c in deck.get('cards', [])
                    if 'due_date' in c and datetime.fromisoformat(c['due_date']) <= datetime.now()
                ]
                if due_cards:
                    has_due_cards = True
                    ui.label(
                        f'You have {len(due_cards)} cards due for review in "{deck["name"]}"'
                    ).classes('text-lg text-grey-7 mt-0')

            if not has_due_cards:
                ui.label('You are done for today! 🎉').classes('text-lg text-grey-7 mt-0 font-semibold')

    with ui.card().props('rounded').classes('w-full max-w-5xl mx-auto p-6 gap-8'):
        ui.label('Navigate to different functions').classes('text-lg text-grey-7 mt-0')

        with ui.grid(columns=3).classes('w-full gap-5'):
            with ui.button(on_click=lambda: ui.navigate.to('/flashcard_library')) \
                    .classes('cursor-pointer hover:scale-105 transition-transform bg-white dark:bg-grey-8 '
                             'flex flex-col items-center justify-center p-8 gap-4 shadow-sm hover:shadow-md '
                             'bg-grey-2 dark:bg-grey-7'):
                ui.icon('library_books', size='4rem') \
                    .classes('text-teal-600 dark:text-teal-400 bg-grey-2 dark:bg-grey-7 rounded-full p-2')
                ui.label('Flashcard library').classes('text-lg font-medium text-center text-grey-7')

            with ui.button(on_click=lambda: ui.navigate.to('/progress_visualiser')) \
                    .classes('cursor-pointer hover:scale-105 transition-transform bg-white dark:bg-grey-8 '
                             'flex flex-col items-center justify-center p-8 gap-4 shadow-sm hover:shadow-md '
                             'bg-grey-2 dark:bg-grey-7'):
                ui.icon('trending_up', size='4rem') \
                    .classes('text-purple-600 dark:text-purple-400 bg-grey-2 dark:bg-grey-7 rounded-full p-2')
                ui.label('Progress visualiser').classes('text-lg font-medium text-center text-grey-7')

            with ui.button(on_click=lambda: ui.navigate.to('/preference_settings')) \
                    .classes('cursor-pointer hover:scale-105 transition-transform bg-white dark:bg-grey-8 '
                             'flex flex-col items-center justify-center p-8 gap-4 shadow-sm hover:shadow-md '
                             'bg-grey-2 dark:bg-grey-7'):
                ui.icon('settings', size='4rem') \
                    .classes('text-orange-600 dark:text-orange-400 bg-grey-2 dark:bg-grey-7 rounded-full p-2')
                ui.label('Preference Settings').classes('text-lg font-medium text-center text-grey-7')
