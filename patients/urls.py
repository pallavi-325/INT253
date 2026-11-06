from django.urls import path
from .views import (
    ParentDashboardView,
    ChildListView,
    ChildDetailView,
    ChildCreateView,
    ChildUpdateView,
    SkinImageUploadView,
    SkinImageDeleteView,
)

app_name = 'patients'

urlpatterns = [
    path('dashboard/', ParentDashboardView.as_view(), name='parent_dashboard'),
    path('children/', ChildListView.as_view(), name='child_list'),
    path('children/add/', ChildCreateView.as_view(), name='child_create'),
    path('children/<int:pk>/', ChildDetailView.as_view(), name='child_detail'),
    path('children/<int:pk>/edit/', ChildUpdateView.as_view(), name='child_update'),
    path('skin-images/upload/', SkinImageUploadView.as_view(), name='upload_skin_image'),
    path('skin-images/<int:pk>/delete/', SkinImageDeleteView.as_view(), name='delete_skin_image'),
]
