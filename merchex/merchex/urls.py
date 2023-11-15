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
from django.conf import settings
from django.contrib import admin
from listing import views
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accueil', views.home),
    path('inscription', views.registration),
    # UTILISATEUR CONNECTE
    path('app/flux', views.flux, name='flux'),
    path('app/mes-posts', views.my_posts, name='mes-posts'),
    path('app/available_users/', views.available_users, name='available_users'),
    # path('app/available_users/', views.subscribe_user, name="subscribe_user"),
    path('accueil', auth_views.LogoutView.as_view(), name='logout'),
    path('app/creation-ticket', views.create_ticket, name='creation-ticket'),
    path('app/nouvelle-critique-2/<int:ticket_id>/', views.nouvelle_critique_2, name='nouvelle-critique-2'),
    path('app/nouvelle-critique', views.create_combined, name='nouvelle-critique'),
    path('app/modifier-critique', views.modify_review),
    path('app/modifier-ticket/<int:ticket_id>/', views.modify_ticket, name='modifier-ticket'),
    path('delete-ticket/<int:ticket_id>/', views.delete_ticket, name='delete-ticket'),
    path('view-review/<int:review_id>/', views.view_review, name='view_review'),
    path('ticket/<int:ticket_id>/', views.view_ticket, name='view_ticket'),
    path('app/followers/', views.followers, name='followers'),
    path('follow/<int:user_id>/', views.follow, name='follow'),
    path('unfollow/<int:user_id>/', views.unfollow, name='unfollow'),
    # path('app/search_users/', views.search_users, name='search_users'),
    path("subscribe/", views.subscribe_user, name="subscribe_user"),
    path('app/get_subscriptions/', views.get_subscriptions, name='get_subscriptions'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    