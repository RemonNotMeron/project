from nicegui import ui
import auth
from datetime import date, datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict


def get_user_data():
    """Get current user data"""
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
    """Calculate statistics from user's flashcards"""
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
    mastered_cards = 0  # repetitions >= 5
    learning_cards = 0  # 1 <= repetitions < 5
    new_cards = 0       # repetitions == 0
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
                except:
                    pass
    
    # Estimate study hours (1 minute per review as rough estimate)
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
    """Generate timeline data of cards mastered over time using the mastered_date field"""
    if not user or 'decks' not in user:
        return [], []
    
    mastery_data = defaultdict(int)
    
    for deck in user.get('decks', []):
        for card in deck.get('cards', []):
            reps = int(card.get('repetitions', 0))
            if reps >= 5:
                # 1. Try to use the explicit mastered_date set during the review
                mastery_str = card.get('mastered_date')
                if mastery_str:
                    try:
                        m_date = datetime.fromisoformat(mastery_str).date()
                        mastery_data[m_date] += 1
                        continue # Move to next card
                    except:
                        pass
                
                # 2. Fallback: If repetitions >= 5 but no date exists (legacy cards),
                # we treat it as mastered "today" or use a neutral past date.
                mastery_data[date.today()] += 1
    
    # Generate timeline from 30 days ago to today
    timeline_dates = []
    timeline_mastered = []
    cumulative = 0
    
    # Get all-time mastery count before the 30-day window to start cumulative correctly
    start_date = date.today() - timedelta(days=30)
    
    # Calculate initial cumulative for cards mastered before our 30-day window
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
    """Get breakdown of card states for pie chart"""
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
    """Create graph showing cards mastered over time"""
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
    """Create pie chart of card states"""
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
    
    ui.button('Back to Dashboard', icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')).props('flat')
    with ui.row().classes('w-full items-center mb-4'):
        ui.label('Progress Visualiser').classes('text-2xl font-bold flex-grow')
        
    
    # Create tabs for Statistics and Graph
    with ui.tabs().classes('w-full') as tabs:
        stats_tab = ui.tab('Statistics')
        graph_tab = ui.tab('Graph')
    
    with ui.tab_panels(tabs).classes('w-full'):
        # Statistics Tab
        with ui.tab_panel(stats_tab):
            stats = calculate_card_stats(user)
            
            with ui.grid(columns=2).classes('w-full gap-4'):
                # Total Studying Hours
                with ui.card().classes('p-6'):
                    ui.label('Total Studying Hours').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['study_hours']}h").classes('text-3xl font-bold text-blue-600')
                
                # Flashcards in Library
                with ui.card().classes('p-6'):
                    ui.label('Flashcards in Library').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['total_cards']}").classes('text-3xl font-bold text-purple-600')
                
                # Flashcards Remembered (Mastered)
                with ui.card().classes('p-6'):
                    ui.label('Flashcards Mastered').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['mastered_cards']}").classes('text-3xl font-bold text-green-600')
                
                # Cards Due Today
                with ui.card().classes('p-6'):
                    ui.label('Cards Due Today').classes('text-lg font-semibold text-gray-600')
                    ui.label(f"{stats['due_today']}").classes('text-3xl font-bold text-orange-600')
            
            # Additional stats row
            with ui.grid(columns=3).classes('w-full gap-4 mt-4'):
                # New Cards
                with ui.card().classes('p-6'):
                    ui.label('New Cards').classes('text-sm font-semibold text-gray-600')
                    ui.label(f"{stats['new_cards']}").classes('text-2xl font-bold text-blue-500')
                
                # Learning Cards
                with ui.card().classes('p-6'):
                    ui.label('Learning').classes('text-sm font-semibold text-gray-600')
                    ui.label(f"{stats['learning_cards']}").classes('text-2xl font-bold text-yellow-500')
                
                # Total Reviews
                with ui.card().classes('p-6'):
                    ui.label('Total Reviews').classes('text-sm font-semibold text-gray-600')
                    ui.label(f"{stats['total_reviews']}").classes('text-2xl font-bold text-indigo-600')
        
        # Graph Tab
        with ui.tab_panel(graph_tab):
            with ui.grid(columns=1).classes('w-full gap-4'):
                # Mastery Timeline Graph
                ui.label('Cards Mastered Over Time').classes('text-lg font-semibold mt-4')
                with ui.element('div').classes('w-full'):
                    ui.plotly(create_mastery_graph()).classes('w-full')
                
                # Card State Breakdown
                ui.label('Card States Distribution').classes('text-lg font-semibold mt-6')
                with ui.element('div').classes('w-full'):
                    ui.plotly(create_state_breakdown_graph()).classes('w-full')
    