from django.urls import path
from . import views
from . import update_global_db
from .views import login_view, logout_view, get_current_user, CustomTokenRefreshView

urlpatterns = [
    # Authentication endpoints
    path('auth/login/', login_view, name='login'),
    path('auth/logout/', logout_view, name='logout'),
    path('auth/token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', get_current_user, name='current_user'),
    
    # Existing endpoints
    path('departments/', views.get_all_departments ,name='get_all_departments'),
    path('batches/', views.get_all_batches ,name='get_all_batches'),
    path('programmes/', views.get_all_programmes ,name='get_all_programmes'),
    path('get-user-roles-by-username/', views.get_user_role_by_username ,name='get_user_role_by_username'),
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
    path('audit-logs/', views.get_audit_logs, name='get_audit_logs'),
    path('users/<str:username>/archive/', views.archive_user, name='archive_user'),
    path('users/<str:username>/restore/', views.restore_user, name='restore_user'),
]
