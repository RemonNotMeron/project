from nicegui import ui
import auth


@ui.page('/registeration')
def registration_page():
    ui.label('Create Account').classes('text-3xl font-bold text-center mb-5 mx-auto')
    # Username input
    create_username = ui.input(
        label='Username',
        placeholder='Enter your username'
    ).props('borderless filled').classes('w-full mb-2')

    #full name input
    create_full_name = ui.input(
        label='Full Name',
        placeholder='Enter your full name'
    ).props('borderless filled').classes('w-full mb-2')

    # Password input
    create_pw = ui.input(
        label='Password',
        placeholder='Enter your password',
        password=True,
        password_toggle_button=True
    ).props('outlined filled dense').classes('w-full mb-2')
    # Confirm Password input
    confirm_pw = ui.input(
        label='Confirm Password',
        placeholder='Confirm your password',
        password=True,
        password_toggle_button=True
    ).props('outlined filled dense').classes('w-full mb-0')


    def try_register():
        username = create_username.value.strip().lower()
        full_name = create_full_name.value.strip()
        pw = create_pw.value
        confirm = confirm_pw.value

        if not username or not full_name or not pw:
            ui.notify('Please fill in all fields.', type='negative')
            return
        if pw != confirm:
            ui.notify('Passwords do not match.', type='negative')
            return
        if username in auth.users:
            ui.notify('Username already exists.', type='negative')
            return

        # Add the new user via helper (also saves to disk)
        if not auth.add_user(username, full_name, pw):
            ui.notify('Username already exists or invalid.', type='negative')
            return

        ui.notify('Account created successfully. Signing you in...', type='positive')
        # Auto-login and go to dashboard
        auth.login_success(username)

    ui.button('Register', on_click=try_register).classes('w-full mt-4')