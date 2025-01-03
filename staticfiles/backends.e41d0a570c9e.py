from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class PhoneOrUsernameBackend(ModelBackend):
    """
    Кастомный бэкэнд для аутентификации по логину или номеру телефона.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        # Проверяем логин или номер телефона
        try:
            if username.isdigit():  # Если это номер телефона
                if username[0] == '0': # Проверяем если номер записывается не с 380
                    username = '38' + username    
                user = User.objects.get(phone=username)
            else:  # Если это логин
                user = User.objects.get(username=username)
        except User.DoesNotExist:
            return None

        # Проверяем пароль
        if user.check_password(password) and self.user_can_authenticate(user):
            return user

        return None