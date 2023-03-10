from django.shortcuts import render
from main import forms
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.shortcuts import get_object_or_404, render
from main import models
import logging
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import (
    FormView,
    CreateView,
    UpdateView,
    DeleteView,
    )
from django.http import HttpResponseRedirect
from django.urls import reverse

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

class AddressListView(LoginRequiredMixin, ListView):
    model = models.Address

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = models.Address
    fields = [
        "name",
        "address1",
        "address2",
        "zip_code",
        "city",
        "country",
    ]
    success_url = reverse_lazy("address_list")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user # set database user to the correct logged in user
        obj.save()
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, UpdateView):
    model = models.Address
    fields = [
        "name",
        "address1",
        "address2",
        "zip_code",
        "city",
        "country",
    ]
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

class AddressDeleteView(LoginRequiredMixin, DeleteView):
    model = models.Address
    success_url = reverse_lazy("address_list")

    def get_queryset(self):
        return self.model.objects.filter(user=self.request.user)

def add_to_basket(request):
    product = get_object_or_404(
        models.Product, pk=request.GET.get("product_id")
    )
    basket = request.basket
    if not request.basket:
        if request.user.is_authenticated:
            user = request.user
        else:
            user = None
        basket = models.Basket.objects.create(user=user)
        request.session["basket_id"] = basket.id

    basketline , created = models.BasketLine.objects.get_or_create(
        basket=basket, product=product
    )
    if not created:
        basketline.quantity += 1
        basketline.save()
    return HttpResponseRedirect(
        reverse("product", args=(product.slug,))
    )

def manage_basket(request):
    if not request.basket:
        context = {
            "formset": None
        }
        return render(request, "basket.html", context)
    
    if request.method == "POST":
        formset = forms.BasketLineFormSet(
            request.POST, instance=request.basket
        )
        if formset.is_valid():
            formset.save()

    else:
        formset = forms.BasketLineFormSet(
            instance=request.basket
        )
    
    if request.basket.is_empty():
        context = {
            "formset": None
        }
        return render(request, "basket.html", context)

    return render(request, "basket.html", {"formset": formset})

class AddressSelectionView(LoginRequiredMixin, FormView):
    template_name = "address_selection.html"
    form_class = forms.AddressSelectionForm
    success_url = reverse_lazy("checkout_done")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        del self.request.session['basket_id']
        basket = self.request.basket
        basket.create_order(
            form.cleaned_data['billing_address'],
            form.cleaned_data['shipping_address']
            )
        return super().form_valid(form)