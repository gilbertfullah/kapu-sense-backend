from django.urls import path
from .views import MessageView

urlpatterns = [
    path("", MessageView.as_view()),
    #path("messages/<int:pk>/", MessageDetail.as_view()),
]
