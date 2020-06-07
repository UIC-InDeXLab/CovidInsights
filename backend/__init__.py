from flask import Flask

app = Flask(__name__)
#todo: remove this on production
app.debug = True

import backend.backend
import backend.error_handlers
import backend.processor


