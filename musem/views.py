from django.db.models import Q
from django.utils.timezone import now
from django.contrib import auth, messages
from django.http import HttpResponseNotFound, HttpResponseForbidden
from django.shortcuts import render, redirect, reverse, get_object_or_404
from .forms import *

# Данная view отвечает за отображение главной пользовательской страницы
# (пока здесь ничего нету, скоро здесь появится запросы к БД)
def my_first_view(request):
    table = Service.objects.raw(
        raw_query="SELECT ms.service_id, ms.name, ms.description, ms.cost, (SELECT AVG(mark) FROM musem_rating mr "
                  "WHERE mr.service_id=ms.service_id AND mr.is_activate = 1) as rating "
                  "FROM musem_service ms WHERE is_activate = 1"
    )

    return render(request, 'client_pages/main_page.html', {
        'title_page': "Добро пожаловать, ",
        'hide_nav_bar': 0,
        'table': table,
        'is_description': 0,
        'is_administrative_zone': 0
    })

# Вьюха, которая позволяет клиенту просмотреть список услуг, которые он посещал и должен посетить
def client_list_visits(request):
    if not request.user.is_authenticated or request.user.is_superuser:
        return HttpResponseForbidden()

    # Данный запрос показывает услуги, которые пользователь забронировал но не посетил
    list_accesible_sessions = Revenue.objects.raw(
        raw_query=f"SELECT mr.revenue_id, mr.date, ms2.name, mr.revenue, mr.service_id "
                  f"FROM musem_revenue mr JOIN musem_service ms2 "
                  f"ON ms2.service_id = mr.service_id WHERE mr.client_id = {request.user.id} AND mr.revenue_id "
                  f"NOT IN (SELECT ms.revenue_id FROM musem_session ms) AND mr.is_activate = 1 ORDER BY mr.date"
    )

    list_visited_sessions = Revenue.objects.raw(
        raw_query=f"SELECT mr.revenue_id, mr.date, ms2.name, mr.revenue, mr.service_id "
                  f"FROM musem_revenue mr JOIN musem_service ms2 "
                  f"ON ms2.service_id = mr.service_id WHERE mr.client_id = {request.user.id} AND mr.revenue_id "
                  f"IN (SELECT ms.revenue_id FROM musem_session ms) AND mr.is_activate = 1 ORDER BY mr.date"
    )

    return render(request, 'client_pages/user_visited_not_visited_sessions.html', {
        'title_page': "Ваши посещения",
        'hide_nav_bar': 0,
        'list_accesible_sessions': list_accesible_sessions,
        'list_visited_sessions': list_visited_sessions,
        'is_description': 0,
        'is_administrative_zone': 0
    })

# Данная View отображает содержимое услуги, а также отзывы
def service_description(request, service_id, type_sort):
    # Получаем описание к конкретной услуге из соответсвующих журналов
    table_with_service_description = Service.objects.raw(
        raw_query=f"SELECT ms.service_id, ms.name, ms.description, ms.cost, (SELECT AVG(mark) FROM musem_rating mr "
                  f"WHERE mr.service_id=ms.service_id AND mr.is_activate = 1) as rating FROM musem_service ms "
                  f"WHERE ms.service_id = {service_id}"
    )

    # Получаем список отзывов к данной услуге
    raw_query = f"SELECT mr.rating_id, mr.mark, mr.description, au.first_name, mr.client_id, mr.date_writing FROM " \
                f"musem_rating mr JOIN auth_user au ON mr.client_id = au.id WHERE is_activate = 1 AND " \
                f"mr.service_id = {service_id} "
    if type_sort == "negative":
        raw_query += "ORDER BY mr.mark"
    elif type_sort == "positive":
        raw_query += "ORDER BY mr.mark DESC"
    elif type_sort == "old":
        raw_query += "ORDER BY mr.date_writing"
    elif type_sort == "new":
        raw_query += "ORDER BY mr.date_writing DESC"
    else:
        return HttpResponseNotFound()

    table_with_rating_to_service = Rating.objects.raw(raw_query=raw_query)

    # При помощи этого условия проверяем, есть ли вообще отзывы к этой услуге
    if len(list(table_with_rating_to_service)) > 0:
        is_rating_to_service = 1
    else:
        is_rating_to_service = 0

    # Проверяем оставлял ли конкретно авторизованный пользователь отзыв к услуге
    user_rating = None
    q = f"SELECT * FROM musem_rating mr JOIN auth_user au ON au.id = mr.client_id " \
        f"WHERE mr.service_id = {service_id} AND mr.client_id = {request.user.id} AND mr.is_activate = 1"

    if request.user.is_authenticated:
        user_rating = Rating.objects.raw(raw_query=q)

        if len(list(user_rating)) == 1:
            has_rating = 1
        else:
            has_rating = 0
    else:
        has_rating = -1

    return render(request, 'client_pages/service_description.html', {
        'title_page': "Подробнее об услуге ",
        'hide_nav_bar': 0,
        'table_service': table_with_service_description,
        'table_rating': table_with_rating_to_service,
        'is_description': 1,
        'is_rating_exists': has_rating,
        'user_rating_list': user_rating,
        'is_rating_to_service': is_rating_to_service,
        'is_administrative_zone': 0,
        'id': service_id
    })

