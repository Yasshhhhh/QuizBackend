from django.urls import path
from . import views

urlpatterns = [
    path('', views.text_prompt, name='hello_world'),
    path('pdf', views.pdf_prompt, name='pdf'),
    path('submit',views.submit_quiz,name='submit'),
    path('login',views.login_view,name='login'),
    path('logout',views.logout_view,name='logout'),
    path('history',views.user_history,name='history'),
    path('register',views.register_view,name='register'),
    path('hello',views.hello_world,name='hello')

]