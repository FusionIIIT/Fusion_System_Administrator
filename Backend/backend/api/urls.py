from django.urls import path
from . import views
from . import update_global_db

urlpatterns = [
    path('departments/', views.get_all_departments ,name='get_all_departments'),
    path('batches/', views.get_all_batches ,name='get_all_batches'),
    path('programmes/', views.get_all_programmes ,name='get_all_programmes'),
    path('get-user-roles-by-email/', views.get_user_role_by_email ,name='get_user_role_by_email'),
    path('update-user-roles/', views.update_user_roles ,name='update_user_roles'),
    path('view-roles/', views.global_designation_list ,name='global_designation_list'),
    path('view-designations/', views.get_category_designations ,name='get_category_designations'),
    path('create-role/', views.add_designation ,name='add_designation'),
    path('modify-role/', views.update_designation ,name='update_designation'),
    path('get-module-access/', views.get_module_access, name='get_module_access'),
    path('modify-roleaccess/', views.modify_moduleaccess ,name='modify_moduleaccess'),
    path('users/add-student/', views.add_individual_student, name='add_individual_student'),
    path('users/add-staff/', views.add_individual_staff, name='add_individual_staff'),
    path('users/add-faculty/', views.add_individual_faculty, name='add_individual_faculty'),
    path('users/reset_password/', views.reset_password, name='reset-password'),
    path('users/import/', views.bulk_import_users, name='bulk-import-users'),
    path('users/export/', views.bulk_export_users, name='bulk-export-users'),
    path('users/mail-batch/', views.mail_to_whole_batch, name='mail-to-whole-batch'),
    path('update-globals-db/', update_global_db.update_globals_db, name='update_globals_db'),
    path('download-sample-csv/', views.download_sample_csv, name='download_sample_csv'),
    path("users/", views.UserListView.as_view(), name='user-list'),
]
