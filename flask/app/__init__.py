from flask import Flask, request, redirect
from app import views  # noqa

app = Flask(__name__, static_folder='static')
app.url_map.strict_slashes = False

app.jinja_options = app.jinja_options.copy()
app.jinja_options.update({
    'trim_blocks': True,
    'lstrip_blocks': True
})

app.config['DEBUG'] = True
app.config['SECRET_KEY'] = \
    '222a79f58a0cf4012d0862a167646183395f28b4fbfdb9e4809e0da53d1e12df'

app.config['JSON_AS_ASCII'] = False

@app.before_request
def remove_trailing_slash():
   # Check if the path ends with a slash but is not the root "/"
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1], code=308)

