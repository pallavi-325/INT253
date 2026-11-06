from django.urls import path
from .views import (
    CustomLoginView,
    CustomLogoutView,
    ParentRegisterView,
    DoctorRegisterView,
    RoleBasedRedirectView,
)

app_name = 'accounts'

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('register/parent/', ParentRegisterView.as_view(), name='register_parent'),
    path('register/doctor/', DoctorRegisterView.as_view(), name='register_doctor'),
    path('dashboard-redirect/', RoleBasedRedirectView.as_view(), name='dashboard_redirect'),
]

