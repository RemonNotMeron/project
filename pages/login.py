from nicegui import ui
#from auth import users, pwd_context, login_success, login_failed


@ui.page('/login')
def login_page():
    #Page title
    ui.label('Sign in').classes('text-3xl font-bold text-center mb-5 mx-auto')

    #text input for username and password
    username_input = ui.input(
                label='Username',
                placeholder='Enter your username'
            ).props('borderless filled').classes('w-full mb-4')

    password_input = ui.input(
                label='Password',
                placeholder='Enter your password',
                password=True,
                password_toggle_button=True
            ).props('outlined filled').classes('w-full mb-0')

    #link for forgot password
    ui.link('Forgot Password?', '#').classes('text-blue-500 hover:underline mb-10')


    #sign in button
    """def try_login():
        username = username_input.value.strip().lower()
        password = password_input.value

        user = users.get(username)
        if user and pwd_context.verify(password, user["password_hash"]):
            login_success(username)
        else:
            login_failed()"""

    ui.button('Sign In').classes('w-full mt-4')