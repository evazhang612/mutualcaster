from flask import Flask, jsonify,request, Response, render_template, redirect, url_for
from flask_restful import Resource
from flask_cors import CORS 
import requests
import pandas as pd
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import json
from flask import render_template_string

app = Flask(__name__)


app.config['SECRET_KEY'] = 'vfapafwo68'
Bootstrap(app)

OPTIONS = ['mutuals','intros','commonfollowing',\
			 'aremutuals', 'isfollowing', 'peopletofollow',
			 'stats']

class MutualForm(FlaskForm):
    name1 = StringField('User 1?', validators=[DataRequired()])
    name2 = StringField('User 2?', validators=[DataRequired()])
    option = SelectField(label='Option', 
    			choices = OPTIONS, 
    			validators = [DataRequired()]) 
    submit = SubmitField('Submit')

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

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/',methods=("GET","POST"))
def hello():
	form = MutualForm()
	if form.validate_on_submit():
		return redirect( url_for(form.option.data, user1=form.name1.data, user2=form.name2.data) )
	return render_template('index.html', form =form)

def username_to_addy(name):
	name = name.lower()
	return requests.get("https://searchcaster.xyz/api/profiles?username="+name)

def path_to_image_html(path):
    return '<img src="'+ path + '" width="75" >'

@app.route('/isfollowing/<user1>/<user2>')
def isfollowing(user1, user2):
	user1name = username_to_addy(user1).json()[0]['body']['address']
	user2name = username_to_addy(user2).json()[0]['body']['address']
	df1 = get_following(user1name)
	isfollowing = user2 in list(df1.username)
	if isfollowing: 
		result = "yay!"
	else:
		result = "nay!"
	return render_template('yayornay.html', result=result)

@app.route('/aremutuals/<user1>/<user2>')
def aremutuals(user1, user2):
	user1name = username_to_addy(user1).json()[0]['body']['address']
	user2name = username_to_addy(user2).json()[0]['body']['address']
	df1 = get_following(user1name)
	df2 = get_following(user2name)
	is1following = user2 in list(df1.username)
	is2following = user1 in list(df2.username)
	if is1following and is2following: 
		result = "yay!"
	else:
		result = "nay!"
	return render_template('yayornay.html', result=result)

@app.route('/mutuals/<user1>/<user2>')
def mutuals(user1, user2):
		# return followers of user1 followed by user2
	user1name = username_to_addy(user1).json()[0]['body']['address']
	user2name = username_to_addy(user2).json()[0]['body']['address']
	df1 = get_followers(user1name)
	print(user2)
	df2 = get_following(user2name)
	print(df1)
	print(df2)
	moots = list(set(df1.username).intersection(set(df2.username)))
	resultsdf = df1[df1['username'].isin(moots)]
	resultsdf['image'] = [path_to_image_html(i) for i in resultsdf['avatar.url']] 
	resultsdf = resultsdf[['username', 'displayName','image']]
	print(resultsdf.to_html())
	return render_template('result.html',  
				tables=resultsdf.to_html(justify= 'justify-all', col_space='75px',
					render_links=True,escape=False,index=False,
					classes=["table-bordered"]),
				nmutuals = resultsdf.shape[0]) 

@app.route('/peopletofollow/<user1>/<user2>')
def peopletofollow(user1, user2):
		# return followers of user1 followed by user2
	user1name = username_to_addy(user1).json()[0]['body']['address']
	user2name = username_to_addy(user2).json()[0]['body']['address']
	df1 = get_followers(user1name)
	df2 = get_following(user2name)
	moots = list(set(df1.username) - set(df2.username))
	resultsdf = df1[df1['username'].isin(moots) & df1['username'] != user2]
	print(resultsdf)
	if resultsdf.shape[0] == 0:
		return render_template('yayornay.html', result = "you followed everyone")

	resultsdf['image'] = [path_to_image_html(i) if i is not None else '' \
										for i in resultsdf['avatar.url'] ] 
	resultsdf = resultsdf[['username', 'displayName','image']]
	print(resultsdf.to_html())
	return render_template('result.html',  
				tables=resultsdf.to_html(justify= 'justify-all', col_space='75px',
					render_links=True,escape=False,index=False,
					classes=["table-bordered"]),
				nmutuals = resultsdf.shape[0]) 

@app.route('/intros/<user1>/<user2>')
def intros(user1,user2):
	# return followers of user1 followed by user2
	user1name = username_to_addy(user1).json()[0]['body']['address']
	user2name = username_to_addy(user2).json()[0]['body']['address']
	df1 = get_following(user1name)
	df2 = get_followers(user2name)
	moots = set(df1.username).intersection(set(df2.username))
	resultsdf = df1[df1['username'].isin(moots)]
	resultsdf['image'] = [path_to_image_html(i) for i in resultsdf['avatar.url']] 
	resultsdf = resultsdf[['username', 'displayName','image']]
	return render_template('result.html',  
				tables=resultsdf.to_html(
					justify= 'justify-all', col_space='75px',
					render_links=True,escape=False,index=False,
					classes=["table-bordered"]),
				nmutuals = resultsdf.shape[0]) 

@app.route('/commonfollowing/<user1>/<user2>')
def commonfollowing(user1,user2):
	# return followers of user1 followed by user2
	user1name = username_to_addy(user1).json()[0]['body']['address']
	user2name = username_to_addy(user2).json()[0]['body']['address']
	df1 = get_following(user1name)
	df2 = get_following(user2name)
	moots = set(df1.username).intersection(set(df2.username))
	resultsdf = df1[df1['username'].isin(moots)]
	resultsdf['image'] = [path_to_image_html(i) for i in resultsdf['avatar.url']] 
	resultsdf = resultsdf[['username', 'displayName','image']]
	return render_template('result.html',  
				tables=resultsdf.to_html(
					justify= 'justify-all', col_space='75px',
					render_links=True,escape=False,index=False,
					classes=["table-bordered"]),
				nmutuals = resultsdf.shape[0])

if __name__ == '__main__':
	app.run(debug=True, use_debugger=False, use_reloader=False,ssl_context='adhoc')
