import json
from rest_framework.renderers import JSONRenderer
from rest_framework.utils.serializer_helpers import ReturnList


class OrderInventoryJSONRenderer(JSONRenderer):
    charset = 'utf-8'
    label = 'object'
    label_plural: 'objects'

    def render(self, data, media_type=None, renderer_contex=None):
        if not data:
            return None

        
        if isinstance(data,ReturnList):
            _data = json.loads(super(OrderInventoryJSONRenderer, self).render(data).decode('utf-8'))

            return json.dumps({self.label_plural:_data})   

        errors = data.get('errors', None)

        if errors is not None:
            return super(OrderInventoryJSONRenderer, self).render(data)

        return json.dumps({self.label: data})
