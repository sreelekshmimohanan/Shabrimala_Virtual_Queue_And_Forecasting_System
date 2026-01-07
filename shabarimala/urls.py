"""shabarimala URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.urls import path
from . import views
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('',views.first, name='first'),
    path('index/',views.index, name='index'),
    path('reg/',views.reg, name='reg'),
    path('reg/addreg',views.addreg, name='addreg'),
    path('login/',views.login, name='login'),
    path('login/addlogin',views.addlogin, name='addlogin'),
    path('logout/',views.logout, name='logout'),
    path('viewuser/',views.viewuser, name='viewuser'),
    path('upload/',views.upload, name='upload'),
    path('add_slot/', views.add_slot, name='add_slot'),
    path('add_weather/', views.add_weather, name='add_weather'),
    path('book_slot/', views.book_slot, name='book_slot'),
    path('view_weather/', views.view_weather, name='view_weather'),
    path('view_booking/', views.view_booking, name='view_booking'),
    path('add_police/', views.add_police, name='add_police'),
    path('add_police/add_police_post', views.add_police_post, name='add_police_post'),
    path('add_emergency/', views.add_emergency, name='add_emergency'),
    path('add_emergency/add_emergency_post', views.add_emergency_post, name='add_emergency_post'),
    path('view_emergency/', views.view_emergency, name='view_emergency'),
    path('view_response/', views.view_response, name='view_response'),
    path('respond_emergency/<int:emergency_id>/', views.respond_emergency, name='respond_emergency'),
    path('add_medical_staff/', views.add_medical_staff, name='add_medical_staff'),
    path('add_medical_staff/add_medical_staff_post', views.add_medical_staff_post, name='add_medical_staff_post'),
    path('admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
