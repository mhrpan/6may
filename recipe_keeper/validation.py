"""
Validation utilities for the Recipe Keeper application.
Provides functions to validate user inputs for all API endpoints.
"""
import re
from flask import jsonify
from functools import wraps
from werkzeug.datastructures import ImmutableDict

class ValidationError(Exception):
    """Exception raised for validation errors."""
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        
    def to_response(self):
        """Convert the error to a Flask response."""
        return jsonify({
            'status': 'error',
            'message': self.message
        }), self.status_code

def validate_uuid(value, field_name="ID"):
    """Validate that a string is a valid UUID."""
    if not value:
        raise ValidationError(f"{field_name} is required")
    
    # UUID pattern validation
    uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    if not re.match(uuid_pattern, value, re.IGNORECASE):
        raise ValidationError(f"Invalid {field_name} format")
    
    return value

def validate_string(value, field_name, required=True, min_length=1, max_length=None):
    """Validate a string field."""
    if required and not value:
        raise ValidationError(f"{field_name} is required")
    
    if value:
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name} must be at least {min_length} characters")
        
        if max_length and len(value) > max_length:
            raise ValidationError(f"{field_name} cannot exceed {max_length} characters")
    
    return value

def validate_int(value, field_name, required=True, min_value=None, max_value=None):
    """Validate an integer field."""
    if required and value is None:
        raise ValidationError(f"{field_name} is required")
    
    if value is not None:
        try:
            value = int(value)
        except (ValueError, TypeError):
            raise ValidationError(f"{field_name} must be a valid integer")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} cannot exceed {max_value}")
    
    return value

def validate_email(value, field_name="Email", required=True):
    """Validate an email address."""
    if required and not value:
        raise ValidationError(f"{field_name} is required")
    
    if value:
        # Simple email pattern validation
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, value):
            raise ValidationError(f"Invalid {field_name} format")
    
    return value

def validate_array(value, field_name, required=True, min_items=0, max_items=None, item_validator=None):
    """Validate an array field."""
    if required and not value:
        raise ValidationError(f"{field_name} is required")
    
    if value:
        if not isinstance(value, list):
            raise ValidationError(f"{field_name} must be an array")
        
        if len(value) < min_items:
            raise ValidationError(f"{field_name} must have at least {min_items} items")
        
        if max_items is not None and len(value) > max_items:
            raise ValidationError(f"{field_name} cannot have more than {max_items} items")
        
        # Validate each item in the array if an item validator is provided
        if item_validator:
            validated_items = []
            for i, item in enumerate(value):
                try:
                    validated_item = item_validator(item, f"{field_name}[{i}]")
                    validated_items.append(validated_item)
                except ValidationError as e:
                    raise ValidationError(f"Invalid item in {field_name}: {e.message}")
            return validated_items
    
    return value

def validate_url(value, field_name="URL", required=False):
    """Validate a URL."""
    if required and not value:
        raise ValidationError(f"{field_name} is required")
    
    if value:
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        # URL pattern validation (basic)
        url_pattern = r'^(https?://)?([a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?$'
        if not re.match(url_pattern, value):
            raise ValidationError(f"Invalid {field_name} format")
    
    return value

def validate_phone(value, field_name="Phone", required=False):
    """Validate a phone number."""
    if required and not value:
        raise ValidationError(f"{field_name} is required")
    
    if value:
        if not isinstance(value, str):
            raise ValidationError(f"{field_name} must be a string")
        
        # Allow +, digits, spaces, dashes, and parentheses
        phone_pattern = r'^\+?[\d\s\(\)-]{6,20}$'
        if not re.match(phone_pattern, value):
            raise ValidationError(f"Invalid {field_name} format")
    
    return value

# Specific validators for recipe-related data

def validate_recipe_input(data):
    """Validate recipe input data."""
    if not isinstance(data, dict) and not isinstance(data, ImmutableDict):
        raise ValidationError("Invalid recipe data format")
    
    # Validate required fields
    name = validate_string(data.get('name'), "Recipe name", required=True, max_length=255)
    story = validate_string(data.get('story'), "Description", required=False, max_length=5000)
    servings = validate_int(data.get('servings'), "Servings", required=False, min_value=1, max_value=100)
    image_url = validate_url(data.get('image'), "Image URL", required=False)
    
    # Validate ingredients array
    ingredients = validate_array(
        data.get('ingredients'), 
        "Ingredients", 
        required=True,
        min_items=1,
        item_validator=validate_ingredient
    )
    
    # Validate steps array
    steps = validate_array(
        data.get('steps'), 
        "Steps", 
        required=True,
        min_items=1,
        item_validator=validate_step
    )
    
    # Return validated data
    return {
        'name': name,
        'story': story,
        'servings': servings,
        'image': image_url,
        'ingredients': ingredients,
        'steps': steps
    }

