__author__ = 'tarzan'

from .. import RowRenderer
from formencode.compound import CompoundValidator
from formencode import validators as builtin_validators


class SmartHorizontalInputRowRenderer(RowRenderer):
    def __call__(self, name, **attrs):
        schema = self.form.schema
        field = schema.fields[name]
        validators = field.validators \
            if isinstance(field, CompoundValidator) else [field, ]
        for validator in reversed(validators):
            input_tag = validator.input_tag \
                if hasattr(validator, 'input_tag') else None
            if not input_tag:
                if isinstance(validator, builtin_validators.OneOf):
                    input_tag = 'select'
                elif isinstance(validator, builtin_validators.Bool):
                    input_tag = 'checkbox'
                elif  isinstance(validator, builtin_validators.Set):
                    input_tag = 'checkboxlist'
            if input_tag:
                break

        if input_tag == 'select': # render a select box
            try:
                options = getattr(schema, name + '_options')
                return self.form_renderer.select_row(name, options=options, **attrs)
            except AttributeError:
                pass
        elif input_tag in ('checkbox', 'textarea'):
            return getattr(self.form_renderer, input_tag + '_row')(name, **attrs)
        elif input_tag in ('checkboxlist',):
            return getattr(self.form_renderer, input_tag + '_row')(name, **attrs)

        # render text for default in case of input_tag can not be detected
        return self.form_renderer.text_row(name, **attrs)