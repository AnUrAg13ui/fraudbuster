from django.contrib.auth.decorators import login_required
from django.urls import path
from .views import HomeView, TrainView, PredictView, login_view, logout_view


urlpatterns = [
    path('', HomeView.as_view(), name='Home'),
    path('train/', login_required(TrainView.as_view()), name='Train'),
    path('predict/', login_required(PredictView.as_view()), name='Predict'),
    path('login/', login_view, name='login'),
    path('logout/', login_required(logout_view), name='logout'),
]
