from django.contrib import admin
from django.urls import path

from musem.views import *

urlpatterns = [
    # Доступ к админке
    path('admin/', admin.site.urls),
    # Доступ к нашей странице
    path('', my_first_view, name="main_page"),
    # Регистрация пользователей
    path('register/', register_user, name="register"),
    # Авторизация пользователей
    path('login/', login_user, name="login"),
    # Выход пользователей из системы
    path('logout/', logout_user, name="logout"),
    # Изменение пользовательских данных
    path('user_settings/', change_data_user, name="user_settings"),
    # Поосмотр клиентом информации о себе
    path('user_info/', show_user_data, name="user_data"),
    # Смена пользователем пароля
    path('change_password/', change_password, name="change_password"),
    path('service/<int:service_id>-<str:type_sort>', service_description, name="client_service_description"),
    # Ссылка, которая позволяет оставлять отзыв к конкретной услуге
    path('service/<int:service_id>/create_rating', client_create_rating, name="client_create_rating"),
    # Ссылка, которая позволяет менять отзыв к услуге
    path('service<int:service_id>/edit_rating', client_edit_rating, name="client_edit_rating"),
    # Ссылка, которая позволяет удалять отзыв к услуге
    path('service<int:service_id>/delete_rating', client_rating_delete, name="client_delete_rating"),
    # Ссылка, которая позволяет приобретать билет к конкретной услуге
    path('service<int:service_id>/buy_ticket', client_buy_ticket_to_museum, name="client_buy_ticket"),
    path('list_visiting/', client_list_visits, name="client_list_visits"),
    # Ссылка, которая позволяет клиенту удалить потенциальное посещение клиента в музей
    path('list_visiting/<int:revenue_id>/delete', client_delete_access_session, name="client_delete_access_session"),

    # Админские ссылки
    path('main_page_admin/', admin_main_page, name="main_page_admin"),
    path('main_page_admin/users', admin_client_list, name="clients_list"),
    path('main_page_admin/employees', admin_employee_list, name="employee_list"),
    path('main_page_admin/rating', admin_rating_list, name="rating_list"),
    path('main_page_admin/services', admin_services_list, name="services_list"),
    path('main_page_admin/revenues', admin_revenue_list, name="revenue_list"),
    path('main_page_admin/expense', admin_expense_list, name="expanse_list"),
    path('main_page_admin/sessions', admin_session_list, name="session_list"),
    path('main_page_admin/gik', admin_gik, name="gik_list"),
    path('main_page_admin/safety', admin_save_list, name="safety_list"),
    path('main_page_admin/inventory', admin_inventory_list, name="inventory_list"),
    path('main_page_admin/location', admin_location_list, name="location_list"),
    path('main_page_admin/salary_employee', admin_salary_employee_list, name="salary_employee_list"),
    # Ссылки на другие страницы (когда нажимаем на ссылку)

    path('main_page_admin/user/<int:user_id>', admin_client_description, name="user_description"),
    path('main_page_admin/employee/<int:employee_id>', admin_employee_description, name="employee_description"),
    path('main_page_admin/service/<int:service_id>', admin_service_description, name="service_description"),
    path('main_page_admin/rating/<int:rating_id>', admin_rating_description, name="rating_description"),
    path('main_page_admin/revenue<int:revenue_id>', admin_revenue_description, name="revenue_description"),
    path('main_page_admin/expense<int:expense_id>', admin_expense_description, name="expense_description"),
    path('main_page_admin/session<int:session_id>', admin_session_description, name="session_description"),
    path('main_page_admin/gik<int:gik_id>', admin_gik_description, name="gik_description"),
    path('main_page_admin/safe<int:safe_id>', admin_safe_description, name="safe_description"),
    path('main_page_admin/location<int:location_id>', admin_location_description, name="location_description"),
    path('main_page_admin/inventory<int:inventory_id>', admin_inventory_description, name="inventory_description"),
    path('main_page_admin/salary_employee<int:salary_id>', admin_salary_employee_description, name="salary_employee_description"),

    path('main_page_admin/service<int:service_id>/rating', admin_rating_service, name="rating_for_certain_service"),

    path('main_page_admin/location<int:location_id>/delete', admin_location_delete, name="delete_location"),
    path('main_page_admin/gik<int:gik_id>/delete', admin_gik_delete, name="delete_gik"),
    path('main_page_admin/service<int:service_id>/delete', admin_service_delete, name="delete_service"),
    path('main_page_admin/client<int:client_id><int:type_delete>/delete', admin_client_delete, name="delete_client"),
    path('main_page_admin/employee<int:employee_id><int:type_delete>/delete', admin_employee_delete, name="delete_employee"),
    path('main_page_admin/revenue<int:revenue_id>/delete', admin_revenue_delete, name="delete_revenue"),
    path('main_page_admin/expense<int:expense_id>/delete', admin_expense_delete, name="delete_expense"),
    path('main_page_admin/session<int:session_id>/delete', admin_session_delete, name="delete_session"),
    path('main_page_admin/inventory<int:inventory_id>/delete', admin_inventory_delete, name="delete_inventory"),
    path('main_page_admin/safe<int:safe_id>/delete', admin_safe_delete, name="delete_safe"),
    path('main_page_admin/salary_employee<int:salary_id>/delete', admin_salary_employee_delete, name="delete_salary_employee"),
    path('main_page_admin/rating<int:rating_id>/delete', admin_rating_delete, name="delete_rating"),

    path('main_page_admin/employees/create', admin_create_employee, name="create_employee"),
    path('main_page_admin/services/create', admin_create_service, name="create_service"),
    path('main_page_admin/expense/create', admin_create_expense, name="create_expense"),
    path('main_page_admin/revenue/create', admin_create_revenue, name="create_revenue"),
    path('main_page_admin/session/create', admin_create_session, name="create_session"),
    path('main_page_admin/gik/create', admin_create_gik, name="create_gik"),
    path('main_page_admin/safety/create', admin_create_safe, name="create_safe"),
    path('main_page_admin/location/create', admin_create_location, name="create_location"),
    path('main_page_admin/inventory/create', admin_create_inventory, name="create_inventory"),
    path('main_page_admin/salary_em/create', admin_create_salary_employee, name="create_salary"),

    # Ссылки на редактирование данных
    path('main_page_admin/employee<int:employee_id>/edit', admin_edit_employee, name="edit_employee"),
    path('main_page_admin/service<int:service_id>/edit', admin_edit_service, name="edit_service"),
    path('main_page_admin/revenue<int:revenue_id>/edit', admin_edit_revenue, name="edit_revenue"),
    path('main_page_admin/expense<int:expense_id>/edit', admin_edit_expense, name="edit_expense"),
    path('main_page_admin/session<int:session_id>/edit', admin_edit_session, name="edit_session"),
    path('main_page_admin/gik<int:gik_id>/edit', admin_edit_gik, name="edit_gik"),
    path('main_page_admin/safe<int:safe_id>/edit', admin_edit_safe, name="edit_safety"),
    path('main_page_admin/location<int:location_id>/edit', admin_edit_location, name="edit_location"),
    path('main_page_admin/inventory<int:inventory_id>/edit', admin_edit_inventory, name="edit_inventory"),
    path('main_page_admin/salary_emp<int:salary_employee_id>/edit', admin_edit_salary_employee, name="edit_salary_emp"),

    path('main_page_admin/gik<int:gik_id>/safe', get_safe_history_for_object, name="safe_description_for_gik"),

    path('main_page_admin/report_revenue', admin_calculate_report_revenue, name="report_revenue"),
    path('main_page_admin/report_expense', admin_calculate_report_expense, name="report_expense"),
    path('main_page_admin/report_earning', admin_calculate_report_earnings, name="report_earning"),
    path('main_page_admin/report_popular', admin_calculate_report_popular, name="report_popular"),
    path('main_page_admin/report_workload', admin_calculate_workload, name="report_workload"),

    path('main_page_admin/report_revenue/<int:month_id>', admin_get_data_by_month, name="report_revenue_description"),

]
