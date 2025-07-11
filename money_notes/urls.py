"""
URL configuration for money_notes project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from django.conf.urls.static import static
from django.conf import settings

from main import views as main_view

urlpatterns = [
    path(route="", view=main_view.login_page, name="login_page"),
    path(route="logout",view=main_view.logout_page, name="logout_page"),
    path(route="create-account", view=main_view.create_account_page, name="create_account"),
    path(route="delete-account", view=main_view.delete_account, name="delete_account"),
    path(route="verify-email/<str:email>", view=main_view.verify_email, name="verify_email"),
    path(route="forgot-password", view=main_view.forgot_password, name="forgot_password"),
    path(route="send-otp/<str:email>", view=main_view.send_otp, name="send_otp"),
    path(route="verify-otp/<str:entered_otp>", view=main_view.verify_otp, name="verify_otp"),

    path(route="add-data", view=main_view.add_data, name="add_data"),
    path(route="get-data", view=main_view.get_data, name="get_data"),
    path(route="update-record/<int:id>", view=main_view.update_record, name="update_record"),
    path(route="delete-record/<int:id>/<str:query_url>", view=main_view.delete_record, name="delete_record"),
    path('admin/', admin.site.urls),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS)