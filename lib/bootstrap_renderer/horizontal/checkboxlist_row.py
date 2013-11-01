__author__ = 'tarzan'

from pyramid.compat import escape
from formencode import variabledecode
from . import HorizontalRowRenderer

class HorizontalCheckboxListRowRenderer(HorizontalRowRenderer):
    inline = False

    def _get_checked_values(self, name):
        posted_data = variabledecode.variable_decode(
            self.form.data,
            list_char=self.form.list_char)
        return posted_data[name] if name in posted_data and posted_data[name] else []

    def render_control(self, name, **attrs):
        schema = self.schema
        field = schema.fields[name]
        if hasattr(field, 'options'):
            options = field.options
        else:
            options_attr = name + '_options'
            if hasattr(schema, options_attr):
                options = getattr(schema, options_attr)
        assert options

        # v2l = {v:l for (v,l) in options}
        v2l = {}
        for (v,l) in options:
            v2l[v] = l
        n2v = variabledecode.variable_encode(v2l.keys(),
                                             list_char=self.form.list_char,
                                             prepend=name,
                                             add_repetitions=False)
        checkboxes = []
        class_ = 'checkbox-inline' if self.inline else 'checkbox'
        id = attrs['id'] if 'id' in attrs else 'input_' + name
        i = 0
        checked_values = self._get_checked_values(name)
        for name, value in n2v.items():
            label = v2l[value]
            check = u' checked="checked"' if value in checked_values else ''
            checkboxes.append(u"""
<div class="%(class)s">
  <label>
    <input type="checkbox" name="%(name)s" value="%(value)s" id="%(id)s"%(check)s>
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