from nicegui import ui
import auth
import base64
from pathlib import Path


# Available emoji icons for user customization
EMOJI_OPTIONS = ['👤', '🎓', '📚', '🧠', '⭐', '🎯', '✨', '🚀', '💡', '🎨', '📝', '🏆']


def get_user_icon():
    """Get user's custom icon or default"""
    if auth.current_user and 'icon' in auth.current_user:
        return auth.current_user['icon']
    return '👤'


def set_user_icon(icon: str):
    """Set user's custom icon"""
    if auth.current_user:
        auth.current_user['icon'] = icon
        auth.save_users()
        ui.notify(f"Icon changed to {icon}", type='positive')


def change_full_name(new_name: str):
    """Change user's full name"""
    if not new_name or not new_name.strip():
        ui.notify('Name cannot be empty', type='negative')
        return False
    
    if auth.current_user:
        auth.current_user['full_name'] = new_name.strip()
        auth.save_users()
        ui.notify('Name updated successfully', type='positive')
        return True
    return False


def change_username(new_username: str):
    """Change user's username"""
    new_username = new_username.strip().lower()
    
    if not new_username:
        ui.notify('Username cannot be empty', type='negative')
        return False
    
    if new_username in auth.users and new_username != auth.current_username:
        ui.notify('Username already taken', type='negative')
        return False
    
    if auth.current_user and auth.current_username:
        # Get the current user data
        user_data = auth.users[auth.current_username]
        
        # Remove old username entry
        del auth.users[auth.current_username]
        
        # Add new username entry with same data
        auth.users[new_username] = user_data
        
        # Update session
        auth.current_username = new_username
        auth.current_user = auth.users[new_username]
        
        auth.save_users()
        ui.notify('Username updated successfully', type='positive')
        return True
    return False


def change_password(current_password: str, new_password: str, confirm_password: str):
    """Change user's password"""
    if not current_password or not new_password or not confirm_password:
        ui.notify('Please fill in all password fields', type='negative')
        return False
    
    if new_password != confirm_password:
        ui.notify('New passwords do not match', type='negative')
        return False
    
    if len(new_password) < 6:
        ui.notify('Password must be at least 6 characters', type='negative')
        return False
    
    if auth.current_user and auth.current_username:
        # Verify current password
        if not auth.pwd_context.verify(current_password, auth.current_user['password_hash']):
            ui.notify('Current password is incorrect', type='negative')
            return False
        
        # Update password
        auth.current_user['password_hash'] = auth.pwd_context.hash(new_password)
        auth.save_users()
        ui.notify('Password updated successfully', type='positive')
        return True
    return False


