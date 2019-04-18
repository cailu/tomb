from django.views.generic import View
from django.http.response import JsonResponse

from utils import generator


class GenerateView(View):
    def get(self, request):
        ret = self.generate()
        return JsonResponse(ret)

    @classmethod
    def generate(cls):
        ret = generator.Generator().generate()
        return ret
