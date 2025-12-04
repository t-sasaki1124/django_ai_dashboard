from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("pricing/", views.pricing, name="pricing"),
    path("comments-table/", views.comments_table, name="comments_table"),
]
