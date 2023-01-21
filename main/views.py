from django.shortcuts import render
from main import forms
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404
from main import models

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
