"""Form handling utilities for SLDK web framework.

Provides form building, validation, and processing capabilities.
"""


class FormField:
    """Base class for form fields."""
    
    def __init__(self, name, label=None, required=False, default=None, validators=None):
        """Initialize form field.
        
        Args:
            name: Field name
            label: Field label (defaults to name)
            required: Whether field is required
            default: Default value
            validators: List of validator functions
        """
        self.name = name
        self.label = label or name.replace('_', ' ').title()
        self.required = required
        self.default = default
        self.validators = validators or []
        self.value = default
        self.errors = []
    
    def validate(self, value):
        """Validate field value.
        
        Args:
            value: Value to validate
            
        Returns:
            bool: True if valid
        """
        self.errors = []
        self.value = value
        
        # Check required
        if self.required and (value is None or value == ''):
            self.errors.append(f"{self.label} is required")
            return False
        
        # Run custom validators
        for validator in self.validators:
            try:
                if not validator(value):
                    self.errors.append(f"{self.label} is invalid")
            except Exception as e:
                self.errors.append(str(e))
        
        return len(self.errors) == 0
    
    def render(self, value=None):
        """Render field HTML.
        
        Args:
            value: Current field value
            
        Returns:
            str: Field HTML
        """
        if value is None:
            value = self.value or self.default or ''
        
        return f'<input type="text" name="{self.name}" value="{value}">'


class TextField(FormField):
    """Text input field."""
    
    def __init__(self, name, label=None, required=False, default=None, 
                 validators=None, placeholder=None, max_length=None):
        super().__init__(name, label, required, default, validators)
        self.placeholder = placeholder
        self.max_length = max_length
    
    def render(self, value=None):
        """Render text field HTML."""
        if value is None:
            value = self.value or self.default or ''
        
        attrs = [f'type="text"', f'name="{self.name}"', f'value="{value}"']
        
        if self.placeholder:
            attrs.append(f'placeholder="{self.placeholder}"')
        
        if self.max_length:
            attrs.append(f'maxlength="{self.max_length}"')
        
        if self.required:
            attrs.append('required')
        
        return f'<input {" ".join(attrs)}>'


class NumberField(FormField):
    """Number input field."""
    
    def __init__(self, name, label=None, required=False, default=None,
                 validators=None, min_value=None, max_value=None, step=None):
        super().__init__(name, label, required, default, validators)
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
    
    def validate(self, value):
        """Validate number field."""
        if not super().validate(value):
            return False
        
        if value and value != '':
            try:
                num_value = float(value)
                
                if self.min_value is not None and num_value < self.min_value:
                    self.errors.append(f"{self.label} must be at least {self.min_value}")
                
                if self.max_value is not None and num_value > self.max_value:
                    self.errors.append(f"{self.label} must be at most {self.max_value}")
                    
            except ValueError:
                self.errors.append(f"{self.label} must be a number")
        
        return len(self.errors) == 0
    
    def render(self, value=None):
        """Render number field HTML."""
        if value is None:
            value = self.value or self.default or ''
        
        attrs = [f'type="number"', f'name="{self.name}"', f'value="{value}"']
        
        if self.min_value is not None:
            attrs.append(f'min="{self.min_value}"')
        
        if self.max_value is not None:
            attrs.append(f'max="{self.max_value}"')
        
        if self.step is not None:
            attrs.append(f'step="{self.step}"')
        
        if self.required:
            attrs.append('required')
        
        return f'<input {" ".join(attrs)}>'


