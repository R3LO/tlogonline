from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _


@login_required
def index(request):
    """
    Главная страница приложения log_online
    """
    return render(request, 'log_online/index.html', {
        'title': _('Онлайн лог'),
    })
