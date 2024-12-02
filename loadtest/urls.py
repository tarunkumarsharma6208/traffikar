from django.urls import path
from .views import *

urlpatterns = [
    path("", home, name="home"),
    path('login/', login_view, name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', logout_view, name='logout'),
    path("load-test/", load_test_view, name="load_test_view"),
    path("advance/load-test/", advance_test_view, name="advance_test_view"),
    path("results/", load_test_results, name="load_test_results"),
]
