__author__ = 'tarzan'
from pyramid_simpleform import renderers as _sf_renderers
import copy

class RowRenderer(object):
    input_name = None
    form_renderer = None
    default_attrs = {}

    def __init__(self, input_name=None, **default_attrs):
        self.input_name = input_name
        self.default_attrs = default_attrs

    @property
    def form(self):
        return self.form_renderer.form

    @property
    def schema(self):
        return self.form.schema

class FormRendererMetaClass(type):
    def __new__(meta, class_name, bases, new_attrs):
        cls = type.__new__(meta, class_name, bases, new_attrs)
        for name, value in new_attrs.items():
            if isinstance(value, RowRenderer):
                cls.__child_renderers__[name] = value
        return cls

class FormRenderer(_sf_renderers.FormRenderer):
    __metaclass__ = FormRendererMetaClass
    __child_renderers__ = {}


    def __init__(self, *args, **kwargs):
        for name, renderer in self.__child_renderers__.items():
            renderer = copy.copy(renderer)
            renderer.form_renderer = self
            setattr(self, name, renderer)
        return super(FormRenderer, self).__init__(*args, **kwargs)


    # def radiogroup_row(self, name, options, selected_value=None, id=None, **attrs):
    #     id = id or ('input_%s' % name)
    #     selected_value = selected_value if selected_value is not None else self.data.get(name)
    #     controls = ""
    #     index = 0
    #     for opt in options:
    #         value, label = opt
    #         checked = 'checked="checked"' if selected_value == value else ''
    #         radio = u'<label class="radio inline">' \
    #                     u'<input type="radio" id="%(id)s" name="%(name)s" value="%(value)s" %(checked)s>' \
    #                     u'%(label)s' \
    #                 u'</label>' % {
    #             'id': id + ('_%d' %index),
    #             'name': name,
    #             'value': value,
    #             'checked': checked,
    #             'label': label,
    #         }
    #         controls = controls + radio
    #         index += 1
    #
    #     return self._form_group(name, controls, id, **attrs)

    def smart_render(self):
        schema = self.form.schema
        fields_order = copy.copy(schema.smart_fields_order) \
            if hasattr(schema, 'smart_fields_order') else []
        for field_name in schema.fields:
            if not field_name in fields_order:
                fields_order.append(field_name)
        return "\n".join([self.smart_input_row(name) for name in fields_order])

from horizontal import HorizontalFormRenderer