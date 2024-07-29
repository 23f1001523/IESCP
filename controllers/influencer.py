from datetime import datetime
from flask import Flask, render_template, request, url_for, session, flash, json
from werkzeug.utils import redirect

from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest, Negotiation
from flask import current_app as app
from controllers.usermanager import *
from functools import wraps

fatalerror = "Error Occured. Please contact Administrator"


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
    influencer = Influencer.query.filter_by(
        influencer_id=influencer_id).first()
    if influencer:
      flash('Influencer already registered')
    else:
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
@login_required_influencer
def influencerdashboard():
  id = session['user_id']
  adrequests = AdRequest.query.filter_by(influencer_id=id).all()
  return render_template('/influencer/influencer_dashboard_display.html',
                         adrequests=adrequests)


@app.route('/influencer/adrequest/negotiation/<id>', methods=['GET', 'POST'])
@login_required_influencer
def negotiation():
  if request.method == 'POST':
    adrequest_id = request.form.get('adrequest_id')
    negotiation = request.form.get('negotiation')
    adrequest = AdRequest.query.filter_by(adrequest_id=adrequest_id).first()
    adrequest.negotiation = negotiation
    db.session.commit()


#INFLUENCER PROFILE
@app.route('/influencer/profile', methods=['GET', 'POST'])
@login_required_influencer
def influencer_profile():
  user_id = session['user_id']
  if request.method == 'POST':
    try:
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
    except:
      flash(fatalerror)
  influencer = Influencer.query.filter_by(influencer_id=user_id).first()
  return render_template('/influencer/influencer_profile.html',
                         influencer=influencer)


#INFLUENCER CHANGE CATEGORY
@app.route('/influencer/change/category', methods=['GET', 'POST'])
@login_required_influencer
def influencer_change_category():
  if request.method == 'POST':
    category = request.form.get('category')
    influencer = Influencer.query.filter_by(
        influencer_id=session['user_id']).first()
    if influencer:
      influencer.category = category
      db.session.commit()
      flash("Category Successfully Updated")
    else:
      flash("Influencer ID not registered")
    influencer = Influencer.query.filter_by(
        influencer_id=session['user_id']).first()
    return redirect(url_for('influencer_profile'))


#INFLUENCER CHANGE CATEGORY
@app.route('/influencer/change/niche', methods=['GET', 'POST'])
@login_required_influencer
def influencer_change_niche():
  if request.method == 'POST':
    category = request.form.get('niche')
    influencer = Influencer.query.filter_by(
        influencer_id=session['user_id']).first()
    if influencer:
      influencer.niche = niche
      db.session.commit()
      flash("Niche Successfully Updated")
    else:
      flash("Influencer ID not registered")
    influencer = Influencer.query.filter_by(
        influencer_id=session['user_id']).first()
    return redirect(url_for('influencer_profile'))


    #INFLUENCER CHANGE CATEGORY
@app.route('/influencer/change/reach', methods=['GET', 'POST'])
@login_required_influencer
def influencer_change_reach():
  if request.method == 'POST':
    category = request.form.get('reach')
    influencer = Influencer.query.filter_by(
        influencer_id=session['user_id']).first()
    if influencer:
      influencer.reach = reach
      db.session.commit()
      flash("Reach Successfully Updated")
    else:
      flash("Influencer ID not registered")
    influencer = Influencer.query.filter_by(
        influencer_id=session['user_id']).first()
    return redirect(url_for('influencer_profile'))


#INFLUENCER SIDEBAR PRIVATE ADREQUESTS STATUS
@app.route('/private/adrequests/status')
def private_adrequests_status():
  influencer_id = session['user_id']
  negotiations = Negotiation.query.filter_by(influencer_id=influencer_id).all()
  return render_template('/influencer/private_adrequest_status.html',
                         negotiations=negotiations)


# INFLUENCER SIDEBAR  PUBLIC ADREQUESTS STATUS
@app.route('/public/adrequests/status')
def public_adrequests_status():
  influencer_id = session['user_id']
  negotiations = Negotiation.query.filter_by(influencer_id=influencer_id).all()
  return render_template('/influencer/public_adrequest_status.html',
                         negotiations=negotiations)


#INFLUENCER FIND
@app.route('/influencer/find')
@login_required_influencer
def influncer_find():
  return render_template('/influencer/influencer_find.html')


#PUBLIC ADREQUEST FIND BY CAMPAIGN NAME ON INFLUENCER FIND
@app.route('/influencer/show/<id>', methods=['GET', 'POST'])
@login_required_influencer
def show(id):
  if request.method == 'POST':
    negotiation = request.form.get('negotiation')
    influencer_id = session['user_id']
    adrequest_id = id
    negotiations = Negotiation.query.filter_by(
        influencer_id=influencer_id, adrequest_id=adrequest_id).first()
    if negotiations:
      negotiations.negotiation = negotiation
      db.session.commit()
      flash('Successfully updated')
      return redirect(url_for('public_adrequests_status'))
    else:

      negotiations = Negotiation(negotiation=negotiation,
                                 influencer_id=influencer_id,
                                 adrequest_id=adrequest_id)

      db.session.add(negotiations)
      db.session.commit()
      flash("successfully entered in database")
      # return render_template('/sponsor/adrequest_negotiation.html',
      #                        negotiations=negotiations)
  return redirect(url_for('influencerdashboard'))


# CAMPAIGN SEARCH OPTION ON INFLUENCER FIND
@app.route("/influencer/campaign/search", methods=['GET', 'POST'])
@login_required_influencer
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
@login_required_influencer
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
    elif adrequest_search_type == 'message':
      adrequests = AdRequest.query.filter(
          AdRequest.message.like("%" + adrequest_search + "%")).all()
      if adrequests:
        return render_template('/influencer/influencer_find.html',
                               adrequests=adrequests)
      else:
        flash('No adrequests found')
    elif adrequest_search_type == 'requirements':
      adrequests = AdRequest.query.filter(
          AdRequest.requirements.like("%" + adrequest_search + "%")).all()
      if adrequests:
        return render_template('/influencer/influencer_find.html',
                               adrequests=adrequests)
      else:
        flash('No adrequests found')
  return render_template('/influencer/influencer_find.html')


#INFLUENCER STATS
@app.route('/influencer/stats')
@login_required_influencer
def influencer_stats():
  return render_template('/influencer/influencer_stats.html')


#INFLUENCER CAMPAIGN PROGRESS CHART ON INFLUENCER STATS
@app.route('/influencer/campaign/progress/chart')
@login_required_influencer
def inluencercampaignprogresschart():
  campaigns = Campaign.query.all()
  data = []
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


#INFLUENCER BUDGET PROGRESS CHART
@app.route('/influencer/adrequests/budget/chart')
@login_required_influencer
def campaign_budget_chart():
  influencer_id = session['user_id']
  adrequests = AdRequest.query.filter_by(influencer_id=influencer_id,
                                         status='ACCEPTED').all()
  data = []
  for adrequest in adrequests:
    dict = {}
    dict = {"name": adrequest.adrequest_id, "budget": adrequest.payment_amount}
    data.append(dict)
  return data
