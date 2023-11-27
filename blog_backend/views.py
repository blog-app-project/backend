import os

from django.http import HttpResponseBadRequest, HttpResponse


def media(request, file_path=None):
    from django.conf import settings as cfg
    media_root = getattr(cfg, 'MEDIA_ROOT', None)

    if not media_root:
        return HttpResponseBadRequest('Invalid Media Root Configuration')
    if not file_path:
        return HttpResponseBadRequest('Invalid File Path')

    with open(os.path.join(media_root, file_path), 'rb') as doc:
        response = HttpResponse(doc.read(), content_type='application/doc')
        response['Content-Disposition'] = 'filename=%s' % (file_path.split('/')[-1])
        return response