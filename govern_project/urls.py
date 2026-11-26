"""
URL configuration for govern_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from govern_app import views
from govern_project import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index,name='index'),
    path('get_lgd_records/',views.get_lgd_records,name='get_lgd_records'),
    path('citizen_registration/',views.citizen_registration,name='citizen_registration'),
    path('login/',views.view_login,name='login'),
    path('adminhome/',views.adminhome,name='adminhome'),
    path('citizenhome/',views.citizenhome,name='citizenhome'),
    path('view_citizen/',views.view_citizen,name='view_citizen'),
    path('edit_citizen/<int:citizen_id>/',views.edit_citizen,name='edit_citizen'),
    path('delete_citizen/<int:citizen_id>/',views.delete_citizen,name='delete_citizen'),
    path('validate_officer_location/',views.validate_officer_location,name='validate_officer_location'),
    path('add_officer/',views.add_officer,name='add_officer'),
    path('view_officer/',views.view_officer,name='view_officer'),
    path('edit_officer/<int:officer_id>/',views.edit_officer,name='edit_officer'),
    path('delete_officer/<int:officer_id>/',views.delete_officer,name='delete_officer'),
    path('officerhome/',views.officerhome,name='officerhome'),
    path('help/',views.help,name='help'),
    path('privacy/',views.privacy,name='privacy'),
    path('terms/',views.terms,name='terms'),
    path('accessibility/',views.accessibility,name='accessibility'),
    path('contact/',views.contact,name='contact'),
    path('logout/',views.logout_view,name='logout'),
    path('view_citizen_profile/<int:citizen_id>/',views.view_citizen_profile,name='view_citizen_profile'),
    path('view_officer_profile/<int:officer_id>/',views.view_officer_profile,name='view_officer_profile'),
    path('citizen_view_officer_activity/',views.view_officer_activity,name='citizen_view_officer_activity'),
    path('add_officer_activity/',views.add_officer_activity,name='add_officer_activity'),
    path('view_officeractivity/',views.view_officeractivity,name='view_officeractivity'),
    path('edit_officeractivity/<int:activity_id>/',views.edit_officeractivity,name='edit_officeractivity'),
    path('delete_officeractivity/<int:activity_id>/',views.delete_officeractivity,name='delete_officeractivity'),
    path('add_citizen_feedback/',views.add_citizen_feedback,name='add_citizen_feedback'),
    path('view_citizen_feedback/',views.view_citizen_feedback,name='view_citizen_feedback'),
    path('edit_citizen_feedback/<int:feedback_id>/',views.edit_citizen_feedback,name='edit_citizen_feedback'),
    path('delete_citizen_feedback/<int:feedback_id>/',views.delete_citizen_feedback,name='delete_citizen_feedback'),
    path('view_officer_feedback/',views.view_officer_feedback,name='view_officer_feedback'),
    path('view_all_citizen_feedback/',views.view_all_citizen_feedback,name='view_all_citizen_feedback'),
    
    ]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)    