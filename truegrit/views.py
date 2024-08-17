from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User


class FrontPage(View):

    template_name = 'index.html'
    context = {}

    def get(self, request, *args, **kwargs):
        self.context["users"] = User.objects.all()
        return render(request, self.template_name, self.context)