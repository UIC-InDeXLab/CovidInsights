# -*- coding: utf-8 -*-

from flask import Flask

app = Flask(__name__)
#todo: remove this on production
app.debug = True

# import backend.backend
import backend.error_handlers
import backend.processor

if __name__ == '__main__':
    app.run()
