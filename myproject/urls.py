from django.contrib import admin
from django.urls import path, include
from myapp import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico')),
    path("", include("myapp.urls")),
]


urlpatterns = [
    path('', views.index, name='home'),
    path('pricing/', views.pricing, name='pricing'),
    path('admin/', admin.site.urls),
]