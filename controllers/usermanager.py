from flask import Flask,flash,redirect,url_for,session
from functools import wraps

def login_required(func):
  @wraps(func)
  def wrapper(*args, **kwargs):
    if session.get('loggedin') is None:
      flash('You need to login first')
      return redirect(url_for('login'))
    return func(*args, **kwargs) 
  return wrapper

def userlogin(user,user_type):
  session['loggedin']=True
  session['user_type']=user_type
  if user_type=='admin':
    session['user_id']=user.admin_id
    session['user_name']=user.admin_name
  elif user_type=='sponsor':
    session['user_id']=user.sponsor_id
    session['user_name']=user.sponsor_name
  elif user_type=='influencer':
    session['user_id']=user.influencer_id
    session['user_name']=user.influencer_name

def userlogout():
  session.pop('loggedin',None)
  session.pop('user_id',None)
  session.pop('user_name',None)
  session.pop('user_type',None)
  return redirect(url_for('login'))

