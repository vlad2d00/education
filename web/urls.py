from django.urls import path
from .views import *


urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('', home_view, name='home'),
    path('rating/', rating_view, name='rating'),
    path('achievements/', achievements_view, name='achievements'),
    path('roadmap/', roadmap_view, name='roadmap'),
    path('links/', links_view, name='links'),
    path('feedback/', feedback_view, name='feedback'),
    path('control/', control_view, name='control'),
    path('notices/', notices_view, name='notices'),

    path('users/<slug:username>/', user_view, name='user'),
    path('edit/', edit_user_view, name='edit-user'),
    path('projects/<int:project_id>/', project_view, name='project'),
    path('posts/<int:post_id>/', post_view, name='post'),
    path('tasks/<int:task_id>/', task_view, name='task'),
    path('tests/<int:test_id>/', test_view, name='test'),
    path('events/<int:event_id>/', event_view, name='event'),

]