# Функция, которая позволяет клиенту покупать билеты
def client_buy_ticket_to_museum(request, service_id):
    if request.user.is_superuser and not request.user.is_authenticated:
        return HttpResponseForbidden()

    cost_revenue = list(Service.objects.filter(service_id=service_id))[0].cost
    my_revenue = Revenue(client_id=request.user.id, service_id=service_id, revenue=cost_revenue,
                         date=datetime.datetime.now())

    # Принцип работы прост: клиент, покупая билет, вносится в электронный журнал админа
    # По приходу в музей клиент оплачивает свою услугу в соответсвии со стоимостью,
    # на момент которой он бронировал услугу
    my_revenue.save()

    return redirect(reverse('main_page'))

# Администраторская зона (его главная страница)
def admin_main_page(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    return render(request, 'admin_pages/main_page_admin.html', {
        'title_page': "Электронный документооборот музея",
        'hide_nav_bar': 0,
        'is_administrative_zone': 1
    })


# Администраторская зона (просмотр списка клиентов)
def admin_client_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    raw_data = User.objects.raw(
        raw_query="SELECT id, first_name, last_name, username, email, is_active FROM auth_user WHERE is_active = 1 "
                  "AND is_staff = 0 AND is_superuser = 0"
    )
    # Модель нашей таблицы (то как она будет выглядеть)
    # Пока здесь текст-рыба но в будущем здесь будет запрос
    head = ["Номер", "Имя", "Фамилия", "Ник", "Почта", "Статус"]

    return render(request, 'admin_pages/tables/client_list_page.html', {
        'title_page': 'Журнал клиентов',
        'hide_nav_bar': 0,
        'head': head,
        'table': raw_data,
        'is_administrative_zone': 1
    })


# Просмотр списка сотрудников
def admin_employee_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Имя", "Фамилия", "Отчество", "Дата рождения", "Должность", "Оклад", "Дата начала работы", "Статус"]
    raw_data = Employee.objects.raw(
        raw_query="SELECT * FROM musem_employee WHERE is_activate = 1"
    )

    return render(request, 'admin_pages/tables/employee_list_pages.html', {
        'title_page': 'Журнал сотрудников',
        'hide_nav_bar': 0,
        'head': head,
        'table': raw_data,
        'is_administrative_zone': 1
    })

# Просмотр списка услуг
def admin_services_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Название", "Описание", "Стоимость", "Отзывы"]
    table = Service.objects.raw(
        raw_query="SELECT ms.service_id, ms.name, ms.description, ms.cost, (SELECT AVG(mark) FROM musem_rating mr " \
                  "WHERE mr.service_id=ms.service_id AND mr.is_activate = 1) as rating " \
                  "FROM musem_service ms WHERE is_activate = 1")

    return render(request, 'admin_pages/tables/services_list_page.html', {
        'title_page': 'Журнал услуг',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'enable_all_description': 0,
        'is_rating': list(table)[0].rating is not None,
        'is_administrative_zone': 1
    })


# Просмотр списка доходов
def admin_revenue_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # Поля нашей таблицы
    head = ["Номер", "Дата", "Услуга", "Стоимость", "Клиент"]

    # Для большей наглядности использую чистые запросы, а не ORM
    table = Revenue.objects.raw(
        raw_query="SELECT mr.revenue_id, mr.date, mr.revenue, ms.name AS service_name, au.first_name as client_name, "
                  "ms.service_id, au.id FROM musem_revenue mr JOIN musem_service ms, auth_user au ON "
                  "mr.service_id = ms.service_id AND mr.client_id = au.id WHERE mr.is_activate = 1")

    return render(request, 'admin_pages/tables/revenue_list_page.html', {
        'title_page': 'Журнал доходов',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр списка расходов
def admin_expense_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Дата", "Стоимость", "Примечание", "Сотрудник"]
    table = Expense.objects.raw(
        raw_query="SELECT me.expense_id, me.cost, me.date, me.note, me.employee_id, me2.name FROM musem_expense me "
                  "JOIN musem_employee me2 ON me.employee_id = me2.employee_id WHERE me.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/expense_list_pages.html', {
        'title_page': 'Журнал расходов',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр списка расходов
def admin_session_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Дата", "Чек"]
    table = Session.objects.raw(
        raw_query="SELECT ms.session_id, ms.date, ms.revenue_id FROM musem_session ms JOIN musem_revenue mr ON "
                  "ms.revenue_id = mr.revenue_id AND mr.is_activate = 1 WHERE ms.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/session_list_pages.html', {
        'title_page': 'Журнал посещений',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр списка расходов
def admin_gik(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # Пока здесь текст-рыба но в будущем здесь будет запрос
    head = ["Номер", "Дата", "Название предмета", "ФИО автора", "Количество объектов", "Материал",
            "Степень сохранности", "Примечание", "Сотрудник"]
    table = Gik.objects.raw(
        raw_query="SELECT mg.gik_id, mg.date, mg.name, mg.name_author, mg.surname_author, mg.count_objects, mg.material, mg.safety_on_coming, "
                  "mg.short_description, mg.note, me.name as name_employee, me.surname as employee_surname, "
                  "me.employee_id FROM musem_gik mg JOIN musem_employee me ON mg.employee_id = me.employee_id "
                  "WHERE mg.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/gik_list_pages.html', {
        'title_page': 'Журнал "ГИК"',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_description': 0,
        'is_administrative_zone': 1
    })


# Просмотр картотеки сохранности
def admin_save_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Дата", "Сохранность", "Примечание", "Музейный объект"]
    table = Safety.objects.raw(
        raw_query="SELECT ms.safe_id, ms.date, ms.safety, ms.note, ms.gik_id FROM musem_safety ms JOIN musem_gik mg ON "
                  "ms.gik_id = mg.gik_id AND mg.is_activate = 1 WHERE ms.is_activate = 1;"
    )

    return render(request, 'admin_pages/tables/safety_list_pages.html', {
        'title_page': 'Картотека сохранности',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_description': 0,
        'is_administrative_zone': 1
    })


# Просмотр инвентарной картотеки
def admin_inventory_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Подробное описание", "Номер в ГИК"]
    table = Inventory.objects.raw(
        raw_query="SELECT mi.inventory_id, mi.long_description, mi.gik_id FROM musem_inventory mi JOIN musem_gik mg "
                  "ON mi.gik_id = mg.gik_id AND mg.is_activate = 1 WHERE mi.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/inventory_list_pages.html', {
        'title_page': 'Инвентарная картотека',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_description': 0,
        'is_administrative_zone': 1
    })


# Просмотр картотеки сохранности
def admin_location_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Номер стеллажа", "Номер полки", "Количество объектов", "Номер в ГИК"]
    table = Location.objects.raw(
        raw_query="SELECT * FROM musem_location ml JOIN musem_gik mg ON ml.gik_id = mg.gik_id "
                  "AND mg.is_activate=1 WHERE ml.is_activate = 1 ORDER BY ml.gik_id"
    )

    return render(request, 'admin_pages/tables/location_list_pages.html', {
        'title_page': 'Топографическая картотека',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр картотеки сохранности
def admin_rating_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Рейтинг", "Комментарий", "Клиент", "Дата", "Услуга"]
    table = Rating.objects.raw(
        raw_query="SELECT mr.rating_id, mr.mark, mr.date_writing,"
                  " mr.description, au.username, au.id, ms.name FROM musem_rating mr "
                  "JOIN auth_user au, musem_service ms ON mr.client_id = au.id AND "
                  "ms.service_id = mr.service_id WHERE mr.is_activate = 1 ORDER BY mr.service_id"
    )

    return render(request, 'admin_pages/tables/rating_list_page.html', {
        'title_page': 'Таблица отзывов',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'show_last_field': 1,
        'is_administrative_zone': 1
    })


# Просмотр списка зарплаты сотрудникам
def admin_salary_employee_list(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # Поля нашей таблицы
    head = ["Номер", "Дата", "Оклад", "Сотрудник"]

    # Для большей наглядности использую чистые запросы, а не ORM
    table = Sal_emp.objects.raw(
        raw_query="SELECT mse.salary_id, mse.date , mse.count_money, mse.employee_id, me.name FROM musem_sal_emp mse "
                  "JOIN musem_employee me ON mse.employee_id = me.employee_id WHERE mse.is_activate = 1")


    return render(request, 'admin_pages/tables/salary_employee_list_pages.html', {
        'title_page': 'Журнал выплаты заработной платы',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Администраторская зона (просмотр информации о конкретном клиенте)
def admin_client_description(request, user_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Имя", "Фамилия", "Ник", "Почта", "Статус"]
    query = f"SELECT id, first_name, last_name, username, email, is_active " \
            f"FROM auth_user WHERE id = {user_id}"

    table = User.objects.raw(raw_query=query)

    return render(request, 'admin_pages/tables/descriptions/client_description.html', {
        'title_page': 'Сведения о клиенте',
        'hide_nav_bar': 0,
        'head': head,
        "table": table,
        'is_administrative_zone': 1
    })


# Просмотр списка сотрудников (подробный, с доп.функциями)
def admin_employee_description(request, employee_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Имя", "Фамилия", "Отчество", "Дата рождения", "Должность", "Оклад", "Дата начала работы",
            "Статус"]

    query = f"SELECT * FROM musem_employee WHERE employee_id = {employee_id}"
    raw_data = Employee.objects.raw(raw_query=query)

    return render(request, 'admin_pages/tables/descriptions/employee_description.html', {
        'title_page': 'Сведения о сотруднике',
        'hide_nav_bar': 0,
        'head': head,
        'table': raw_data,
        'is_administrative_zone': 1
    })


# Просмотр списка услуг
def admin_service_description(request, service_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Название", "Описание", "Стоимость", "Отзывы", "Статус"]
    table = Service.objects.raw(
        raw_query=f"SELECT ms.service_id, ms.name, ms.description, ms.cost, (SELECT AVG(mark) FROM musem_rating mr "
              f"WHERE mr.service_id=ms.service_id AND mr.is_activate = 1) as rating FROM musem_service ms "
                  f"WHERE ms.service_id = {service_id}")

    return render(request, 'admin_pages/tables/descriptions/service_description.html', {
        'title_page': 'Журнал услуг',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'enable_all_description': 1,
        'is_rating': list(table)[0].rating is not None,
        'is_administrative_zone': 1
    })


# Просмотр содержимого о рейтинге
def admin_rating_description(request, rating_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Рейтинг", "Комментарий", "Клиент", "Дата и время", "Услуга"]
    table = Rating.objects.raw(
        raw_query=f"SELECT mr.rating_id, mr.mark, mr.description, mr.date_writing, "
                  f"au.username, au.id, ms.name FROM musem_rating mr "
                  f"JOIN auth_user au, musem_service ms ON mr.client_id = au.id AND "
                  f"ms.service_id = mr.service_id WHERE mr.rating_id = {rating_id} ORDER BY mr.service_id "
                  f"AND mr.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/descriptions/rating_description.html', {
        'title_page': 'Отзыв',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'show_last_field': 1,
        'is_administrative_zone': 1
    })


# Просмотр списка доходов
def admin_revenue_description(request, revenue_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # Пока здесь текст-рыба но в будущем здесь будет запрос
    head = ["Номер", "Дата", "Услуга", "Стоимость", "Клиент"]

    query = f"SELECT mr.revenue_id, mr.date, mr.revenue, ms.name AS service_name, au.first_name as client_name, " \
            f"ms.service_id, au.id FROM musem_revenue mr JOIN musem_service ms, auth_user au ON " \
            f"mr.service_id = ms.service_id AND mr.client_id = au.id WHERE mr.revenue_id = {revenue_id} AND " \
            f"mr.is_activate = 1"

    table = Revenue.objects.raw(raw_query=query)

    return render(request, 'admin_pages/tables/descriptions/revenue_description.html', {
        'title_page': 'Поступивший доход',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр информации о расходе
def admin_expense_description(request, expense_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Дата", "Стоимость", "Примечание", "Сотрудник"]
    table = Expense.objects.raw(
        raw_query=f"SELECT me.expense_id, me.cost, me.date, me.note, me.employee_id, me2.name FROM musem_expense me "
                  f"JOIN musem_employee me2 ON me.employee_id = me2.employee_id WHERE expense_id = {expense_id}"
                  f" AND me.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/descriptions/expense_description.html', {
        'title_page': 'Сведения о расходе',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр списка расходов
def admin_session_description(request, session_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # Модель нашей таблицы (то как она будет выглядеть)
    # Пока здесь текст-рыба но в будущем здесь будет запрос
    head = ["Номер", "Дата", "Чек"]
    table = Session.objects.raw(
        raw_query=f"SELECT * FROM musem_session WHERE session_id = {session_id} AND is_activate = 1"
    )

    return render(request, 'admin_pages/tables/descriptions/session_description.html', {
        'title_page': 'Посещение клиента в музей',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр списка расходов
def admin_gik_description(request, gik_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # Пока здесь текст-рыба но в будущем здесь будет запрос
    head = ["Номер", "Дата", "Название предмета", "ФИО автора", "Количество объектов", "Материал",
            "Степень сохранности", "Примечание", "Сотрудник"]
    table = Gik.objects.raw(
        raw_query=f"SELECT mg.gik_id, mg.date, mg.name, mg.name_author, mg.surname_author, mg.count_objects, mg.material, mg.safety_on_coming,"
                  f" mg.short_description, mg.note, me.name as name_employee, me.surname as employee_surname, "
                  f"me.employee_id FROM musem_gik mg JOIN musem_employee me ON mg.employee_id = me.employee_id "
                  f"WHERE gik_id = {gik_id} AND mg.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/descriptions/gik_description.html', {
        'title_page': 'Сведения о музейном объекте',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_description': 1,
        'is_administrative_zone': 1
    })


# Просмотр подробных сведений в картотеке сохранности
def admin_safe_description(request, safe_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Дата", "Сохранность", "Примечание", "Музейный объект"]
    table = Safety.objects.raw(
        raw_query=f"SELECT * FROM musem_safety WHERE safe_id = {safe_id} AND is_activate = 1"
    )

    return render(request, 'admin_pages/tables/descriptions/safety_description.html', {
        'title_page': 'Картотека сохранности',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_description': 1,
        'is_administrative_zone': 1
    })


# Просмотр картотеки сохранности
def admin_location_description(request, location_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Номер стеллажа", "Номер полки", "Количество объектов", "Номер в ГИК"]
    table = Location.objects.raw(
        raw_query=f"SELECT * FROM musem_location ml JOIN musem_gik mg ON ml.gik_id = mg.gik_id "
                  f"AND mg.is_activate=1 WHERE ml.is_activate = 1 AND ml.location_id = {location_id}"
    )

    return render(request, 'admin_pages/tables/descriptions/location_description.html', {
        'title_page': 'Топографическая картотека',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })


# Просмотр инвентарной картотеки
def admin_inventory_description(request, inventory_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Подробное описание", "Номер в ГИК"]
    table = Inventory.objects.raw(
        raw_query=f"SELECT * FROM musem_inventory WHERE inventory_id = {inventory_id} AND is_activate = 1"
    )

    return render(request, 'admin_pages/tables/descriptions/inventory_description.html', {
        'title_page': 'Инвентарная картотека',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_description': 1,
        'is_administrative_zone': 1
    })

# Просмотр картотеки сохранности
def admin_rating_service(request, service_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    head = ["Номер", "Рейтинг", "Комментарий", "Клиент"]
    table = Rating.objects.raw(
        raw_query=f"SELECT mr.rating_id, mr.mark, mr.description, au.username, au.id, ms.name FROM musem_rating mr "
                  f"JOIN auth_user au, musem_service ms ON mr.client_id = au.id AND "
                  f"ms.service_id = mr.service_id WHERE mr.service_id = {service_id} AND mr.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/rating_list_page.html', {
        'title_page': f'Таблица отзывов для услуги "{table[0].name}"',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'show_last_field': 0,
        'is_administrative_zone': 1
    })

# Просмотр списка зарплаты сотрудникам (детализированная версия)
def admin_salary_employee_description(request, salary_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    # Поля нашей таблицы
    head = ["Номер", "Дата", "Оклад", "Сотрудник"]

    # Для большей наглядности использую чистые запросы, а не ORM
    table = Sal_emp.objects.raw(
        raw_query=f"SELECT mse.salary_id, mse.date , mse.count_money, mse.employee_id, me.name FROM musem_sal_emp mse "
                  f"JOIN musem_employee me ON mse.employee_id = me.employee_id WHERE mse.salary_id = {salary_id} "
                  f"AND mse.is_activate = 1")

    return render(request, 'admin_pages/tables/descriptions/salary_employee_description.html', {
        'title_page': 'Журнал выплаты заработной платы',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })

"""Удаление различных объектов (делай по такому принципу для всех остальных. По**й на реализацию кода)"""
def admin_location_delete(request, location_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Location.objects.filter(location_id=location_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

def admin_service_delete(request, service_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Service.objects.filter(service_id=service_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

def admin_client_delete(request, client_id, type_delete):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if type_delete:
        User.objects.filter(id=client_id).update(is_active=0)
    else:
        User.objects.filter(id=client_id).update(is_active=1)
    return redirect(reverse('main_page_admin'))

def admin_employee_delete(request, employee_id, type_delete):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    # Удаление сотрудника
    if type_delete:
        Employee.objects.filter(employee_id=employee_id).update(is_activate=0, date_off=now())
    else:
        # Восстановление сотрудника
        Employee.objects.filter(employee_id=employee_id).update(is_activate=1)
    return redirect(reverse('main_page_admin'))

# Функция, позволяющая удалить отзыв
def client_rating_delete(request, service_id):
    if not request.user.is_authenticated or request.user.is_superuser:
        return HttpResponseForbidden()

    Rating.objects.filter(Q(service_id=service_id) & Q(client_id=request.user.id)).update(is_activate=0)
    return redirect(reverse('main_page'))

# Функция, которая позволяет удалить доход
def admin_revenue_delete(request, revenue_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Revenue.objects.filter(revenue_id=revenue_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

def admin_expense_delete(request, expense_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Expense.objects.filter(expense_id=expense_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

def admin_session_delete(request, session_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Session.objects.filter(session_id=session_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

# Вьюха, которая позволяет клиенту отменить бронирование улсуги
def client_delete_access_session(request, revenue_id):
    if not request.user.is_authenticated or request.user.is_superuser:
        return HttpResponseForbidden()

    Revenue.objects.filter(revenue_id=revenue_id).update(is_activate=0)
    return redirect(reverse('main_page'))

def admin_inventory_delete(request, inventory_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Inventory.objects.filter(inventory_id=inventory_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

def admin_safe_delete(request, safe_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Safety.objects.filter(safe_id=safe_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

def admin_salary_employee_delete(request, salary_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Sal_emp.objects.filter(salary_id=salary_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

def admin_rating_delete(request, rating_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Rating.objects.filter(rating_id=rating_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

# Не забудь, что при использовании JoIn-а нужно также добавлять проверку на единицу activate-а
def admin_gik_delete(request, gik_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    Gik.objects.filter(gik_id=gik_id).update(is_activate=0)
    return redirect(reverse('main_page_admin'))

""" Формы создания чего-либо """
def admin_create_employee(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateEmployeeForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateEmployeeForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавить сотрудника',
        'text_button': 'Зарегистрировать',
        'is_administrative_zone': 1
    })

def admin_create_service(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateServiceForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateServiceForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление услуги',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

# Вьюха, которая позволяет оставить отзыв к конкретной услуге
def client_create_rating(request, service_id):
    # Запетные случаи: суперюзер, неавторизованный аноним или человек, оставлявший отзыв к данной услуге
    if not request.user.is_authenticated or request.user.is_superuser or \
            Rating.objects.filter(Q(service_id=service_id) & Q(client_id=request.user.id) & Q(is_activate=1)).exists():
        return HttpResponseForbidden()

    if request.method == "POST":
        creation_rating_form = CreateRatingForm(data=request.POST)
        # Проверка на валидность формы
        if creation_rating_form.is_valid():
            # Оценка
            mark = creation_rating_form.cleaned_data['mark']
            # Описание
            description = creation_rating_form.cleaned_data['description']

            my_rating = Rating(mark=mark, description=description, service_id=service_id, client_id=request.user.id)
            my_rating.save()

            return redirect(reverse('main_page'))
        else:
            messages.error(request, "An error to create a form")
    else:
        creation_rating_form = CreateRatingForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_rating_form,
        'title_page': 'Форма оставления отзыва к услуге',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

def admin_create_expense(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateExpenseForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateExpenseForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление расходы',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

def admin_create_revenue(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateRevenueForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateRevenueForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление дохода',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

def admin_create_session(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateSessionForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateSessionForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление посещения',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

# Отвечает за добавление объекта в ГИК
def admin_create_gik(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateGikForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateGikForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление данных в ГИК',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

# Отвечает за добавление объекта в ГИК
def admin_create_safe(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateSafetyForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateSafetyForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление данных о сохранности',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

# Отвечает за добавление объекта в ГИК
def admin_create_location(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateLocationForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateLocationForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление данных о позиции объектов',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

# Отвечает за добавление объекта в ГИК
def admin_create_inventory(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateInventoryForm(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateInventoryForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление данных о расширенном описании объекта',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

# Отвечает за добавление объекта в ГИК
def admin_create_salary_employee(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = CreateSalaryEmployee(data=request.POST)

        if creation_form.is_valid():
            creation_form.save()
            return redirect(reverse('main_page_admin'))
    else:
        creation_form = CreateSalaryEmployee()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Добавление данных о ЗП сотрудникам',
        'text_button': 'Добавить',
        'is_administrative_zone': 1
    })

""" Форма редактирования текста"""
# Редактирование сотрудника
def admin_edit_employee(request, employee_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Employee, employee_id=employee_id)
    form = CreateEmployeeForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных о сотруднике',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование услуги
def admin_edit_service(request, service_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Service, service_id=service_id)
    form = CreateServiceForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных об услуге',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Вьюха, которая редактирует отзыв (в случае если, например, человек, изменил своё дилетантское мнение)
def client_edit_rating(request, service_id):
    # Если пользователь не авторизован, то ему доступа нет
    if not request.user.is_authenticated or request.user.is_superuser:
        return HttpResponseForbidden()

    # При помощи Q мы можем использовать оператор AND
    instance = get_object_or_404(Rating.objects.filter(Q(service_id=service_id) & Q(client_id=request.user.id) &
                                                       Q(is_activate=1)))
    form = CreateRatingForm(request.POST or None, instance=instance)

    # Проверка формы на валидность
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование отзыва к услуге',
        'text_button': 'Редактировать',
        'is_administrative_zone': 0
    })

# Редактирование дохода
def admin_edit_revenue(request, revenue_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Revenue, revenue_id=revenue_id)
    form = CreateRevenueForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных о поступившем доходе',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование дохода
def admin_edit_expense(request, expense_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Expense, expense_id=expense_id)
    form = CreateExpenseForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных о расходах',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование дохода
def admin_edit_session(request, session_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Session, session_id=session_id)
    form = CreateSessionForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных о прибытии клиента',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование дохода
def admin_edit_gik(request, gik_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Gik, gik_id=gik_id)
    form = CreateGikForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных ГИК',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование дохода
def admin_edit_safe(request, safe_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Safety, safe_id=safe_id)
    form = CreateSafetyForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных картотеки сохранности',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование картотеки сохранности
def admin_edit_location(request, location_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Location, location_id=location_id)
    form = CreateLocationForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных топографической картотеки',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование картотеки сохранности
def admin_edit_inventory(request, inventory_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Inventory, inventory_id=inventory_id)
    form = CreateInventoryForm(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных инвентарной картотеки',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Редактирование картотеки сохранности
def admin_edit_salary_employee(request, salary_employee_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    instance = get_object_or_404(Sal_emp, salary_id=salary_employee_id)
    form = CreateSalaryEmployee(request.POST or None, instance=instance)
    if form.is_valid():
        form.save()
        return redirect(reverse('main_page_admin'))

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': form,
        'title_page': 'Редактирование данных ЗП сотрудника',
        'text_button': 'Редактировать',
        'is_administrative_zone': 1
    })

# Эта функция стоит особняком - показать историю сохранности в процессе эксплуатации
def get_safe_history_for_object(request, gik_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    head = ["Номер", "Дата", "Сохранность", "Примечание", "Музейный объект"]
    table = Safety.objects.raw(
        raw_query=f"SELECT * FROM musem_safety ms WHERE ms.gik_id = {gik_id} AND ms.is_activate = 1 ORDER BY ms.date DESC;"
    )

    return render(request, 'admin_pages/tables/safety_list_pages.html', {
        'title_page': 'Картотека сохранности для объекта',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_description': 0,
        'is_administrative_zone': 1
    })

"""Отчёты которые мы получаем """
# Отчёт, который позволяет нам получить доходы в разные периоды
def admin_calculate_report_revenue(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = DatesForm(data=request.POST)

        # Если форма валидна, то выводим окно с отчётом за данный промежуток времени
        if creation_form.is_valid():
            start_date = creation_form.cleaned_data['start_date']
            end_date = creation_form.cleaned_data['end_date']
            query = f"SELECT ms.session_id, strftime('%m', ms.date) as month, SUM(mr.revenue) as summ_revenue " \
                    f"FROM musem_session ms JOIN musem_revenue mr ON ms.revenue_id = mr.revenue_id WHERE ms.date " \
                    f"BETWEEN '{start_date}' AND '{end_date}' AND ms.is_activate = 1 GROUP BY month;"
            print(query)
            table = Session.objects.raw(query)
            head = ['Месяц', 'Доход']
            return render(request, 'admin_pages/tables/report_revenue.html', {
                'title_page': 'Отчёт по доходам',
                'hide_nav_bar': 0,
                'head': head,
                'table': table,
                'start_date': start_date,
                'end_date': end_date,
                'is_administrative_zone': 1
            })

    else:
        creation_form = DatesForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Отчёт по доходам',
        'text_button': 'Получить отчёт',
        'is_administrative_zone': 1
    })

# Отчёт, который позволяет показать расходы заведения за месяц
def admin_calculate_report_expense(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = DatesForm(data=request.POST)

        # Если форма валидна, то выводим окно с отчётом за данный промежуток времени
        if creation_form.is_valid():
            start_date = creation_form.cleaned_data['start_date']
            end_date = creation_form.cleaned_data['end_date']

            query = f"SELECT me.expense_id, strftime('%m', me.date) as month, SUM(me.cost) AS expense, (SELECT SUM(mse.count_money) " \
                    f"FROM musem_sal_emp mse WHERE mse.is_activate " \
                    f"AND strftime('%m', me.date) = strftime('%m', mse.date)) AS " \
                    f"expense_employee FROM musem_expense me WHERE me.is_activate = 1 " \
                    f"AND me.date BETWEEN '{start_date}' AND '{end_date}' GROUP BY month;"

            head = ['Месяц', 'Расходы', "Выплата сотрудникам"]
            table = Expense.objects.raw(query)

            return render(request, 'admin_pages/tables/report_expense.html', {
                'title_page': 'Отчёт по расходам',
                'hide_nav_bar': 0,
                'head': head,
                'table': table,
                'start_date': start_date,
                'end_date': end_date,
                'is_administrative_zone': 1
            })

    else:
        creation_form = DatesForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Отчёт по расходам',
        'text_button': 'Получить отчёт',
        'is_administrative_zone': 1
    })

# Отчёт, который позволяет показать выручку заведения за месяц
def admin_calculate_report_popular(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = DatesForm(data=request.POST)

        # Если форма валидна, то выводим окно с отчётом за данный промежуток времени
        if creation_form.is_valid():
            start_date = creation_form.cleaned_data['start_date']
            end_date = creation_form.cleaned_data['end_date']

            query = f"SELECT ms.session_id, STRFTIME('%m', ms.date) AS month, ms2.name AS service_name, COUNT(ms2.name) " \
                    f"as popularity FROM musem_session ms JOIN musem_revenue mr ON ms.revenue_id = mr.revenue_id " \
                    f"JOIN musem_service ms2 ON mr.service_id = ms2.service_id WHERE ms.date " \
                    f"BETWEEN '{start_date}' AND '{end_date}' GROUP BY month ORDER BY popularity DESC ;"

            head = ['Название услуги', "Популярность"]
            table = Session.objects.raw(query)

            return render(request, 'admin_pages/tables/report_popular_services.html', {
                'title_page': 'Популярные услуги среди клиентов',
                'hide_nav_bar': 0,
                'head': head,
                'table': table,
                'start_date': start_date,
                'end_date': end_date,
                'is_administrative_zone': 1
            })

    else:
        creation_form = DatesForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Отчёт по расходам',
        'text_button': 'Получить отчёт',
        'is_administrative_zone': 1
    })

# Отчёт, который позволяет показать выручку заведения за месяц
def admin_calculate_workload(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        creation_form = DatesForm(data=request.POST)

        # Если форма валидна, то выводим окно с отчётом за данный промежуток времени
        if creation_form.is_valid():
            start_date = creation_form.cleaned_data['start_date']
            end_date = creation_form.cleaned_data['end_date']

            query = f"SELECT ms.session_id, DATE(ms.date) as my_date, COUNT(ms.revenue_id) as count_visits " \
                    f"FROM musem_session ms WHERE ms.date BETWEEN '{start_date}' AND '{end_date}' " \
                    f"GROUP BY my_date ORDER BY my_date;"

            head = ['Дата', "Количество посещений"]
            table = Session.objects.raw(query)

            return render(request, 'admin_pages/tables/report_workload.html', {
                'title_page': 'Популярные услуги среди клиентов',
                'hide_nav_bar': 0,
                'head': head,
                'table': table,
                'start_date': start_date,
                'end_date': end_date,
                'is_administrative_zone': 1
            })

    else:
        creation_form = DatesForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'hide_nav_bar': 0,
        'form': creation_form,
        'title_page': 'Отчёт по нагруженности музея',
        'text_button': 'Получить отчёт',
        'is_administrative_zone': 1
    })

# Просмотр детальной информации по доходу за месяц
def admin_get_data_by_month(request, month_id):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    head = ["Session ID", "Дата", "Доход"]
    table = Session.objects.raw(
        raw_query=f"SELECT ms.session_id, ms.date, mr.revenue as dohod FROM musem_session ms JOIN musem_revenue mr ON "
                  f"ms.revenue_id = mr.revenue_id WHERE strftime('%m', ms.date) = '{month_id}' AND ms.is_activate = 1"
    )

    return render(request, 'admin_pages/tables/detail_report_revenue_list_pages.html', {
        'title_page': 'Детальный доход за месяц',
        'hide_nav_bar': 0,
        'head': head,
        'table': table,
        'is_administrative_zone': 1
    })

"""Регистрация пользователей"""
# Примечание: пароль надо вводить с учётом больших букв, маленьких букв и цифр
# Иначе он не регистрирует
def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
            mail = form.cleaned_data['email']
            is_user_exists_with_mail = User.objects.filter(email=mail)

            # Проверка на уникальность username (он должен быть уникальным естественно)
            if is_user_exists_with_mail.exists():
                messages.error(request, "This mail are exists. Please retype the mail and try again")
            else:
                new_user = form.save()
                auth.login(request, new_user)
                return redirect(reverse('main_page'))

        else:
            messages.error(request, "Error in the inputting data")
    else:
        form = UserRegistrationForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'form': form,
        'hide_nav_bar': 0,
        'title_page': 'Форма регистрации',
        'text_button': 'Зарегистрироваться',
        'is_administrative_zone': 0
    })

# Метод занимается авторизацией пользователя (не трогать код ^^))
def login_user(request):
    if request.user.is_authenticated:
        return HttpResponseNotFound()

    # Если тип запроса - POST, то тогда проверяем на валидность
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                return redirect(reverse('main_page'))
            else:
                messages.error(request, "Incorrect name or password")
        else:
            messages.error(request, "Error in the inputting login data")
    else:
        form = LoginForm()

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'form': form,
        'hide_nav_bar': 0,
        'title_page': 'Форма авторизации',
        'text_button': 'Авторизоваться',
        'is_administrative_zone': 0
    })

# Случай, когда пользователь выходит из системы
def logout_user(request):
    if not request.user.is_authenticated:
        return HttpResponseNotFound()
    auth.logout(request)
    return redirect(reverse('main_page'))

# Данная форма позволяет изменить пользовательские даннве
def change_data_user(request):
    if not request.user.is_authenticated:
        return HttpResponseNotFound()

    if request.method == "POST":
        user_form = UserSettingsForm(request.POST, instance=request.user)

        if user_form.is_valid():
            mail = user_form.cleaned_data['email']
            is_user_exists_with_mail = User.objects.filter(email=mail)

            # Проверка на уникальность username (он должен быть уникальным естественно)
            if is_user_exists_with_mail.exists():
                messages.error(request, "This mail are exists. Please retype the mail and try again")
            else:
                user_form.save()
                return redirect(reverse('main_page'))
        else:
            messages.error(request, "Error in the changing data")
    else:
        user_form = UserSettingsForm(instance=request.user)

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'form': user_form,
        'hide_nav_bar': 0,
        'title_page': 'Форма изменения данных',
        'text_button': 'Изменить данные',
        'is_administrative_zone': 0
    })

# Эта смена пароля (не сброс пароля, это другое)
def change_password(request):
    if not request.user.is_authenticated:
        return HttpResponseNotFound()

    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Важно: пароли у нас хешируются. Поэтому обновляем хеш
            auth.update_session_auth_hash(request, user)
            return redirect(reverse('main_page'))
        else:
            messages.error(request, "Error in changing the password")
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'admin_pages/forms/form_create_object.html', {
        'form': form,
        'hide_nav_bar': 0,
        'title_page': 'Форма изменения пароля',
        'text_button': 'Изменить пароль',
        'is_administrative_zone': 0
    })

# Метод позволяет получить информацию о пользователе
def show_user_data(request):
    data = User.objects.filter(username=request.user.username)
    return render(request, 'client_pages/user_data.html', {
        'table': data,
        'hide_nav_bar': 0,
        'title_page': 'Личная информация',
        'text_button': 'Изменить данные',
        'is_administrative_zone': 0
    })