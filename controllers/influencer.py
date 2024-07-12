from datetime import datetime
from flask import Flask, render_template, request, url_for, session, flash
from werkzeug.utils import redirect

from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest
from flask import current_app as app
from controllers.usermanager import userlogin, login_required, userlogout


#INFLUENCER REGISTER
@app.route('/influencer/register', methods=['GET', 'POST'])
def influencers():
  if request.method == 'POST':
    influencer_name = request.form['influencer_name']
    influencer_id = request.form['influencer_id']
    influencer_password = request.form['influencer_password']
    category = request.form['category']
    niche = request.form['niche']
    reach = request.form['reach']
    status = 'ACTIVE'
    new_influencer = Influencer(influencer_name=influencer_name,
                                influencer_id=influencer_id,
                                influencer_password=influencer_password,
                                category=category,
                                niche=niche,
                                reach=reach,
                                status=status)
    db.session.add(new_influencer)
    db.session.commit()
    flash("Successfully Registerd as Influencer.Please Login now.")
    return render_template('login.html')
  return render_template('register.html')


#INFLUENCER LOGIN
@app.route('/influencer/login', methods=['GET', 'POST'])
def influencer_login():
  if request.method == 'POST':
    influencer_id = request.form.get('influencer_id')
    influencer_password = request.form.get('influencer_password')
    if influencer_id == '' or influencer_password == '':
      flash("Please enter all the fields")
      return render_template('login.html')
    influencer = Influencer.query.filter_by(
        influencer_id=influencer_id).first()
    if influencer:
      if influencer.status == 'ACTIVE':
        if influencer.influencer_password == influencer_password:
          userlogin(influencer, "influencer")
          return redirect(url_for('influencerdashboard'))

        else:
          flash("Password is wrong")
          return render_template('login.html')
      else:
        flash("You are not allowed to login")
        return render_template('login.html')
    else:
      flash("User ID not registered")
      return render_template('login.html')
  return render_template('login.html')


#INFLUENCER DASHBOARD
@app.route('/influencer/dashboard')
def influencerdashboard():
  id=session['user_id']
  adrequests=AdRequest.query.filter_by(influencer_id=id).all()
  return render_template('/influencer/influencer_dashboard_display.html',adrequests=adrequests)


@app.route('/influencer/adrequest/negotiation/<id>',methods=['GET', 'POST'])
def negotiation():
  if request.method == 'POST':
    adrequest_id = request.form.get('adrequest_id')
    negotiation = request.form.get('negotiation')
    adrequest = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    adrequest.negotiation = negotiation  
    db.session.commit()
    
    

#INFLUENCER PROFILE
@app.route('/influencer/profile', methods=['GET', 'POST'])
def influencer_profile():
  user_id = session['user_id']
  if request.method == 'POST':
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    influencer_id = request.form.get('influencer_id')
    influencer_password = request.form.get('influencer_password')
    influencer = Influencer.query.filter_by(
        influencer_id=influencer_id).first()
    if influencer:
      if influencer.influencer_password == influencer_password:
        if new_password == confirm_new_password:
          influencer.influencer_password = new_password
          db.session.commit()
          flash("Password Successfully Updated")
          return render_template('/influencer/influencer_profile.html',
                                 user_id=user_id)
        else:
          flash("Your Passwords do not match")
          return render_template('/influencer/influencer_profile.html',
                                 user_id=user_id)
      else:
        flash("You are not allowed to change password")
        return render_template('/influencer/influencer_profile.html',
                               user_id=user_id)
    else:
      flash("User ID not registered")
      return render_template('/influencer/influencer_profile.html',
                             user_id=user_id)
  return render_template('/influencer/influencer_profile.html',
                         user_id=user_id)


#INFLUENCER FIND
@app.route('/influencer/find')
def influncer_find():
  return render_template('/influencer/influencer_find.html')


