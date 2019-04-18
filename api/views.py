import json
from django.views.generic import View
from django.http.response import HttpResponse

from utils import generator


class GenerateView(View):
    def get(self, request):
        age_min = request.GET.get('age_min')
        age_max = request.GET.get('age_max')
        if age_min is None and age_max is None:
            age_min, age_max = 20, 30
        elif age_min is None:
            age_min = 0
        elif age_max is None:
            age_max = max(100, int(age_min)+1)
        data = {
            'age_min': age_min,
            'age_max': age_max,
            'bank_org': request.GET.get('bank_org', 'ICBC'),
            'home': bool(int(request.GET.get('home', 1))),
        }
        ret = generator.Generator().generate(data)
        ret = json.dumps(ret, ensure_ascii=False)
        return HttpResponse(ret, content_type='application/json, charset=utf8')
