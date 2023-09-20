"""merchex URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from django.contrib.auth import views as auth_views
from listing import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accueil', views.home),
    path('inscription', views.registration),
    path('app/flux', views.flux, name='flux'),
    path('app/abonnement', views.subscription),
    path('app/creation-ticket', views.create_ticket, name='creation-ticket'),
    path('app/nouvelle-critique', views.create_combined, name='nouvelle-critique'),
    #path('app/reponse-critique', views.critic_response),
    path('app/mes-posts', views.my_posts, name='mes-posts'),
    path('app/modifier-critique', views.modify_review),
    path('modifier-ticket/<int:ticket_id>/', views.modify_ticket, name='modifier-ticket'),
    path('delete-ticket/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('accueil/', auth_views.LogoutView.as_view(), name='logout'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)