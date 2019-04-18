from django.conf.urls import url
from api.views import GenerateView


urlpatterns = [
    url(r'^random$', GenerateView.as_view()),
]
