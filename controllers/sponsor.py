from flask import Flask, render_template, request, url_for, session, flash,jsonify
from werkzeug.utils import redirect
from datetime import datetime
from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest
from flask import current_app as app
from controllers.usermanager import userlogin, login_required, userlogout
from sqlalchemy import func


# SPONSOR REGISTER
@app.route('/sponsor/register', methods=['GET', 'POST'])
def sponsorregister():
  if request.method == 'POST':
    sponsor_name = request.form['sponsor_name']
    sponsor_id = request.form['sponsor_id']
    sponsor_password = request.form['sponsor_password']
    industry = request.form['industry']
    budget = request.form['budget']
    status = 'ACTIVE'
    sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
    if sponsor:
      flash("Sponsor ID already registered. Use diferrent ID.")
      return render_template('register.html')
    else:

      new_sponsor = Sponsor(sponsor_name=sponsor_name,
                            sponsor_id=sponsor_id,
                            sponsor_password=sponsor_password,
                            industry=industry,
                            budget=budget,
                            status=status)
      db.session.add(new_sponsor)
      db.session.commit()
      flash("Registered successfully ! Please login now.")
      return render_template('login.html')

  return render_template('register.html')


# SPONSOR LOGIN
@app.route('/sponsor/login', methods=['GET', 'POST'])
def sponsor_login():
  if request.method == 'POST':
    id = request.form.get('sponsor_id')
    password = request.form.get('sponsor_password')
    if id == '' or password == '':
      flash("Please enter all the fields")
      return render_template('login.html')
    sponsor = Sponsor.query.filter_by(sponsor_id=id).first()
    if sponsor:
      if sponsor.status == 'ACTIVE':
        if sponsor.sponsor_password == password:
          userlogin(sponsor, "sponsor")
          return redirect(url_for('sponsordashboard'))
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


# SPONSOR DASHBOARD
@app.route('/sponsor/dashboard')
def sponsordashboard():
  campaigns = Campaign.query.all()
  adrequests = AdRequest.query.all()
  user_name = session['user_name']
  return render_template('/sponsor/sponsor_dashboard.html',
                         campaigns=campaigns,
                         adrequests=adrequests,
                         user_name=user_name)


# SPONSOR PROFILE
@app.route('/sponsor/profile', methods=['GET', 'POST'])
def sponsor_profile():
  user_id = session['user_id']
  if request.method == 'POST':
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    sponsor_id = request.form.get('sponsor_id')
    sponsor_password = request.form.get('sponsor_password')
    sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
    if sponsor:
      if sponsor.sponsor_password == sponsor_password:
        if new_password == confirm_new_password:
          sponsor.sponsor_password = new_password
          db.session.commit()
          flash("Password Successfully Updated")
          return render_template('/sponsor/sponsor_profile.html',
                                 user_id=user_id)
        else:
          flash("Your Passwords do not match")
          return render_template('/sponsor/sponsor_profile.html',
                                 user_id=user_id)
      else:
        flash("You are not allowed to change password")
        return render_template('/sponsor/sponsor_profile.html',
                               user_id=user_id)
    else:
      flash("User ID not registered")
      return render_template('/sponsor/sponsor_profile.html')
  return render_template('/sponsor/sponsor_profile.html', user_id=user_id)


# SPONSOR CAMPAIGN SHOW
@app.route('/sponsor/campaign/show')
def show_campaign():
  user_id = session['user_id']
  campaigns = Campaign.query.filter_by(sponsor_id=user_id).all()
  adrequests = AdRequest.query.all()

  return render_template('/sponsor/campaign.html',
                         campaigns=campaigns,
                         adrequests=adrequests,
                         user_id=user_id)


