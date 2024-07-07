from flask_login import current_user
from flask import render_template, flash, current_app, request, redirect, url_for
from functools import wraps

from flask_login import current_user
from flask import render_template, flash, current_app
from functools import wraps

# Code Provided by Bono
def role_required(roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if current_user and current_user.role in roles:
                pass
            else:
                flash('You do not have permission to access this function.', 'error')
                # Return the user to the previous url after trying to do something that
                # they are unauthorized to do
                return redirect(request.referrer)
            if callable(getattr(current_app, "ensure_sync", None)):
                return current_app.ensure_sync(func)(*args, **kwargs)
            return func(*args, *kwargs)
        return wrapper
    return decorator