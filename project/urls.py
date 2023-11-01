from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('post', views.post, name="post"),
    path('explore', views.explore, name="explore"),
    path('deviceSearch', views.deviceSearch, name="deviceSearch"),
    path('typeSearch', views.typeSearch, name="typeSearch"),
    path('show_device/<int:device_id>/', views.show_device, name="show_device"),
    path('createRecycleEvent', views.createRecycleEvent, name="createRecycleEvent"),
    path('recycle', views.recycle, name="recycle"),
    path('zipSearch', views.zipSearch, name="zipSearch"),
    path('delete_post/<int:device_id>/', views.delete_post, name="dlt_post"),
    path('sold/<int:device_id>/', views.sold, name="sold"),
    path('delete_event/<int:event_id>/', views.delete_event, name="dlt_event"),
    path('want_to_buy', views.send_email, name="send_email"),
]