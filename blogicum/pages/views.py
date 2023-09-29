from django.views import View
from django.shortcuts import render

class AboutView(View):
    template_name = 'pages/about.html'

    def get(self, request, args, **kwargs):
        return render(request, self.template_name)

class RulesView(View):
    template_name = 'pages/rules.html'

    def get(self, request,args, **kwargs):
        return render(request, self.template_name)

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def csrf_fail(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)

def server_error(request, exception=''):
    return render(request, 'pages/500.html', status=404)