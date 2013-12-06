__author__ = 'tarzan'

from .. import FormRenderer, FormRendererMetaClass, RowRenderer
from webhelpers.html.builder import format_attrs

class HorizontalRowRenderer(RowRenderer):
    def _render_error(self, name, **attrs):
        return self.form_renderer._render_error(name, **attrs)

    def _form_group(self, name, controls, id=None,  **attrs):
        attrs = self.form_renderer.attributes_for_row(**attrs)
        try:
            label = attrs['label']
            del attrs['label']
        except KeyError:
            label = ' '.join([word.capitalize() for word in name.split('_')])

        try:
            class_ = attrs['class_'] + ' form-group'
            del attrs['class_']
        except KeyError:
            class_ = 'form-group'

        attrs_html = format_attrs(**attrs)
        error_html, error_css = self._render_error(name, id=id, **attrs)
        return u"""
<div class="%(classes)s%(error_css)s" %(attrs_html)s>
    <label class="col-lg-2 control-label" for="%(id)s">%(label)s</label>
    <div class="col-lg-10">
        %(controls)s
        %(error_html)s
    </div>
</div>
""" % {
            'classes': class_,
            'error_css': error_css,
            'attrs_html': attrs_html,
            'label': label,
            'id': id,
            'controls': controls,
            'error_html': error_html,
        }

    def render_control(self, name, **attrs):
        for k, v in self.default_attrs.items():
            attrs.setdefault(k, v)
        try:
            attrs['class_'] = attrs['in`put_class']
            del attrs['input_class']
        except KeyError:
            try:
                del attrs['class_']
            except KeyError:
                pass

        attrs = self.form_renderer.attributes_for_input(**attrs)
        try:
            attrs['class_'] = attrs['class_'] + ' form-control'
        except KeyError:
            attrs['class_'] = 'form-control'
        return getattr(self.form_renderer, self.input_name)(name, **attrs)

    def __call__(self, name, **attrs):
        attrs['id'] = self.form_renderer.populate_input_id(name, **attrs)
        return self._form_group(name, self.render_control(name, **attrs), **attrs)

from smart_input_row import SmartHorizontalInputRowRenderer
from radiogroup_row import RadioGroupRowRenderer
from checkboxlist_row import HorizontalCheckboxListRowRenderer
from checkbox_row import CheckBoxRowRenderer

class HorizontalFormRenderer(FormRenderer):
    __metaclass__ = FormRendererMetaClass

    _input_attrs = ['id', 'options', 'selected_value',]

    def populate_input_id(self, name, **attrs):
        try:
            id_ = attrs['id']
            if not id_:
                raise KeyError
        except KeyError:
            id_ = 'input_%s' % name
        return id_

    def _render_error(self, name, **attrs):
        id = self.populate_input_id(name, **attrs)
        if self.is_error(name):
            error_list = self.errors_for(name)
            error_html = ""
            for err in error_list:
                error_html = error_html + u'<span style="" id="%s_em_" class="help-block">' \
                                            u'<small><em>%s</em></small>' \
                                          u'</span>' % (id, err)
            error_css = u' has-error'
        else:
            error_html = u''
            error_css = u''
        return error_html, error_css

    def attributes_for_row(self, **attrs):
        return {k:v for k,v in attrs.items() if k not in self._input_attrs}

    def attributes_for_input(self, **attrs):
        _attrs = {}
        for k, v in attrs.items():
            if k in self._input_attrs:
                _attrs[k] = v
            if k.startswith('input_'):
                _attrs[k[6:]] = v

        return _attrs

    smart_input_row = SmartHorizontalInputRowRenderer()
    text_row = HorizontalRowRenderer('text')
    select_row = HorizontalRowRenderer('select')
    checkbox_row = CheckBoxRowRenderer()
    textarea_row = HorizontalRowRenderer('textarea', rows=5)
    checkboxlist_row = HorizontalCheckboxListRowRenderer()
    radiogroup_row = RadioGroupRowRenderer()

