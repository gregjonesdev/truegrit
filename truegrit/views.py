from django.views.generic import View
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

class FrontPage(LoginRequiredMixin, View):

    template_name = 'index.html'
    context = {}

    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name, self.context)