class SelectField(FormField):
    """Select dropdown field."""
    
    def __init__(self, name, label=None, required=False, default=None,
                 validators=None, options=None):
        super().__init__(name, label, required, default, validators)
        self.options = options or []
    
    def validate(self, value):
        """Validate select field."""
        if not super().validate(value):
            return False
        
        if value and value != '':
            # Check if value is in options
            option_values = [opt[0] if isinstance(opt, tuple) else opt for opt in self.options]
            if value not in option_values:
                self.errors.append(f"{self.label} has invalid selection")
        
        return len(self.errors) == 0
    
    def render(self, value=None):
        """Render select field HTML."""
        if value is None:
            value = self.value or self.default or ''
        
        attrs = [f'name="{self.name}"']
        if self.required:
            attrs.append('required')
        
        html = [f'<select {" ".join(attrs)}>']
        
        for option in self.options:
            if isinstance(option, tuple):
                opt_value, opt_label = option
            else:
                opt_value = opt_label = option
            
            selected = ' selected' if str(opt_value) == str(value) else ''
            html.append(f'<option value="{opt_value}"{selected}>{opt_label}</option>')
        
        html.append('</select>')
        return '\n'.join(html)


class CheckboxField(FormField):
    """Checkbox field."""
    
    def __init__(self, name, label=None, required=False, default=False,
                 validators=None):
        super().__init__(name, label, required, default, validators)
    
    def render(self, value=None):
        """Render checkbox field HTML."""
        if value is None:
            value = self.value or self.default or False
        
        attrs = [f'type="checkbox"', f'name="{self.name}"', f'value="1"']
        
        if value:
            attrs.append('checked')
        
        if self.required:
            attrs.append('required')
        
        return f'<input {" ".join(attrs)}>'


class ColorField(FormField):
    """Color picker field."""
    
    def validate(self, value):
        """Validate color field."""
        if not super().validate(value):
            return False
        
        if value and value != '':
            # Simple hex color validation
            if not (value.startswith('#') and len(value) == 7):
                self.errors.append(f"{self.label} must be a valid hex color (e.g., #FF0000)")
        
        return len(self.errors) == 0
    
    def render(self, value=None):
        """Render color field HTML."""
        if value is None:
            value = self.value or self.default or '#000000'
        
        attrs = [f'type="color"', f'name="{self.name}"', f'value="{value}"']
        
        if self.required:
            attrs.append('required')
        
        return f'<input {" ".join(attrs)}>'


