from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.contrib import messages

def add_message_success_login(sender, user, request, **kwargs):
    messages.success(request, f'Добро пожаловать, {user.username}')

def add_message_success_logout(sender, user, request, **kwargs):
    messages.success(request, f'Удачи, {user.username}')

def add_message_error_login(sender, request, **kwargs):
    messages.error(request, 'Ошибка входа')

user_logged_in.connect(add_message_success_login)
user_logged_out.connect(add_message_success_logout)
user_login_failed.connect(add_message_error_login)