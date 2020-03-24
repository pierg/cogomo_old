from werkzeug.exceptions import HTTPException, NotFound, abort
from flask import render_template
from web import app

# App main route + generic routing
@app.route('/', defaults={'path': 'index.html'})
@app.route('/<path>')
def index(path):
    try:
        return render_template('layouts/default.html',
                               content=render_template('pages/' + path))
    except:
        abort(404)
