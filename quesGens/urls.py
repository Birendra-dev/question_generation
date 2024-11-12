from django.urls import path

from . import views

urlpatterns = [
    path("", views.generate_mcq, name="generate_mcq"),
    # path("about/", views.about, name="about"),

    path('/login/', views.login_view, name='login'),
    path('/register/', views.register_view, name='register'),
    path('/is_logged_in/', views.is_logged_in, name='is_logged_in'),
    # path('result/',views.result,name='result')
]