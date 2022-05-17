from django import forms


class PercentForm(forms.Form):
    first_num = forms.FloatField()
    second_num = forms.FloatField()

    class Meta:
        fields = ('first_num', 'second_num')
        label = {'first_num': 'большее',
                 'second_num': 'меньшее'}
        help_text = {'first_num': 'Процент от этого числа',
                     'second_num': 'Процент этого числа'}
