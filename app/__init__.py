from flask import Flask, request, redirect

app = Flask(__name__, static_folder='static')
app.url_map.strict_slashes = False

app.jinja_options = app.jinja_options.copy()
app.jinja_options.update({
    'trim_blocks': True,
    'lstrip_blocks': True
})

app.config['SECRET_KEY'] = \
    '179810bb56e3c78e5aa5d426aecf3e98432bbe3fd88cf0ac'

app.config['DEBUG'] = True

@app.before_request
def remove_trailing_slash():
   # Check if the path ends with a slash but is not the root "/"
    if request.path != '/' and request.path.endswith('/'):
        return redirect(request.path[:-1], code=308)

from app import views  # noqa
