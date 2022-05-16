from django.urls import re_path
from web import views

urlpatterns = [
    re_path(r'^$', views.home),
    re_path(r'^authorise/$', views.authorise, name='authorise'), # Add this /authorise/ route
    re_path(r'^authenticate/$', views.authenticate), # Add this /authenticate/ route
]