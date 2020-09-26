from flask import Flask
import requests
app=Flask(__name__)

@app.route("/")
def index():
	return "Hello World"