from django.template.loader import render_to_string
from django.http import HttpResponse


class ErrorPagesMiddleware:
    """Affiche les pages d'erreur personnalisées 401 et 405."""

    TEMPLATES = {401: '401.html', 405: '405.html'}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        template = self.TEMPLATES.get(response.status_code)
        if template and 'text/html' in response.get('Content-Type', 'text/html') \
                and not getattr(response, 'streaming', False):
            new = HttpResponse(
                render_to_string(template, request=request),
                status=response.status_code,
            )
            for header in ('Allow', 'WWW-Authenticate'):
                if response.has_header(header):
                    new[header] = response[header]
            return new
        return response
