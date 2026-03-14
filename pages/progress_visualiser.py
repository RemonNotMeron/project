from nicegui import ui
import auth
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict


def get_user_data():
    user = None
    if hasattr(auth, 'current_username') and auth.current_username in auth.users:
        user = auth.users[auth.current_username]
    else:
        for k, v in auth.users.items():
            if v is auth.current_user:
                user = v
                break
    return user


def calculate_card_stats(user):
    if not user or 'decks' not in user:
        return {
            'total_cards': 0,
            'mastered_cards': 0,
            'learning_cards': 0,
            'new_cards': 0,
            'due_today': 0,
            'total_reviews': 0,
            'study_hours': 0
        }

    total_cards = 0
    mastered_cards = 0
    learning_cards = 0
    new_cards = 0
    due_today = 0
    total_reviews = 0
    today = date.today()

    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            total_cards += 1
            reps = int(card.get('repetitions', 0))
            total_reviews += reps

            if reps >= 5:
                mastered_cards += 1
            elif reps > 0:
                learning_cards += 1
            else:
                new_cards += 1

            due_date = card.get('due_date', '')
            if due_date:
                try:
                    card_due = datetime.fromisoformat(due_date).date()
                    if card_due <= today:
                        due_today += 1
                except Exception:
                    pass

    study_hours = round(total_reviews / 60, 1)

    return {
        'total_cards': total_cards,
        'mastered_cards': mastered_cards,
        'learning_cards': learning_cards,
        'new_cards': new_cards,
        'due_today': due_today,
        'total_reviews': total_reviews,
        'study_hours': study_hours
    }


def get_mastery_timeline(user):
    if not user or 'decks' not in user:
        return [], []

    mastery_data = defaultdict(int)

    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            reps = int(card.get('repetitions', 0))
            if reps >= 5:
                mastery_str = card.get('mastered_date')
                if mastery_str:
                    try:
                        m_date = datetime.fromisoformat(mastery_str).date()
                        mastery_data[m_date] += 1
                        continue
                    except Exception:
                        pass
                mastery_data[date.today()] += 1

    timeline_dates = []
    timeline_mastered = []
    cumulative = 0
    start_date = date.today() - timedelta(days=30)
    total_before_window = sum(count for d, count in mastery_data.items() if d < start_date)
    cumulative = total_before_window

    current = start_date
    while current <= date.today():
        cumulative += mastery_data.get(current, 0)
        timeline_dates.append(current.strftime('%Y-%m-%d'))
        timeline_mastered.append(cumulative)
        current += timedelta(days=1)

    return timeline_dates, timeline_mastered


def get_card_state_breakdown(user):
    if not user or 'decks' not in user:
        return [], []

    states = {'New': 0, 'Learning': 0, 'Mastered': 0}

    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            reps = int(card.get('repetitions', 0))
            if reps >= 5:
                states['Mastered'] += 1
            elif reps > 0:
                states['Learning'] += 1
            else:
                states['New'] += 1

    return list(states.keys()), list(states.values())


def create_mastery_graph():
    user = get_user_data()
    dates, mastered_count = get_mastery_timeline(user)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates,
        y=mastered_count,
        mode='lines+markers',
        name='Cumulative Mastered Cards',
        line=dict(color='#10b981', width=3),
        marker=dict(size=6)
    ))
    fig.update_layout(
        title='Cards Mastered Over Last 30 Days',
        xaxis_title='Date',
        yaxis_title='Cumulative Cards Mastered',
        hovermode='x unified',
        plot_bgcolor='#f9fafb',
        height=400
    )
    return fig


def create_state_breakdown_graph():
    user = get_user_data()
    labels, values = get_card_state_breakdown(user)

    colors = ['#3b82f6', '#f59e0b', '#10b981']
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        marker=dict(colors=colors),
        hoverinfo='label+value+percent'
    )])
    fig.update_layout(
        title='Card States Breakdown',
        height=400
    )
    return fig


@ui.page('/progress_visualiser')
def progress_visualiser():
    user = get_user_data()

    if not user:
        ui.label('Please log in to view progress').classes('text-red-600')
        return

    # ── header ──────────────────────────────────────────────────────────────
    with ui.row().classes('w-full items-center gap-3 mb-1'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')) \
            .props('flat round').classes('text-grey-6')
        ui.label('Progress Visualiser').classes('text-2xl font-bold')

    ui.separator().classes('mb-4')

    with ui.tabs().classes('w-full') as tabs:
        stats_tab = ui.tab('Statistics')
        graph_tab = ui.tab('Graph')

    with ui.tab_panels(tabs, value=stats_tab).classes('w-full'):

        with ui.tab_panel(stats_tab):
            stats = calculate_card_stats(user)

            with ui.grid(columns=2).classes('w-full gap-4'):
                with ui.card().classes('p-6'):
                    ui.label('Total Studying Hours').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['study_hours']}h").classes('text-3xl font-bold text-blue-600')

                with ui.card().classes('p-6'):
                    ui.label('Flashcards in Library').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['total_cards']}").classes('text-3xl font-bold text-purple-600')

                with ui.card().classes('p-6'):
                    ui.label('Flashcards Mastered').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['mastered_cards']}").classes('text-3xl font-bold text-green-600')

                with ui.card().classes('p-6'):
                    ui.label('Cards Due Today').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['due_today']}").classes('text-3xl font-bold text-orange-600')

            with ui.grid(columns=3).classes('w-full gap-4 mt-4'):
                with ui.card().classes('p-6'):
                    ui.label('New Cards').classes('text-sm font-semibold text-gray-600')
                    ui.label(f"{stats['new_cards']}").classes('text-2xl font-bold text-blue-500')

                with ui.card().classes('p-6'):
                    ui.label('Learning').classes('text-sm font-semibold text-gray-600')
                    ui.label(f"{stats['learning_cards']}").classes('text-2xl font-bold text-yellow-500')

                with ui.card().classes('p-6'):
                    ui.label('Total Reviews').classes('text-sm font-semibold text-gray-600')
                    ui.label(f"{stats['total_reviews']}").classes('text-2xl font-bold text-indigo-600')

        with ui.tab_panel(graph_tab):
            with ui.grid(columns=1).classes('w-full gap-4'):
                ui.label('Cards Mastered Over Time').classes('text-lg font-semibold mt-4')
                with ui.element('div').classes('w-full'):
                    ui.plotly(create_mastery_graph()).classes('w-full')

                ui.label('Card States Distribution').classes('text-lg font-semibold mt-6')
                with ui.element('div').classes('w-full'):
                    ui.plotly(create_state_breakdown_graph()).classes('w-full')
