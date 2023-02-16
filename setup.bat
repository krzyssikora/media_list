@REM set FLASK_ENV=development
set FLASK_DEBUG=1
set TEMPLATES_AUTO_RELOAD=1
set FLASK_APP=media_list
pip install -e .
flask run