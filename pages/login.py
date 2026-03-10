from nicegui import ui
from auth import users, pwd_context, is_authenticated, login_success, login_failed


@ui.page('/')
def login_page():
    # Redirect if already logged in
    if is_authenticated():
        ui.navigate.to('/dashboard')
        return

    with ui.card().props('rounded').classes('w-96 mx-auto mt-24 p-8 shadow-2xl'):
        ui.label('Sign in').classes('text-3xl font-bold text-center mb-5 mx-auto')

        # Username input
        username_input = ui.input(
            label='Username',
            placeholder='Enter your username'
        ).props('borderless filled').classes('w-full mb-4')

        # Password input
        password_input = ui.input(
            label='Password',
            placeholder='Enter your password',
            password=True,
            password_toggle_button=True
        ).props('outlined filled').classes('w-full mb-0')

        def try_login():
            username = username_input.value.strip().lower()
            password = password_input.value

            user = users.get(username)
            if user and pwd_context.verify(password, user["password_hash"]):
                login_success(username)
            else:
                login_failed()

        ui.button('Sign In', on_click=try_login).classes('w-full mt-20')

        with ui.row().classes('justify-center text-sm gap-1 mx-auto'):
            ui.label("Don't have an account?")
            ui.link('Create account', '/registeration').classes('text-blue-500 hover:underline')

