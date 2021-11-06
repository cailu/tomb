import json
import random
from django.views.generic import View
from django.shortcuts import render
from django.http.response import HttpResponse

from utils import generator
from api.solutions import get_solutions
from api.models import Solution


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


class SolveView(View):
    CATEGORY = None

    def get_solution(self, block=None, category='tri'):
        if block:
            sols = Solution.objects.filter(answer__startswith=block.upper(), category=category)[:100]
            if sols:
                sol = random.choice(sols)
                return sol
        sol = Solution.get_random(category)
        return sol

    def get_content(self, block):
        sol = self.get_solution(block, self.CATEGORY)
        sol = sol.answer.split(' ')
        tables = []
        for i, line in enumerate(sol):
            for j, c in enumerate(line):
                tables.append((i, j, c))
        return tables


class TriSolveView(SolveView):
    CATEGORY = 'tri'

    def get(self, request):
        block = request.GET.get('block')
        tables = self.get_content(block)
        if not tables:
            tables = self.get_content(None)
        context = {"tables": tables}
        return render(request, 'solve_tri.html', context)


class RectSolveView(SolveView):
    CATEGORY = 'rect'

    def get(self, request):
        block = request.GET.get('block')
        tables = self.get_content(block)
        if not tables:
            tables = self.get_content(None)
        context = {"tables": tables}
        return render(request, 'solve_rect.html', context)


class PyramidSolveView(SolveView):
    CATEGORY = 'pyramid'

    def get(self, request):
        block = request.GET.get('block')
        tables = self.get_content(block)
        if not tables:
            tables = self.get_content(None)
        context = {"tables": tables}
        return render(request, 'solve_pyramid.html', context)
