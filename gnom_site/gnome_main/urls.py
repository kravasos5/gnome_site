from django.urls import path
from .views import *

app_name = 'gnome_main'

urlpatterns = [
    path('', main, name='main'),
    path('blog/', blog, name='blog'),
    path('login/', Login_view.as_view(), name='log-in'),
    path('logout/', Logout_view.as_view(), name='log-out'),
    path('user/<str:slug>/change/', ChangeUserInfoView.as_view(), name='profile-change'),
    path('user/<str:slug>/', UserProfile.as_view(), name='user-profile'),
    path('register/activate/<str:sign>/', user_activate, name='register-done'),
    path('register/confrim/', RegisterConfrimView.as_view(), name='register-confrim'),
    path('register/', RegisterUserView.as_view(), name='register'),
]
