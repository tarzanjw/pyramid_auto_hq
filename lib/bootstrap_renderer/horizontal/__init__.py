__author__ = 'tarzan'

from .. import FormRenderer, FormRendererMetaClass, RowRenderer

class HorizontalRowRenderer(RowRenderer):
    def _form_group(self, name, controls, id=None,  **attrs):
        label = attrs['label'] if 'label' in attrs \
            else ' '.join([word.capitalize() for word in name.split('_')])

        form_renderer = self.form_renderer
        if form_renderer.is_error(name):
            error_list = form_renderer.errors_for(name)
            error_html = ""
            for err in error_list:
                error_html = error_html + u'<span style="" id="%s_em_" class="help-block">' \
                                            u'<small><em>%s</em></small>' \
                                          u'</span>' % (id, err)
            error_css = u' has-error'
        else:
            error_html = ''
            error_css = ''

        return u"""
<div class="form-group%(error_css)s">
    <label class="col-lg-2 control-label" for="%(id)s">%(label)s</label>
    <div class="col-lg-10">
        %(controls)s
        %(error_html)s
    </div>
</div>
""" % {
            'error_css': error_css,
            'label': label,
            'id': id,
            'controls': controls,
            'error_html': error_html,
        }

    def render_control(self, name, **attrs):
        for k, v in self.default_attrs.items():
            attrs.setdefault(k, v)
        attrs['class_'] = attrs['class_'] + ' form-control' \
            if 'class_' in attrs else 'form-control'
        return getattr(self.form_renderer, self.input_name)(name, **attrs)

    def __call__(self, name, **attrs):
        if 'id' not in attrs or not attrs['id']:
            attrs['id'] = 'input_%s' % name
        return self._form_group(name, self.render_control(name, **attrs), **attrs)

from smart_input_row import SmartHorizontalInputRowRenderer
from radiogroup_row import RadioGroupRowRenderer
from checkboxlist_row import HorizontalCheckboxListRowRenderer

class HorizontalFormRenderer(FormRenderer):
    __metaclass__ = FormRendererMetaClass

    smart_input_row = SmartHorizontalInputRowRenderer()
    text_row = HorizontalRowRenderer('text')
    select_row = HorizontalRowRenderer('select')
    checkbox_row = HorizontalRowRenderer('checkbox')
    textarea_row = HorizontalRowRenderer('textarea', rows=5)
    checkboxlist_row = HorizontalCheckboxListRowRenderer()
    radiogroup_row = RadioGroupRowRenderer()

