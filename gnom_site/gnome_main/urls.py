from django.urls import path
from .views import *

app_name = 'gnome_main'

urlpatterns = [
    path('', Main.as_view(), name='main'),

    path('blog/author/<slug:slug>/filter/', AuthorPostsFilteredView.as_view(), name='blog-filter-author'),
    path('blog/author/<slug:slug>/search/', AuthorPostsSearchView.as_view(), name='blog-search-author'),
    path('blog/author/<slug:slug>/', AuthorPostsView.as_view(), name='blog-author'),

    path('blog/filter/', BlogFilterView.as_view(), name='blog-filter'),
    path('blog/search/', BlogSearchView.as_view(), name='blog-search'),
    path('blog/<slug:slug>/', PostView.as_view(), name='show-post'),
    path('blog/', BlogView.as_view(), name='blog'),

    path('login/', Login_view.as_view(), name='log-in'),
    path('logout/', Logout_view.as_view(), name='log-out'),
    path('user/<str:slug>/delete/starting/', deleteUserStarting, name='user-delete-starting'),
    path('user/<str:slug>/delete/<str:sign>/', DeleteUserView.as_view(), name='user-delete-confirm'),
    path('user/<str:slug>/change/', ChangeUserInfoView.as_view(), name='profile-change'),
    path('user/<slug:slug>/studio/<str:section>/', StudioDetailView.as_view(), name='studio-detail'),
    path('user/<slug:slug>/studio/', UserStudio.as_view(), name='studio'),
    path('user/<str:slug>/', UserProfile.as_view(), name='user-profile'),
    path('user/password/reset/confrim/<str:uidb64>/<str:token>/', PasswordResetConfrim.as_view(), name='password-reset-confrim'),
    path('user/password/reset/complete/', PasswordResetComplete.as_view(), name='password-reset-complete'),
    path('user/password/reset-done/', PasswordResetDone.as_view(), name='password-reset-done'),
    path('user/password/reset/', PasswordReset.as_view(), name='password-reset'),

    path('register/activate/<str:sign>/', user_activate, name='register-done'),
    path('register/confirm/', RegisterConfrimView.as_view(), name='register-confirm'),
    path('register/', RegisterUserView.as_view(), name='register'),

    path('report/<slug:slug>/post/', PostReportView.as_view(), name='post-report'),
    path('report/<slug:slug>/comment/<int:id>/', CommentReportView.as_view(), name='comment-report'),

    path('post/update/<slug:slug>/', PostUpdateView.as_view(), name='update-post'),
    path('post/delete/<slug:slug>/', PostDeleteView.as_view(), name='delete-post'),
    path('post/new/', PostCreateView.as_view(), name='create-post'),

    path('notifications/<slug:slug>/', NotificationView.as_view(), name='notifications'),

    path('access-denied/', AccessDenied.as_view(), name='access-denied'),

    path('favourites-likes-starting/', FavLikeStarting.as_view(), name='user-favourites-likes-starting'),
    path('favourites/', UserFavourites.as_view(), name='user-favourites'),
    path('liked/', UserLiked.as_view(), name='user-liked'),
    path('history/', UserHistory.as_view(), name='user-history'),
]
