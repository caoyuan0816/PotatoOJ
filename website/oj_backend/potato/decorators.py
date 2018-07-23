from django.apps import apps
from django.db.models import Model
from django.db.models.base import ModelBase
from django.db.models.query import QuerySet
from django.utils.functional import wraps
from django.shortcuts import get_object_or_404
from django.http.response import Http404
from rest_framework.response import Response

import traceback
import sys


def action_response(func):
    """
    Decorator for rest framework style response, if func raise any Exception, decorator will return fail response
    :param func:
    :return: {'success': False, 'detail': str(e) } if func raise Exception
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        content = {'success': True}
        try:
            content['detail'] = func(*args, **kwargs)
            return Response(content)
        except Exception as e:
            content['success'] = False
            content['detail'] = str(e)
            traceback.print_exception(*sys.exc_info())
            return Response(content)
    return wrapper


def require_permission(perm, lookup_variables=None):
    """
    Decorator for Model Object Permission check.
    Reuse code from permission_required and permission_required_or_403 of django-guardian, and usage is similar,
    check http://django-guardian.readthedocs.io/en/stable/userguide/check.html#using-decorators.
    Note that if lookup_variables is wrong the decorator will raise Exception
    that might cause http request return not formatted response
    :param perm: permission to be required
    :param lookup_variables:
    :return: {'success': False, 'detail': 'Not authorized to access'} if don't have permission
    """
    # Check if perm is given as string in order not to decorate
    # view function itself which makes debugging harder
    if not isinstance(perm, str):
        raise Exception("First argument must be in format: "
                        "'app_label.codename or a callable which return similar string'")

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # if more than one parameter is passed to the decorator we try to
            # fetch object for which check would be made
            obj = None
            if lookup_variables:
                model, lookups = lookup_variables[0], lookup_variables[1:]
                # Parse model
                if isinstance(model, str):
                    splitted = model.split('.')
                    if len(splitted) != 2:
                        raise Exception("If model should be looked up from "
                                        "string it needs format: 'app_label.ModelClass'")
                    model = apps.get_model(*splitted)
                elif issubclass(model.__class__, (Model, ModelBase, QuerySet)):
                    pass
                else:
                    raise Exception("First lookup argument must always be "
                                    "a model, string pointing at app/model or queryset. "
                                    "Given: %s (type: %s)" % (model, type(model)))
                # Parse lookups
                if len(lookups) % 2 != 0:
                    raise Exception("Lookup variables must be provided as pairs of lookup_string and view_arg")
                lookup_dict = {}
                for lookup, view_arg in zip(lookups[::2], lookups[1::2]):
                    if view_arg not in kwargs:
                        raise Exception("Argument %s was not passed into view function" % view_arg)
                    lookup_dict[lookup] = kwargs[view_arg]

                try:
                    obj = get_object_or_404(model, **lookup_dict)
                except Http404:
                    return Response({'success': False, 'detail': 'Object Not found'})

            has_permissions = request.user.has_perm(perm) or request.user.has_perm(perm, obj)

            if not has_permissions:
                return Response({'success': False, 'detail': 'Not authorized to access'})

            return view_func(request, *args, **kwargs)

        return wraps(view_func)(_wrapped_view)

    return decorator
