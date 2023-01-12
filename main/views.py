from django.shortcuts import render
from main import forms
from django.views.generic.edit import FormView
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
class ContactUsView(FormView):
    template_name = "contact_form.html"
    form_class = forms.ContactForm
    success_url = "/"

    def form_valid(self, form) -> HttpResponse:
        form.send_mail()
        return super().form_valid(form)


# # Function based views are simpler for me to understand
# def contact_us(request):
#     if request.method == "POST":
#         form = forms.ContactForm(request.POST)
#         if form.is_valid():
#             form.send_mail()
#             return render(request, "home.html", {})
#     else:
#         form = forms.ContactForm()

#     return render(request, "contact_form.html", {"form": form})