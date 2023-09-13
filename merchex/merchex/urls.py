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
from django.urls import path
from listing import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('hello', views.hello),
    path('accueil', views.home),
    path('inscription', views.registration),
    path('flux', views.flux),
    path('abonnement', views.subscription),
    path('creation-ticket', views.create_ticket),
    path('nouvelle-critique', views.new_review),
    path('reponse-critique', views.critic_response),
    path('mes-posts', views.my_posts),
    path('modifier-critique', views.modify_review),
    path('modifier-ticket', views.modify_ticket),
    
]
