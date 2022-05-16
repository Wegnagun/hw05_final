from django.shortcuts import render
from .forms import PercentForm


def percent(request):
    """Высчитываем процентное соотношение"""
    form = PercentForm()
    if request.method == 'POST':
        form = PercentForm(request.POST)
        first_num = float(request.POST.get('first_num'))
        second_num = float(request.POST.get('second_num'))
        result = round((second_num / first_num) * 100, 2)
        if form.is_valid():
            return render(
                request, 'useful/percent.html',
                {'form': form, 'result': result})
    return render(request, 'useful/percent.html', {'form': form})
