from django.shortcuts import render
from main import forms
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from main import models
import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages

logger = logging.getLogger(__name__)

# Create your views here.
class ContactUsView(FormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form) -> HttpResponse:
        form.send_mail()
        return super().form_valid(form)

class ProductListView(ListView):
    template_name = "product_list.html"
    paginate_by = 4

    def get_queryset(self):
        tag = self.kwargs['tag']
        self.tag = None
        if tag != "all":
            self.tag = get_object_or_404(
                models.ProductTag, slug = tag
            )
        if self.tag:
            products = models.Product.object.active().filter(
                tags = self.tag
            )
        else:
            products = models.Product.object.active()

        return products.order_by("name")

class SignupView(FormView):
    template_name = "signup.html"
    form_class = forms.UserCreationForm

    def get_success_url(self) -> str:
        redirect_to = self.request.GET.get("next", "/")
        return redirect_to

    def form_valid(self, form) -> HttpResponse:
        response = super().form_valid(form)
        form.save()
        email = form.cleaned_data.get("email")
        raw_password = form.cleaned_data.get("password1")
        logger.info(
            "New signup for email=%s through SignupView", email
        )
        user = authenticate(email=email, password=raw_password)
        login(self.request, user)

        form.send_mail()
        messages.info(
            self.request, "You signed up successfully."
        )
        return response