from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm

from .models import *


# Кастомный класс для того чтобы отображать имя сотрудника
class CustomChoiceFieldName(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.name}"


# Кастомный класс выпадающего списка для того чтобы отобразить имя клиента
class CustomChoiceFieldForUser(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return f"{obj.first_name}"


# Это рабоичй вариант. Остальные формы делаем по аналогии
class CreateEmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['name', 'surname', 'patronymic', 'date_of_birth', 'post', 'salary', 'start_working']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ivan'}))
        self.fields['surname'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ivanov'}))
        self.fields['patronymic'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Ivanovich'}))
        self.fields['date_of_birth'] = forms.CharField(widget=forms.DateInput())
        self.fields['post'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Post'}))
        self.fields['salary'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))
        self.fields['start_working'] = forms.CharField(widget=forms.DateInput())


# Форма создания новой услуги
class CreateServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'cost']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['name'] = forms.CharField(widget=forms.TextInput(
            attrs={'placeholder': 'Name of service'}))
        self.fields['description'] = forms.CharField(widget=forms.Textarea(
            attrs={'placeholder': 'Description of service'}))
        self.fields['cost'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))


# Форма создания класса расходов
class CreateExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['cost', 'date', 'note', 'employee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'] = CustomChoiceFieldName(queryset=Employee.objects.filter(is_activate=1))

        self.fields['cost'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))


# Форма для ввода дохода
class CreateRevenueForm(forms.ModelForm):
    class Meta:
        model = Revenue
        fields = ['date', 'service', 'client', 'revenue']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['client'] = CustomChoiceFieldForUser(queryset=User.objects.filter(is_active=1))
        self.fields['service'] = CustomChoiceFieldName(queryset=Service.objects.filter(is_activate=1))

        self.fields['revenue'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))


# Форма для ввода посещения клиента в музей
class CreateSessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['date', 'revenue']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['revenue'] = forms.ModelChoiceField(queryset=Revenue.objects.all())


# Форма создания ГИК
class CreateGikForm(forms.ModelForm):
    class Meta:
        model = Gik
        fields = ['date', 'name', 'name_author', 'surname_author', 'count_objects', 'material', 'safety_on_coming',
                  'short_description', 'note', 'employee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'] = CustomChoiceFieldName(queryset=Employee.objects.filter(is_activate=1))

        self.fields['count_objects'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))
        self.fields['note'] = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter the note please'}))


# Форма создания формы сохранности
class CreateSafetyForm(forms.ModelForm):
    class Meta:
        model = Safety
        fields = ['date', 'safety', 'note', 'gik']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gik'] = CustomChoiceFieldName(queryset=Gik.objects.filter(is_activate=1))


# форма добавления новой позиции
class CreateLocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['rack_number', 'shelf_number', 'count_at_place', 'gik']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gik'] = CustomChoiceFieldName(queryset=Gik.objects.filter(is_activate=1))

        self.fields['rack_number'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))
        self.fields['shelf_number'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))
        self.fields['count_at_place'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))


# форма добавления новой позиции
class CreateInventoryForm(forms.ModelForm):
    class Meta:
        model = Inventory
        fields = ['long_description', 'gik']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['gik'] = CustomChoiceFieldName(queryset=Gik.objects.filter(is_activate=1))


class CreateRatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['mark', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['mark'] = forms.CharField(widget=forms.TextInput(attrs={'placeholder': '0'}))
        self.fields['description'] = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Description'}))


# форма добавления ЗП сотрудникам
class CreateSalaryEmployee(forms.ModelForm):
    class Meta:
        model = Sal_emp
        fields = ['date', 'count_money', 'employee']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'] = CustomChoiceFieldName(queryset=Employee.objects.filter(is_activate=1))


# Форма регистрации пользователя
class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "email", "password1", "password2"]


# Форма авторизации пользователя (работает только в таком виде :) )
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())


# Форма, где пользователь может менять свои личные данные (например, своё имя и фамилию)
class UserSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'] = forms.EmailField(required=True)


# Форма для получения отчётов
class DatesForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
