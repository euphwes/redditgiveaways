from django.views.generic import TemplateView

# ----------------------------------------------------------------------------------------------------------------------

class HomePageView(TemplateView):
    """ Placeholder homepage view. """

    template_name = 'home/home.html'