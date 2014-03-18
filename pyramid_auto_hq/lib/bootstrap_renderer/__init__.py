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
        """
        @rtype: FormRenderer
        """
        return self.form_renderer.form

    @property
    def schema(self):
        return self.form.schema

    def populate_element_id(self, prefix, id):
        return self.form_renderer.populate_element_id(prefix, id)

    def populate_form_group_id(self, id):
        return self.form_renderer.populate_form_group_id(id)

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

    def populate_element_id(self, prefix, id):
        return prefix + '-' + id

    def populate_form_group_id(self, id):
        return self.populate_element_id('frmGrp', id)

    def populate_error_message_id(self, id):
        return self.populate_element_id('errMsg', id)

    def populate_input_id(self, name, **attrs):
        try:
            id_ = attrs['id']
            if not id_:
                raise KeyError
        except KeyError:
            id_ = 'input-%s' % name
        return id_

    def __init__(self, *args, **kwargs):
        for name, renderer in self.__child_renderers__.items():
            renderer = copy.copy(renderer)
            renderer.form_renderer = self
            setattr(self, name, renderer)
        return super(FormRenderer, self).__init__(*args, **kwargs)

    def smart_render(self):
        schema = self.form.schema
        fields_order = copy.copy(schema.smart_fields_order) \
            if hasattr(schema, 'smart_fields_order') else []
        for field_name in schema.fields:
            if not field_name in fields_order:
                fields_order.append(field_name)
        return "\n".join([self.smart_input_row(name) for name in fields_order])

    @staticmethod
    def errors_to_ajax_response(form):
        errors = []
        for field, err_msg in form.errors.items():
            errors.append((field, err_msg))
        return errors

    @property
    def js_to_show_errors(self):
        return """<script type="text/javascript">
jQuery(function ($) {
    $.fn.show_error_for_field = function(field, err_msg) {
        var $form = $(this)
        var $input = $form.find("[name=" + field + "]")
        $input.each(function (idx, el) {
            var $el = $(el)
            var $frmGrp = $el.parents(".form-group").first()
            var $err = $frmGrp.find(".help-block")
            $frmGrp.addClass("has-error")
            $err.html("<small><em>" + err_msg + "</em></small>")
        })
    }

    $.fn.show_errors = function (errors) {
        var fn, err_msg
        for (i=0;i<errors.length;i++) {
            fn = errors[i][0]
            err_msg = errors[i][1]
            $(this).show_error_for_field(fn, err_msg)
        }
    }
})
</script>"""
from horizontal import HorizontalFormRenderer