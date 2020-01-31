from rest_framework.views import exception_handler


def core_exception_handler(exc, context):

    handlers = {
        'NotFound': _handle_not_found_error,
        'ValidationError': _handle_generic_error}

    response = exception_handler(exc, context)

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)
    else:
        if not response:
            return {'errors':'none'}
        if 'errors' not in response:
            response.data = {'errors': response.data}
        return response    

def _handle_generic_error(exc, context, response):
    response.data = {
        'errors': response.data
    }
    return response


def _handle_not_found_error(exc, context, response):
    view = context.get('view', None)
    if view and hasattr(view, 'queryset') and view.queryset is not None:
        error_key = view.queryset.model._meta.verbose_name

        response.data = {
            'errors': {
                error_key: response.data['detail']
            }
        }
    else:
        response = _handle_generic_error(exc, contex, response)

    return response
