from django import forms
from shopapp.models import Product


# Кастомный виджет для множественной загрузки файлов
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


# Кастомное поле для множественной загрузки файлов
class MultipleImageField(forms.ImageField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount", "preview"

    # Используем кастомное поле для загрузки нескольких изображений
    images = MultipleImageField(
        widget=MultipleFileInput(attrs={"multiple": True}),
        required=False,
        label="Изображения"
    )


class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
