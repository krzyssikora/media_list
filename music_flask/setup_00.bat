export FLASK_DEBUG=1 
export TEMPLATES_AUTO_RELOAD=1
export FLASK_APP=music_flask
pip install -e .
flask run --host=0.0.0.0 --port=80