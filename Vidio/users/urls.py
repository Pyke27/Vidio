from django.urls import path
from .views import delete_audio, home, profile, RegisterView, AudioFileListView, AudioFileUploadView, search_form

urlpatterns = [
    path('', home, name='home'),
    path('register/', RegisterView.as_view(), name='users-register'),
    path('profile/', profile, name='users-profile'),
    path('delete-audio/<int:audio_id>/', delete_audio, name='delete-audio'),
    path('audio_list/', AudioFileListView.as_view(), name='audio_list'),
    path('upload/', AudioFileUploadView.as_view(), name='audio_upload'),
    path('search/', search_form, name='search_form'),
]
