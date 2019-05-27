from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Browsing/playing
    path('courses/<course_id>/<questionnaire_n>/', views.BrowseQuestionnaire, name='browse-questionnaire'),
    path('courses/<course_id>/', views.BrowseCourse, name='browse-course'),
    path('courses/', views.Browse, name='browse'),

    # Editing
    path('edit/<course_id>/<questionnaire_n>/<question_n>/', views.EditQuestion, name='edit-question'),
    path('edit/<course_id>/<questionnaire_n>/', views.EditQuestionnaire, name='edit-questionnaire'),
    path('edit/<course_id>/', views.EditCourse, name='edit-course'),
    path('edit/', views.Edit, name='edit'),

    # Errors/ajax requests/misc
    path('access-denied/', views.ErrorAccessDenied, name='error-access-denied'),
    path('upload-info/', views.UploadInfo, name='upload-info'),
    path('ajax/like-course/', views.AjaxLikeCourse, name='ajax-like-course'),
    path('ajax/questionnaire-done/', views.AjaxQuestionnaireDone, name='ajax-questionnaire-done'),
]