class FormBuilder:
    """Builder for creating and validating forms."""
    
    def __init__(self, action="/", method="POST"):
        """Initialize form builder.
        
        Args:
            action: Form action URL
            method: HTTP method
        """
        self.action = action
        self.method = method
        self.fields = {}
        self.field_order = []
        self.errors = []
    
    def add_field(self, field):
        """Add a field to the form.
        
        Args:
            field: FormField instance
            
        Returns:
            self: For method chaining
        """
        self.fields[field.name] = field
        if field.name not in self.field_order:
            self.field_order.append(field.name)
        return self
    
    def text_field(self, name, **kwargs):
        """Add a text field.
        
        Args:
            name: Field name
            **kwargs: Field options
            
        Returns:
            self: For method chaining
        """
        return self.add_field(TextField(name, **kwargs))
    
    def number_field(self, name, **kwargs):
        """Add a number field.
        
        Args:
            name: Field name
            **kwargs: Field options
            
        Returns:
            self: For method chaining
        """
        return self.add_field(NumberField(name, **kwargs))
    
    def select_field(self, name, options, **kwargs):
        """Add a select field.
        
        Args:
            name: Field name
            options: List of options
            **kwargs: Field options
            
        Returns:
            self: For method chaining
        """
        return self.add_field(SelectField(name, options=options, **kwargs))
    
    def checkbox_field(self, name, **kwargs):
        """Add a checkbox field.
        
        Args:
            name: Field name
            **kwargs: Field options
            
        Returns:
            self: For method chaining
        """
        return self.add_field(CheckboxField(name, **kwargs))
    
    def color_field(self, name, **kwargs):
        """Add a color field.
        
        Args:
            name: Field name
            **kwargs: Field options
            
        Returns:
            self: For method chaining
        """
        return self.add_field(ColorField(name, **kwargs))
    
    def validate(self, data):
        """Validate form data.
        
        Args:
            data: Form data dictionary
            
        Returns:
            bool: True if all fields are valid
        """
        self.errors = []
        all_valid = True
        
        for field_name, field in self.fields.items():
            field_value = data.get(field_name, '')
            if not field.validate(field_value):
                all_valid = False
                self.errors.extend(field.errors)
        
        return all_valid
    
    def get_data(self, data):
        """Get validated and processed form data.
        
        Args:
            data: Raw form data
            
        Returns:
            dict: Processed data
        """
        processed_data = {}
        
        for field_name, field in self.fields.items():
            raw_value = data.get(field_name, '')
            
            # Process based on field type
            if isinstance(field, NumberField):
                try:
                    processed_data[field_name] = float(raw_value) if raw_value else None
                except ValueError:
                    processed_data[field_name] = None
            elif isinstance(field, CheckboxField):
                processed_data[field_name] = raw_value in ['1', 'on', 'true', True]
            else:
                processed_data[field_name] = raw_value
        
        return processed_data
    
    def render(self, data=None, css_class="form"):
        """Render complete form HTML.
        
        Args:
            data: Current form data
            css_class: CSS class for form
            
        Returns:
            str: Complete form HTML
        """
        if data is None:
            data = {}
        
        html = [f'<form action="{self.action}" method="{self.method}" class="{css_class}">']
        
        # Render fields
        for field_name in self.field_order:
            field = self.fields[field_name]
            field_value = data.get(field_name, field.default)
            
            html.append('<div class="form-group">')
            html.append(f'<label for="{field_name}">{field.label}:</label>')
            
            # Add field HTML with id attribute
            field_html = field.render(field_value)
            field_html = field_html.replace(f'name="{field_name}"', 
                                           f'name="{field_name}" id="{field_name}"')
            html.append(field_html)
            
            # Add field errors
            if field.errors:
                html.append('<div class="field-errors">')
                for error in field.errors:
                    html.append(f'<span class="error">{error}</span>')
                html.append('</div>')
            
            html.append('</div>')
        
        # Add form errors
        if self.errors:
            html.append('<div class="form-errors">')
            for error in self.errors:
                html.append(f'<div class="error">{error}</div>')
            html.append('</div>')
        
        html.append('<div class="form-actions">')
        html.append('<button type="submit" class="btn btn-primary">Submit</button>')
        html.append('</div>')
        
        html.append('</form>')
        
        return '\n'.join(html)
    
    def render_field(self, field_name, data=None):
        """Render a single field.
        
        Args:
            field_name: Name of field to render
            data: Current form data
            
        Returns:
            str: Field HTML
        """
        if field_name not in self.fields:
            return ''
        
        field = self.fields[field_name]
        field_value = data.get(field_name, field.default) if data else field.default
        
        return field.render(field_value)


# Validation functions

def min_length(length):
    """Create a minimum length validator.
    
    Args:
        length: Minimum length
        
    Returns:
        function: Validator function
    """
    def validator(value):
        if value and len(str(value)) < length:
            raise ValueError(f"Must be at least {length} characters")
        return True
    return validator


def max_length(length):
    """Create a maximum length validator.
    
    Args:
        length: Maximum length
        
    Returns:
        function: Validator function
    """
    def validator(value):
        if value and len(str(value)) > length:
            raise ValueError(f"Must be at most {length} characters")
        return True
    return validator


def email_validator(value):
    """Validate email format.
    
    Args:
        value: Email value
        
    Returns:
        bool: True if valid email
    """
    if not value:
        return True
    
    # Simple email validation
    if '@' not in value or '.' not in value:
        raise ValueError("Must be a valid email address")
    
    return True


def hex_color_validator(value):
    """Validate hex color format.
    
    Args:
        value: Color value
        
    Returns:
        bool: True if valid hex color
    """
    if not value:
        return True
    
    if not (value.startswith('#') and len(value) == 7):
        raise ValueError("Must be a valid hex color (e.g., #FF0000)")
    
    try:
        int(value[1:], 16)
    except ValueError:
        raise ValueError("Must be a valid hex color")
    
    return True