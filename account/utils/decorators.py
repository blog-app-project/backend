from functools import wraps

from django.contrib.auth import get_user_model
from django.http import Http404


def staff_not_allowed(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        try:
            request.user.profile
        except get_user_model().profile.RelatedObjectDoesNotExist:
            raise Http404("Вам не разрешено это действие")

    return wrap
