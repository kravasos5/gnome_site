from django.urls import path
from .views import *

app_name = 'gnome_main'
urlpatterns = [
    path('', main, name='main'),
    path('blog/', blog, name='blog'),
    path('login/', Login_view.as_view(), name='log-in'),
    path('logout/', Logout_view.as_view(), name='log-out'),
    path('register/', register_view, name='register'),
    path('register-confrim/', register_confrim, name='register-confrim'),
    path('register-complete/', register_complete, name='register-complete'),
]