from django.urls import path

from . import views

urlpatterns = [
    path("", views.generate_mcq, name="generate_mcq"),
    # path("about/", views.about, name="about"),
]
