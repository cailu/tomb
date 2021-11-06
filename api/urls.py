from django.conf.urls import url
from api.views import GenerateView, TriSolveView, RectSolveView, PyramidSolveView


urlpatterns = [
    url(r'^random$', GenerateView.as_view()),
    url(r'^solve$', TriSolveView.as_view()),
    url(r'^rect/solve$', RectSolveView.as_view()),
    url(r'^pyramid/solve$', PyramidSolveView.as_view()),
]
