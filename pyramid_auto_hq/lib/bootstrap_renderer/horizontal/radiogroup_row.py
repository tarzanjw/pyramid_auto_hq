__author__ = 'tarzan'

from pyramid.compat import escape
from formencode import variabledecode
from . import HorizontalRowRenderer

class RadioGroupRowRenderer(HorizontalRowRenderer):
    inline = False

    def render_control(self, name, **attrs):
        inline = attrs.get('inline', self.inline)
        schema = self.schema
        field = schema.fields[name]
        try:
            options = field.options
        except AttributeError:
            try:
                options = getattr(schema, name + '_options')
            except AttributeError:
                pass
        assert options, "You have specify option" \
                        " by arg or schema." + name + "_options"

        selected_value = self.form.data.get(name, None)
        checkboxes = []
        class_ = 'radio-inline' if inline else 'radio'
        id = attrs['id'] = self.form_renderer.populate_input_id(name, **attrs)
        i = 0
        for value, label in options:
            check = u' checked' if value == selected_value else ''
            checkboxes.append(u"""
<div class="%(class)s">
  <label>
    <input type="radio" name="%(name)s" value="%(value)s" %(check)s>
    %(label)s
  </label>
</div>
"""
            % {
                'id': '%s_%d' % (id, i),
                'class': class_,
                'name': name,
                'value': escape(value),
                'label': label,
                'check': check,
            })
            i += 1
        return u"\n".join(checkboxes)