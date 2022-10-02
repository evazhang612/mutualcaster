from flask import Flask, jsonify,request, Response, render_template
from flask_restful import Resource
from flask_cors import CORS 
import requests
import pandas as pd
import json
from flask import render_template_string

app = Flask(__name__)

# terrible style done in like 15 mins please excuse this
# todo: comments and like everything else beyond

def get_followers(farcaster_address):
	url = "https://api.farcaster.xyz/indexer/followers/"
	response = requests.get(url+farcaster_address)
	response = response.json()
	return pd.json_normalize(response)

def get_following(farcaster_address):
	url = "https://api.farcaster.xyz/indexer/following/"
	response = requests.get(url+farcaster_address)
	response=response.json()
	return pd.json_normalize(response)

@app.route('/',methods=("POST", "GET"))
def hello():
	try:
		return {'data': "Up!"}
	except:
		return {'data': 'An Error Occurred during fetching Api'}

def path_to_image_html(path):
    return '<img src="'+ path + '" width="60" >'

@app.route('/mutuals/<user1>/<user2>')
def mutuals(user1, user2):
		# return followers of user1 followed by user2
	df1 = get_followers(user1)
	print(user2)
	df2 = get_following(user2)
	print(df1)
	print(df2)
	moots = list(set(df1.username).intersection(set(df2.username)))
	resultsdf = df1[df1['username'].isin(moots)]
	resultsdf['image'] = [path_to_image_html(i) for i in resultsdf['avatar.url']] 
	resultsdf = resultsdf[['username', 'displayName','image']]
	print(resultsdf.to_html())
	return render_template('result.html',  
				tables=resultsdf.to_html(render_links=True,escape=False,index=False))

@app.route('/intros/<user1>/<user2>')
def intros(user1,user2):
	# return followers of user1 followed by user2
	df1 = get_following(user1)
	df2 = get_followers(user2)
	moots = set(df1.username).intersection(set(df2.username))
	resultsdf = df1[df1['username'].isin(moots)]
	resultsdf['image'] = [path_to_image_html(i) for i in resultsdf['avatar.url']] 
	resultsdf = resultsdf[['username', 'displayName','image']]
	return render_template('result.html',  
				tables=resultsdf.to_html(render_links=True,escape=False,index=False)) 

@app.route('/commonfollowing/<user1>/<user2>')
def get(user1,user2):
	# return followers of user1 followed by user2
	df1 = get_following(user1)
	df2 = get_following(user2)
	moots = set(df1.username).intersection(set(df2.username))
	resultsdf = df1[df1['username'].isin(moots)]
	resultsdf['image'] = [path_to_image_html(i) for i in resultsdf['avatar.url']] 
	resultsdf = resultsdf[['username', 'displayName','image']]
	return render_template('result.html',  
				tables=resultsdf.to_html(render_links=True,escape=False,index=False))

if __name__ == '__main__':
	app.run(debug=True, use_debugger=False, use_reloader=False,ssl_context='adhoc')
