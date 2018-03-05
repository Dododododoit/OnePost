import flask

app = flask.Flask(__name__) 
app.config.from_object('onepost.config')
app.config.from_envvar('ONEPOST_SETTINGS', silent=True)
import onepost.views  
import onepost.model  
