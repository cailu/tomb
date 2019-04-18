import json
from django.views.generic import View
from django.http.response import HttpResponse

from utils import generator


class GenerateView(View):
    def get(self, request):
        ret = self.generate()
        ret = json.dumps(ret, ensure_ascii=False)
        return HttpResponse(ret, content_type='application/json, charset=utf8')

    @classmethod
    def generate(cls):
        ret = generator.Generator().generate()
        return ret