@ui.page('/preference_settings')
def preference_settings():
    if not auth.is_authenticated():
        ui.navigate.to('/')
        return

    user = auth.current_user

    # ── header ──────────────────────────────────────────────────────────────
    with ui.row().classes('w-full items-center gap-3 mb-1'):
        ui.button(icon='arrow_back', on_click=lambda: ui.navigate.to('/dashboard')) \
            .props('flat round').classes('text-grey-6')
        ui.label('Preferences').classes('text-2xl font-semibold text-grey-8 dark:text-grey-2')

    ui.separator().classes('mb-6')

    # ── two-column layout ───────────────────────────────────────────────────
    with ui.row().classes('w-full gap-6 items-start'):

        # ── LEFT COLUMN ─────────────────────────────────────────────────────
        with ui.column().classes('flex-1 gap-5'):

            # Card 1 — Avatar
            with ui.card().classes('w-full p-5'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('account_circle').classes('text-grey-5')
                    ui.label('Avatar').classes('font-semibold text-grey-7')
                with ui.row().classes('items-center gap-4 mb-4'):
                    with ui.avatar(size='xl', color='primary'):
                        current_icon_label = ui.label(get_user_icon()).classes('text-3xl')
                    with ui.column().classes('gap-0'):
                        ui.label(user.get('full_name', '')).classes('font-medium text-grey-8')
                        ui.label(f'@{auth.current_username}').classes('text-sm text-grey-5')
                ui.label('Choose icon').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-2')
                with ui.row().classes('gap-2 flex-wrap'):
                    for emoji in EMOJI_OPTIONS:
                        is_sel = emoji == get_user_icon()
                        ui.button(emoji) \
                            .props('unelevated' if is_sel else 'flat') \
                            .classes('text-xl w-12 h-12 rounded-xl ' +
                                     ('bg-primary text-white' if is_sel else 'hover:bg-grey-2')) \
                            .on('click', lambda e=emoji: (set_user_icon(e), current_icon_label.set_text(e)))

            # Card 2 — Account details
            with ui.card().classes('w-full p-5'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('badge').classes('text-grey-5')
                    ui.label('Account Details').classes('font-semibold text-grey-7')
                ui.label('Full name').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-1')
                name_input = ui.input(placeholder='Your display name', value=user.get('full_name', '')) \
                    .props('outlined dense').classes('w-full mb-4')
                ui.label('Username').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-1')
                username_input = ui.input(placeholder='your_username', value=auth.current_username) \
                    .props('outlined dense').classes('w-full mb-4')
                def save_account():
                    changed = False
                    if name_input.value.strip() != user.get('full_name', ''):
                        if not change_full_name(name_input.value):
                            name_input.set_value(user.get('full_name', '')); return
                        changed = True
                    if username_input.value.strip().lower() != auth.current_username:
                        if not change_username(username_input.value):
                            username_input.set_value(auth.current_username); return
                        changed = True
                    if changed:
                        ui.navigate.to('/preference_settings')
                ui.button('Save changes', icon='save').props('unelevated no-caps') \
                    .classes('bg-primary text-white rounded-lg w-full').on('click', save_account)



        # ── RIGHT COLUMN ────────────────────────────────────────────────────
        with ui.column().classes('flex-1 gap-5'):

            # Card 4 — Security
            with ui.card().classes('w-full p-5'):
                with ui.row().classes('items-center gap-2 mb-4'):
                    ui.icon('lock').classes('text-grey-5')
                    ui.label('Security').classes('font-semibold text-grey-7')
                ui.label('Current password').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-1')
                current_pwd = ui.input(placeholder='Enter current password', password=True, password_toggle_button=True) \
                    .props('outlined dense').classes('w-full mb-3')
                ui.label('New password').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-1')
                new_pwd = ui.input(placeholder='At least 6 characters', password=True, password_toggle_button=True) \
                    .props('outlined dense').classes('w-full mb-3')
                ui.label('Confirm new password').classes('text-xs font-medium text-grey-6 uppercase tracking-wide mb-1')
                confirm_pwd = ui.input(placeholder='Repeat new password', password=True, password_toggle_button=True) \
                    .props('outlined dense').classes('w-full mb-4')
                def update_password():
                    if change_password(current_pwd.value, new_pwd.value, confirm_pwd.value):
                        current_pwd.set_value(''); new_pwd.set_value(''); confirm_pwd.set_value('')
                ui.button('Update password', icon='lock_reset').props('unelevated no-caps') \
                    .classes('bg-blue-600 text-white rounded-lg w-full').on('click', update_password)

            # Card 5 — Sign out
            with ui.card().classes('w-full p-5'):
                with ui.row().classes('items-center gap-2 mb-3'):
                    ui.icon('logout').classes('text-grey-5')
                    ui.label('Session').classes('font-semibold text-grey-7')
                ui.label(f'Signed in as {user.get("full_name", auth.current_username)}') \
                    .classes('text-sm text-grey-6 mb-4')
                def sign_out():
                    ui.notify('Signing out…', type='info')
                    auth.logout()
                ui.button('Sign out', icon='logout').props('unelevated no-caps color=red') \
                    .classes('bg-red-600 text-white rounded-lg w-full').on('click', sign_out)
