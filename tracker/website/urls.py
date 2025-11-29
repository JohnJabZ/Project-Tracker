from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('survey/', views.survey_list, name='survey'),
    path('survey/<int:pk>/', views.survey_detail, name='survey_detail'),
    path('delete_survey_record/<int:pk>/',
         views.delete_survey_record, name='delete_survey_record'),
    path('add_survey_record/', views.add_survey_record, name='add_survey_record'),
    path('update_survey_record/<int:pk>', views.update_survey_record,
         name='update_survey_record'),
    path("survey/export/", views.export_survey_data, name="export_survey_csv"),
    path("survey/export/excel/", views.export_survey_excel,
         name="export_survey_excel"),
    path("survey/import/", views.import_survey_view, name="import_survey"),

]
