# mailings/urls.py

from django.urls import path
from . import views

app_name = 'mailings'

urlpatterns = [
    path('send/<int:mailing_id>/', views.send_mailing, name='send_mailing'),
    path('dashboard/', views.dashboard, name='dashboard'),  # Дашборд
    path('mailing/<int:mailing_id>/sent/', views.mailing_sent, name='mailing_sent'),
]