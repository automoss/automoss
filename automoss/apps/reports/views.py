from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.conf import settings
from django.http import HttpResponse
from django.template.loader import get_template

from .models import GeneratedReport
from xhtml2pdf import pisa

@method_decorator(login_required, name='dispatch')
class Index(View):
	""" Index view of report """

	def link(uri, rel):
		""" Convert HTML URIs to absolute path """
		return uri

	def render_pdf(request):
		""" Render the PDF """

		template_path = 'report.html'
		context = {} # TODO: add request here

		response = HttpResponse(content_type='application/pdf')
		response['Content-Disposition'] = 'attachment; filename="report.pdf"'

		# Retrieve the template
		template = get_template(template_path)

		# Parse template with context, and generate PDF from HTML
		html = template.render(context)
		if request.POST.get('show_html', ''):
			response['Content-Type'] = 'application/text'
			response['Content-Disposition'] = 'attachment; filename="report.txt"'
			response.write(html)
		else:
			pisaStatus = pisa.CreatePDF(html, dest=response, link_callback=link)
			if pisaStatus.err:
				return HttpResponse('Error: %s <pre>%s</pre>' % (pisaStatus.err, html))

		return response