# CAMPAIGN SEARCH OPTION ON INFLUENCER FIND
@app.route("/influencer/campaign/search", methods=['GET', 'POST'])
def influencer_campaign_search():
  if request.method == 'POST':
    campaign_search_type = request.form.get('campaign_search_type')
    campaign_search = request.form.get('campaign_search')

    if campaign_search_type == 'name':
      campaigns = Campaign.query.filter_by(name=campaign_search,
                                           visibility='Public').all()
      if campaigns:
        flash("search complete")
        return render_template('/influencer/influencer_find.html',
                               campaigns=campaigns)
      else:
        flash("You can not search for a Private Campaign")
        return render_template('/influencer/influencer_find.html')
    elif campaign_search_type == 'budget':
      campaigns = Campaign.query.filter_by(budget=campaign_search,
                                           visibility='Public').all()

      if campaigns:
        flash("search complete")
        return render_template('/influencer/influencer_find.html',
                               campaigns=campaigns)
      else:
        flash("You can not search for a Private Campaign")
        return render_template('/influencer/influencer_find.html')

    elif campaign_search_type == 'start_date':
      campaigns = Campaign.query.filter_by(start_date=campaign_search,
                                           visibility='Public').all()
      if campaigns:
        flash("search complete")
        return render_template('/influencer/influencer_find.html',
                               campaigns=campaigns)
      else:
        flash("You can not search for a Private Campaign")
        return render_template('/influencer/influencer_find.html')

    elif campaign_search_type == 'end_date':
      campaigns = Campaign.query.filter_by(end_date=campaign_search,
                                           visibility='Public').all()
      if campaigns:
        flash("search complete")
        return render_template('/influencer/influencer_find.html',
                               campaigns=campaigns)
      else:
        flash("You can not search for a Private Campaign")
        return render_template('/influencer/influencer_find.html')

  return render_template('/influencer/influencer_find.html')


# ADREQUEST SEARCH OPTION ON INFLUENCER FIND
@app.route("/influencer/adrequest/search", methods=['GET', 'POST'])
def influencer_adrequest_search():

  if request.method == 'POST':
    adrequest_search_type = request.form.get('adrequest_search_type')
    adrequest_search = request.form.get('adrequest_search')

    if adrequest_search_type == 'payment_amount':

      adds = []
      adrequests = AdRequest.query.filter_by(
          payment_amount=adrequest_search).all()
      for ads in adrequests:
        camp = Campaign.query.filter_by(campaign_id=ads.campaign_id).first()
        if camp.visibility == 'Public':
          adds.append(ads)
      return render_template('/influencer/influencer_find.html',
                             adrequests=adds)
  return render_template('/influencer/influencer_find.html')


#INFLUENCER STATS
@app.route('/influencer/stats')
def influencer_stats():
  return render_template('/influencer/influencer_stats.html')


#INFLUENCER CAMPAIGN PROGRESS CHART ON INFLUENCER STATS
@app.route('/influencer/campaign/progress/chart')
def inluencercampaignprogresschart():
  campaigns = Campaign.query.all()
  data=[]
  for campaign in campaigns:
    dict = {}
    start_date = campaign.start_date.split('-')
    end_date = campaign.end_date.split('-')
    starting_date = datetime(int(start_date[0]), int(start_date[1]),
                             int(start_date[2]))
    ending_date = datetime(int(end_date[0]), int(end_date[1]),
                           int(end_date[2]))
    campaign_duration = (ending_date - starting_date).days
   
    present_date = datetime.now()
    campaign_progress = (present_date - starting_date).days
    present_date=str(present_date)
    current_date = present_date.split('-')
   
    
    if int(current_date[0]) < int(start_date[0]):
      percentage_progress = 0
    elif int(current_date[0]) > int(end_date[0]):
      percentage_progress = campaign_duration
    else:
      percentage_progress = (campaign_progress / campaign_duration) * 100
    
    dict = {
        "id": campaign.campaign_id,
        "name": campaign.name,
        "progress": percentage_progress
    }
    data.append(dict)
  return data




#INFLUENCER LOGOUT
@app.route('/influencer/logout')
def influencer_logout():
  return render_template('/login.html')
