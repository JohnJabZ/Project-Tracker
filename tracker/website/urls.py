from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # I made Survey Dashboard as Default
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),

    # Survey Paths
    path('survey/', views.survey_list, name='survey'),
    path('survey/<int:pk>/', views.survey_detail, name='survey_detail'),
    path('delete_survey_record/<int:pk>/',
         views.delete_survey_record, name='delete_survey_record'),
    path('add_survey_record/', views.add_survey_record, name='add_survey_record'),
    path('update_survey_record/<int:pk>', views.update_survey_record,
         name='update_survey_record'),
    path('survey/export/', views.export_survey_data, name="export_survey_csv"),
    path('survey/export/excel/', views.export_survey_excel,
         name="export_survey_excel"),
    path('survey/import/', views.import_survey_view, name="import_survey"),
    path('survey/filter/<str:filter_type>/',
         views.survey_filter, name='survey_filter'),

    # Dashboard Paths
    path('dashboard_design', views.dashboard_design, name='dashboard_design'),
    path('dashboard_asbuilt', views.dashboard_asbuilt, name='dashboard_asbuilt'),
    path('dashboard_sor', views.dashboard_sor, name='dashboard_sor'),


    # Design Paths
    path('design/', views.design_list, name='design'),
    path('design/<int:pk>/', views.design_detail, name='design_detail'),
    path('add_design_record/', views.add_design_record, name='add_design_record'),
    path('update_design_record/<int:pk>', views.update_design_record,
         name='update_design_record'),
    path('delete_design_record/<int:pk>/',
         views.delete_design_record, name='delete_design_record'),
    path('design/filter/<str:filter_type>/',
         views.design_filter, name='design_filter'),
    path('design/export/', views.export_design_csv, name="export_design_csv"),
    path('design/export/excel/', views.export_design_excel,
         name="export_design_excel"),
    path('design/import/', views.import_design_view, name="import_design"),
]
