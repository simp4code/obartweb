from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),    
    path('logout/', views.user_logout, name='logout'),
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('home_page/', views.homepage, name='home'),
    # path('activate/<int:uid>/', views.activate_account, name='activate'),
    path('ask_code/',views.ask_code,name="ask_code"),
    path('ask_code/verify_codes',views.verify_codes,name="verify_codes"),
    path('admin-page/', views.admin_page, name='admin_page'),
    path('admin-page/check_codes',views.check_codes,name='check_codes'),
    path('admin-page/check_codes/generate_code',views.generate_code,name='generate_code'),
    path('admin-page/check_codes/remove_old_codes',views.remove_old_codes,name='remove_old_codes'),
    path('admin-page/add_video', views.add_video_content, name='add_video'),
    path('admin-page/update_video/<int:video_id>/', views.update_video, name='update_video'),
    path('admin-page/delete_video/<int:video_id>/', views.delete_video, name='delete_video'),


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)