from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from main import views
from django.conf import settings
from django.conf.urls.static import static
from main import models
from django.contrib.auth import views as auth_views
from main import forms

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about-us/", TemplateView.as_view(template_name="about_us.html"), name="about_us"),
    path("contact-us/", views.ContactUsView.as_view(), name="contact_us"),
    path("products/<slug:tag>/", views.ProductListView.as_view(), name="products"),
    path("product/<slug:slug>/",
         DetailView.as_view(model=models.Product, template_name="product_detail.html"),
         name="product"),
    path("signup/", views.SignupView.as_view(), name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html",
         form_class=forms.AuthenticationForm,), name="login",),
    path("address/", views.AddressListView.as_view(template_name="address_list.html"), name="address_list",),
    path("address/create/", views.AddressCreateView.as_view(template_name="address_form.html"), name="address_create",),
    path("address/<int:pk>/", views.AddressUpdateView.as_view(template_name="address_update.html"), name="address_update",),
    path("address/<int:pk>/delete/", views.AddressDeleteView.as_view(template_name="address_confirm_delete.html"), name="address_delete",),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
