from django.urls import path
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from main import views
from django.conf import settings
from django.conf.urls.static import static
from main import models

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about-us/", TemplateView.as_view(template_name="about_us.html"), name="about_us"),
    path("contact-us/", views.ContactUsView.as_view(), name="contact_us"),
    path("products/<slug:tag>/", views.ProductListView.as_view(), name="products"),
    path("product/<slug:slug>/",
         DetailView.as_view(model=models.Product, template_name="product_detail.html"),
         name="product"
        ),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
