from flask import Flask
from media_list.config import _logger

app = Flask(__name__)

import media_list.views