def validate_ingredient(item, field_name):
    """Validate an ingredient item."""
    if not isinstance(item, dict) and not isinstance(item, ImmutableDict):
        raise ValidationError(f"{field_name} must be an object")
    
    name = validate_string(item.get('name'), f"{field_name} name", required=True, max_length=100)
    quantity = validate_string(item.get('quantity'), f"{field_name} quantity", required=False, max_length=100)
    brand = validate_string(item.get('brand'), f"{field_name} brand", required=False, max_length=100)
    
    return {
        'name': name,
        'quantity': quantity,
        'brand': brand
    }

def validate_step(item, field_name):
    """Validate a recipe step item."""
    if not isinstance(item, dict) and not isinstance(item, ImmutableDict):
        raise ValidationError(f"{field_name} must be an object")
    
    instruction = validate_string(item.get('instruction'), f"{field_name} instruction", required=True, max_length=5000)
    step_image = validate_url(item.get('stepImage'), f"{field_name} image", required=False)
    
    return {
        'instruction': instruction,
        'stepImage': step_image
    }

def validate_family_input(data):
    """Validate family creation input data."""
    if not isinstance(data, dict) and not isinstance(data, ImmutableDict):
        raise ValidationError("Invalid family data format")
    
    # Validate name field
    name = validate_string(data.get('name'), "Family name", required=True, max_length=100)
    
    return {
        'name': name
    }

def validate_family_member_input(data):
    """Validate family member input data."""
    if not isinstance(data, dict) and not isinstance(data, ImmutableDict):
        raise ValidationError("Invalid family member data format")
    
    # Validate required fields
    email = validate_email(data.get('email'), "Email", required=True)
    name = validate_string(data.get('name'), "Name", required=True, max_length=200)
    
    # Validate optional fields
    phone = validate_phone(data.get('phone'), "Phone number", required=False)
    relation = validate_string(data.get('relation'), "Relation", required=False, max_length=50)
    
    return {
        'email': email,
        'name': name,
        'phone': phone,
        'relation': relation
    }

# Create a validator for query parameters
def validate_recipe_query_params(data):
    """Validate recipe query parameters."""
    if not isinstance(data, dict) and not isinstance(data, ImmutableDict):
        raise ValidationError("Invalid query parameters format")
    
    # Validate optional query parameters
    validated = {}
    
    # Validate sort parameter
    if 'sort' in data:
        sort = validate_string(data.get('sort'), "Sort parameter", required=False)
        if sort and sort not in ['created_at', 'title', 'updated_at']:
            raise ValidationError("Sort parameter must be one of: created_at, title, updated_at")
        validated['sort'] = sort
    
    # Validate order parameter
    if 'order' in data:
        order = validate_string(data.get('order'), "Order parameter", required=False)
        if order and order not in ['asc', 'desc']:
            raise ValidationError("Order parameter must be either 'asc' or 'desc'")
        validated['order'] = order
    
    # Validate limit parameter
    if 'limit' in data:
        try:
            limit = int(data.get('limit', '10'))
            if limit < 1 or limit > 100:
                raise ValidationError("Limit must be between 1 and 100")
            validated['limit'] = limit
        except ValueError:
            raise ValidationError("Limit must be a valid integer")
    
    # Validate offset parameter for pagination
    if 'offset' in data:
        try:
            offset = int(data.get('offset', '0'))
            if offset < 0:
                raise ValidationError("Offset cannot be negative")
            validated['offset'] = offset
        except ValueError:
            raise ValidationError("Offset must be a valid integer")
    
    # Validate search parameter
    if 'search' in data:
        search = validate_string(data.get('search'), "Search parameter", required=False)
        if search and len(search) < 2:
            raise ValidationError("Search parameter must be at least 2 characters long")
        validated['search'] = search
    
    return validated

# Decorator for validating request data
def validate_request(validator_func):
    """Decorator to validate request data before processing."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                from flask import request
                
                # Get request data based on content type
                if request.is_json:
                    data = request.json
                elif request.method == 'GET':
                    data = request.args
                else:
                    data = request.form
                
                # Validate the data
                validated_data = validator_func(data)
                
                # Add validated data to kwargs
                kwargs['validated_data'] = validated_data
                
                return f(*args, **kwargs)
            
            except ValidationError as e:
                return e.to_response()
            
        return decorated_function
    return decorator