# ADD CAMPAIGN BUTTON
@app.route('/sponsor/campaign', methods=['GET', 'POST'])
def campaign():
  if request.method == 'POST':
    name = request.form.get('campaign_name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    visibility = request.form.get('visibility')
    goals = request.form.get('goals')
    status = 'ACTIVE'
    sponsor_id = session['user_id']
    expiry = 'UNEXPIRED'
    campaign = Campaign(name=name,
                        description=description,
                        start_date=start_date,
                        end_date=end_date,
                        budget=budget,
                        visibility=visibility,
                        goals=goals,
                        status=status,
                        sponsor_id=sponsor_id,
                        expiry=expiry)
    db.session.add(campaign)
    db.session.commit()
    return redirect(url_for('sponsordashboard'))
  return render_template('/sponsor/campaign_form.html')


# VIEW BUTTON ON CAMPAIGN SHOW
@app.route('/sponsor/campaign/table')
def show_sponsor_details():
  campaigns = Campaign.query.all()
  return render_template('/sponsor/sponsor_campaign_table.html',
                         campaigns=campaigns)


# ADREQUEST BUTTON ON CAMPAIGN SHOW
@app.route('/sponsor/adrequest/<id>', methods=['GET', 'POST'])
def adrequest(id):
  if request.method == 'POST':
    message = request.form.get('message')
    requirements = request.form.get('requirements')
    payment_amount = request.form.get('payment_amount')
    status = 'PENDING'
    negotiation = request.form.get('negotiation')

    new_adrequest = AdRequest(message=message,
                              requirements=requirements,
                              payment_amount=payment_amount,
                              status=status,
                              campaign_id=id,
                              negotiation=negotiation)
    db.session.add(new_adrequest)
    db.session.commit()
    return redirect(url_for('sponsordashboard'))
  campaign = Campaign.query.filter_by(campaign_id=id).first()
  return render_template('/sponsor/adrequest.html', campaign=campaign)


# MODIFY BUTTON ON CAMAPIGN SHOW
@app.route('/sponsor/campaign/modify/<id>', methods=['GET', 'POST'])
def modify_campaign(id):
  campaigns = Campaign.query.filter_by(campaign_id=id).first()
  if request.method == 'POST':
    name = request.form.get('campaign_name')
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    visibility = request.form.get('visibility')
    goals = request.form.get('goals')
    status = 'ACTIVE'
    sponsor_id = session['user_id']
    expiry = 'UNEXPIRED'
    campaign = Campaign.query.filter_by(campaign_id=id).first()
    campaign.name = name
    campaign.description = description
    campaign.start_date = start_date
    campaign.end_date = end_date
    campaign.budget = budget
    campaign.visibility = visibility
    campaign.goals = goals
    campaign.status = status
    campaign.sponsor_id = sponsor_id
    campaign.expiry = expiry

    db.session.commit()
    return redirect(url_for('show_campaign'))
  return render_template('/sponsor/campaign_modify_form.html',
                         campaigns=campaigns)


# ADREQUEST EDIT BUTTON ON ADREQUEST TABLE
@app.route('/sponsor/adrequest/modify/<id>', methods=['GET', 'POST'])
def modify_adrequest(id):
  adrequest = AdRequest.query.filter_by(adrequest_id=id).first()
  if request.method == 'POST':
    adrequest_id = request.form.get('adrequest_id')
    message = request.form.get('message')
    requirements = request.form.get('requirements')
    payment_amount = request.form.get('payment_amount')
    negotiation = request.form.get('negotiation')
    adrequest.message = message
    adrequest.requirements = requirements
    adrequest.payment_amount = payment_amount

    db.session.commit()
    return redirect(url_for('show_campaign'))
  return render_template('/sponsor/adrequest_modify_form.html',
                         adrequests=adrequest)


# SPONSOR FIND
@app.route('/sponsor/find')
def find_sponsor():
  return render_template('/sponsor/sponsor_find.html')


# CAMPAIGN SEARCH OPTION ON SPONSOR FIND
@app.route("/sponsor/campaign/search", methods=['GET', 'POST'])
def sponsor_campaign_search():
  if request.method == 'POST':
    campaign_search_type = request.form.get('campaign_search_type')
    camapign_search = request.form.get('camapign_search')

    if campaign_search_type == 'name':
      campaigns = Campaign.query.filter_by(name=camapign_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html', campaigns=campaigns)
    elif campaign_search_type == 'budget':
      campaigns = Campaign.query.filter_by(budget=camapign_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html', campaigns=campaigns)
    elif campaign_search_type == 'visibility':
      campaigns = Campaign.query.filter_by(visibility=campaign_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html', campaigns=campaigns)
    elif campaign_search_type == 'start_date':
      campaigns = Campaign.query.filter_by(start_date=camapign_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html', campaigns=campaigns)
    elif campaign_search_type == 'end_date':
      campaigns = Campaign.query.filter_by(end_date=camapign_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html', campaigns=campaigns)
  return render_template('/sponsor/sponsor_find.html')


#INFLUENCER SEARCH OPTION ON SPONSOR FIND
@app.route("/sponsor/influencer/search", methods=['GET', 'POST'])
def sponsor_influencer_search():
  if request.method == 'POST':
    influencer_search_type = request.form.get('influencer_search_type')
    influencer_search = request.form.get('influencer_search')

    if influencer_search_type == 'name':
      influencers = Influencer.query.filter_by(
          influencer_name=influencer_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html',
                             influencers=influencers)
    elif influencer_search_type == 'category':
      influencers = Influencer.query.filter_by(
          category=influencer_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html',
                             influencers=influencers)
    elif influencer_search_type == 'niche':
      influencers = Influencer.query.filter_by(niche=influencer_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html',
                             influencers=influencers)
    elif influencer_search_type == 'reach':
      influencers = Influencer.query.filter_by(reach=influencer_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html',
                             influencers=influencers)
  return render_template('/sponsor/sponsor_find.html')


# ADREQUEST SEARCH OPTION ON SPONSOR FIND
@app.route("/sponsor/adrequest/search", methods=['GET', 'POST'])
def sponsor_adrequest_search():
  if request.method == 'POST':
    adrequest_search_type = request.form.get('adrequest_search_type')
    adrequest_search = request.form.get('adrequest_search')

    if adrequest_search_type == 'payment_amount':
      adrequests = AdRequest.query.filter_by(
          payment_amount=adrequest_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html',
                             adrequests=adrequests)
  return render_template('/sponsor/sponsor_find.html')


#SPONSOR STATS
@app.route('/sponsor/stats')
def sponsor_stats():
  return render_template('/sponsor/sponsor_stats.html')


#SPONSOR CAMPAIGN PROGRESS CHART ON SPONSOR STATS
@app.route('/sponsor/campaign/progress/chart')
def sponsorcampaignprogresschart():
  id = session['user_id']
  sponsors = Sponsor.query.filter_by(sponsor_id=id).first()
  validCampaigns = sponsors.campaigns
  data = []
  for campaign in validCampaigns:
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
    present_date = str(present_date)
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


@app.route('/sponsor/influencer/niche/chart')
def influencerNicheCount():
  data = []
  dict={}
  query = db.session.query(
      Influencer.niche,
      func.count(Influencer.niche).label('count')
  ).group_by(Influencer.niche)
  # query = Influencer.query(func.count(niche).label('count').group_by(
  #                           niche))
  for niche, count in query:
    dict = {
        'name': niche,
        'count': count
    }
    data.append(dict)
  # for i in query:
  #   dict['name']=i[0]
  #   dict['count']=i[1]
  #   data.append(dict)
  return jsonify(data)
  # data = [{'name': 'gym', 'count': 1}, {'name': 'beauty', 'count': 2}]
  # return data


#SPONSOR LOGOUT
@app.route('/sponsor/logout')
def sponsorlogout():
  return render_template('login.html')
