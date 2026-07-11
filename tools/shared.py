import ast

# Global color map for console and logs — reuse across the project
MSG_COLORS = {
    'info': '#2374AB',    # Rich Cerulean
    'error': '#D90429',   # Flag Red
    'success': '#0CCA4A', # Jade Green
    'message': '#9CFFD9', # Aquamarine
    'default': '#EDF2F4'  # Platinum
}


def configure_text_tags(text_widget, colors: dict):
    """Configure text tags (colors) on a Text/CTkTextbox widget.

    This allows reusing the same tag names/colors across multiple widgets.
    """
    for name, color in colors.items():
        # CTkTextbox uses tag_config
        try:
            text_widget.tag_config(name, foreground=color)
        except Exception:
            # Fallback: ignore if the widget doesn't support tags
            pass


def safe_echo_eval(expression: str):
    expression = expression.strip()
    if not expression:
        return ''

    # First try to evaluate quoted string literals like "Olá, isso é uma mensagem"
    try:
        value = ast.literal_eval(expression)
        return value
    except Exception:
        pass

    # Then allow safe arithmetic expressions only
    node = ast.parse(expression, mode='eval')
    for sub in ast.walk(node):
        if not isinstance(sub, (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
                                ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod,
                                ast.Pow, ast.FloorDiv, ast.USub, ast.UAdd,
                                ast.Tuple, ast.List, ast.Dict, ast.Set,
                                ast.Compare, ast.Eq, ast.NotEq, ast.Lt, ast.LtE, ast.Gt,
                                ast.GtE, ast.Subscript, ast.Slice)):
            raise ValueError(f'Unsupported expression: {sub.__class__.__name__}')
        if isinstance(sub, ast.Name):
            raise ValueError('Name expressions are not allowed')
        if isinstance(sub, ast.Call):
            raise ValueError('Function calls are not allowed')

    return eval(compile(node, '<string>', 'eval'), {'__builtins__': None}, {})
