__author__ = 'tarzan'

from . import HorizontalRowRenderer


class CheckBoxRowRenderer(HorizontalRowRenderer):

    def __init__(self, input_name=None, **default_attrs):
        if input_name is None:
            input_name = 'checkbox'
        super(CheckBoxRowRenderer, self).__init__(input_name, **default_attrs)

    def __call__(self, name, **attrs):
        attrs['id'] = self.form_renderer.populate_input_id(name, **attrs)
        for k, v in self.default_attrs.items():
            attrs.setdefault(k, v)
        try:
            class_ = attrs['class_'] + ' form-group'
            del attrs['class_']
        except KeyError:
            class_ = 'form-group'

        label = attrs['label'] if 'label' in attrs \
            else ' '.join([word.capitalize() for word in name.split('_')])
        attrs['label'] = label
        try:
            attrs['class_'] = attrs['input_class']
            del attrs['input_class']
        except KeyError:
            pass
        error_html, error_css = self._render_error(name, **attrs)

        print self.form.data[name]

        return u"""<div class="%(class)s%(error_css)s">
    <div class="col-lg-offset-2 col-lg-10">
        <div class="checkbox">
            %(input)s
            %(error_html)s
        </div>
    </div>
</div>""" % {
            'class': class_,
            'label': label,
            'input': self.form_renderer.checkbox(name, **attrs),
            'error_css': error_css,
            'error_html': error_html,
        }
