from django.urls import path
from .views import *

app_name = 'gnome_main'

urlpatterns = [
    path('', main, name='main'),
    path('blog/filter/', BlogFilterView.as_view(), name='blog-filter'),
    path('blog/search/', BlogSearchView.as_view(), name='blog-search'),
    path('blog/<slug:slug>/', PostView.as_view(), name='show-post'),
    path('blog/', BlogView.as_view(), name='blog'),
    path('login/', Login_view.as_view(), name='log-in'),
    path('logout/', Logout_view.as_view(), name='log-out'),
    path('user/<str:slug>/delete/starting/', deleteUserStarting, name='user-delete-starting'),
    path('user/<str:slug>/delete/<str:sign>/', DeleteUserView.as_view(), name='user-delete-confirm'),
    path('user/<str:slug>/change/', ChangeUserInfoView.as_view(), name='profile-change'),
    path('user/<str:slug>/', UserProfile.as_view(), name='user-profile'),
    path('user/password/reset/confrim/<str:uidb64>/<str:token>/', PasswordResetConfrim.as_view(), name='password-reset-confrim'),
    path('user/password/reset/complete/', PasswordResetComplete.as_view(), name='password-reset-complete'),
    path('user/password/reset-done/', PasswordResetDone.as_view(), name='password-reset-done'),
    path('user/password/reset/', PasswordReset.as_view(), name='password-reset'),
    path('register/activate/<str:sign>/', user_activate, name='register-done'),
    path('register/confrim/', RegisterConfrimView.as_view(), name='register-confrim'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('report/<slug:slug>/post/', PostReportView.as_view(), name='post-report'),
    path('report/<slug:slug>/comment/<int:id>/', CommentReportView.as_view(), name='comment-report'),
]
