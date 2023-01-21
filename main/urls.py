from django.urls import path
from django.views.generic import TemplateView
from main import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    path("about-us/", TemplateView.as_view(template_name="about_us.html"), name="about_us"),
    path("contact-us/", views.ContactUsView.as_view(), name="contact_us"),
    path("products/<slug:tag>/", views.ProductListView.as_view(), name="products"),
] + static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
