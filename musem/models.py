import datetime

import django.utils.timezone
from django.db import models
from django.contrib.auth.models import User

# Таблица сотрудников
class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="Ivan")
    surname = models.CharField(max_length=100, default="Ivanov")
    patronymic = models.CharField(max_length=100, default="Ivanovich")
    date_of_birth = models.DateField()
    post = models.CharField(max_length=60, default="post")
    salary = models.IntegerField(default=0)
    start_working = models.DateField()
    is_activate = models.IntegerField(default=1)
    date_off = models.DateField(default=django.utils.timezone.now(), blank=True)


    def __str__(self):
        return str(self.employee_id)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employee on a museum"

# Класс, отвечающий за отзывы к конкретной услуге
class Rating(models.Model):
    rating_id = models.IntegerField(primary_key=True)
    mark = models.IntegerField(default=5)
    description = models.TextField(default='my text about this service')
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)
    date_writing = models.DateTimeField(default=django.utils.timezone.now(), blank=True)

# Класс, отвечаюзий за услуги
# Примечание: поле рейтинг не нужно, так как выборку можно производить и в самом запросе
class Service(models.Model):
    service_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50, default='title')
    description = models.TextField(default='description to service')
    cost = models.FloatField(default=0.0)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.service_id)

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Service in this museum"

# Класс, отвечающий за доходы данного предприятия
class Revenue(models.Model):
    revenue_id = models.IntegerField(primary_key=True)
    date = models.DateField()
    service = models.ForeignKey('Service', on_delete=models.CASCADE)
    client = models.ForeignKey(User, on_delete=models.CASCADE)
    revenue = models.FloatField(default=0.0)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.revenue_id)

    class Meta:
        verbose_name = "Revenue"
        verbose_name_plural = "Revenue in the museum"

# Таблица, отвечающая за расходы музея
class Expense(models.Model):
    expense_id = models.IntegerField(primary_key=True)
    cost = models.FloatField(default=0.0)
    date = models.DateField()
    note = models.TextField()
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.expense_id)

    class Meta:
        verbose_name = "Expense"
        verbose_name_plural = "Expense in the museum"

# Класс, отвечающий за посещения клиентов в музей
class Session(models.Model):
    session_id = models.IntegerField(primary_key=True)
    date = models.DateTimeField()
    revenue = models.ForeignKey('Revenue', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.session_id)

    class Meta:
        verbose_name = "Session"
        verbose_name_plural = "Session on the museum"

# Таблица, отвечающая за ведение ГИК (главной инвентарной книги музея)
class Gik(models.Model):
    gik_id = models.IntegerField(primary_key=True)
    date = models.DateField()
    name = models.CharField(max_length=50)
    name_author = models.CharField(max_length=50)
    surname_author = models.CharField(max_length=50)
    count_objects = models.IntegerField(default=0)
    material = models.CharField(max_length=20)
    safety_on_coming = models.CharField(max_length=50)
    short_description = models.CharField(max_length=200)
    note = models.TextField(default='Some note')
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.gik_id)

    class Meta:
        verbose_name = "Gik"
        verbose_name_plural = "Gik in museum"

# Класс, который отвечает за сохранность объектов
class Safety(models.Model):
    safe_id = models.IntegerField(primary_key=True)
    date = models.DateField()
    safety = models.CharField(max_length=20)
    note = models.TextField()
    gik = models.ForeignKey('Gik', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.safe_id)

    class Meta:
        verbose_name = "Safety"
        verbose_name_plural = "Safety in a museum"

# Класс - позиция нашего объекта в музее
class Location(models.Model):
    location_id = models.IntegerField(primary_key=True)
    rack_number = models.IntegerField(default=0)
    shelf_number = models.IntegerField(default=0)
    count_at_place = models.IntegerField(default=0)
    gik = models.ForeignKey('Gik', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.location_id)

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Location on a museum"

# Класс, описывающий инвентарную картотеку
class Inventory(models.Model):
    inventory_id = models.IntegerField(primary_key=True)
    long_description = models.TextField()
    gik = models.ForeignKey('Gik', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.inventory_id)

    class Meta:
        verbose_name = "Inventory journal"
        verbose_name_plural = "Inventory journal in the museum"

# Класс - зарплата сотрудникам
class Sal_emp(models.Model):
    salary_id = models.IntegerField(primary_key=True)
    date = models.DateField()
    count_money = models.IntegerField(default=0)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    is_activate = models.IntegerField(default=1)

    def __str__(self):
        return str(self.salary_id)

    class Meta:
        verbose_name = "Salary"
        verbose_name_plural = "Salary in the museum"