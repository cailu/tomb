from django.db import models
import random

# Create your models here.
class Solution(models.Model):
    category = models.CharField(max_length=8, default='tri')
    answer = models.CharField(max_length=128)

    class Meta:
        db_table = 'solution'

    @staticmethod
    def get_random(category):
        idx = 1
        if category == 'tri':
            idx = random.randint(1, 32288)
        elif category == 'pyramid':
            idx = random.randint(32289, 34736)
        else:
            idx = random.randint(34736, 405756)
        return Solution.objects.get(id=idx)
