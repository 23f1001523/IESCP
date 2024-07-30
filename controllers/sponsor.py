from flask import Flask, render_template, request, url_for, session, flash, jsonify
from werkzeug.utils import redirect
from datetime import datetime
from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest, Negotiation
from flask import current_app as app
from controllers.usermanager import isActive, userlogin, login_required_sponsor
from sqlalchemy import func
from functools import wraps

fatalerror = "Error Occured. Please contact Administrator"


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
    sponsor = Sponsor.query.filter_by(sponsor_id=id).first()
    if sponsor:
      if sponsor.sponsor_password == password:
        userlogin(sponsor, "sponsor")
        return redirect(url_for('sponsordashboard'))
      else:
        flash("Password is wrong")
    else:
      flash("User ID not registered")
  return render_template('login.html')


# SPONSOR DASHBOARD
@app.route('/sponsor/dashboard')
@login_required_sponsor
def sponsordashboard():
  try:
    if isActive():
      campaigns = Campaign.query.all()
      adrequests = AdRequest.query.all()
      negotiations = Negotiation.query.all()
      user_name = session['user_name']
      return render_template('/sponsor/sponsor_main.html',
                             campaigns=campaigns,
                             adrequests=adrequests,
                             negotiations=negotiations,
                             user_name=user_name)
    else:
      return render_template('error.html')
  except:
    return render_template('error.html')


@app.route('/sponsor/profile')
@login_required_sponsor
def sponsorprofile():
  sponsor_id = session['user_id']
  sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
  return render_template('/sponsor/sponsor_profile.html', sponsor=sponsor)


# SPONSOR PROFILE
@app.route('/profile/change/password', methods=['GET', 'POST'])
@login_required_sponsor
def sponsor_profile():
  user_id = session['user_id']
  if request.method == 'POST':
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    sponsor_id = user_id
    sponsor_password = request.form.get('sponsor_password')
    sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
    if sponsor:
      if sponsor.sponsor_password == sponsor_password:
        if new_password == confirm_new_password:
          sponsor.sponsor_password = new_password
          db.session.commit()
          flash("Password Successfully Updated")
          return redirect(url_for('sponsorprofile'))
        else:
          flash("Confirm Passwords do not match")
          return redirect(url_for('sponsorprofile'))
      else:
        flash("Password entered is wrong")
        return redirect(url_for('sponsorprofile'))
    else:
      flash("User ID not registered")
      return redirect(url_for('sponsorprofile'))
  return redirect(url_for('sponsorprofile'))


@app.route('/profile/change/budget', methods=['GET', 'POST'])
@login_required_sponsor
def sponsor_profile_budget():
  sponsor_id = session['user_id']
  if request.method == 'POST':
    budget = request.form.get('budget')
    sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
    if sponsor:
      sponsor.budget = budget
      db.session.commit()
      flash("Budget Successfully Updated")
    else:
      flash("Sponsor ID not registered")
  sponsor = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
  return render_template('/sponsor/sponsor_profile.html', sponsor=sponsor)


# SPONSOR CAMPAIGN SHOW
@app.route('/sponsor/campaign/show')
@login_required_sponsor
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
@login_required_sponsor
def campaign():
  sponsor_id = session['user_id']
  sponsors = Sponsor.query.filter_by(sponsor_id=sponsor_id).first()
  campaigns = Campaign.query.filter_by(sponsor_id=sponsor_id).all()
  negotiations = Negotiation.query.all()
  total_budget = 0
  for campaign in campaigns:
    total_budget += campaign.budget
  if request.method == 'POST':
    name = request.form.get('campaign_name').title()
    description = request.form.get('description')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    budget = request.form.get('budget')
    visibility = request.form.get('visibility')
    goals = request.form.get('goals')
    status = 'ACTIVE'
    sponsor_id = session['user_id']
    expiry = 'UNEXPIRED'
    if (float(budget) + float(total_budget)) >= sponsors.budget:
      flash("Budget Exceeded")
      return redirect(url_for("campaign"))
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
    return redirect(url_for('show_campaign'))
  return render_template('/sponsor/campaign_form.html',
                         sponsors=sponsors,
                         total_budget=total_budget)


#DELETE CAMPAIGN BUTTON ON CAMPAIGN SHOW
@app.route('/sponsor/delete/campaign/<id>', methods=['GET', 'POST'])
@login_required_sponsor
def delete_campaign(id):
  campaign = Campaign.query.filter_by(campaign_id=id).first()
  for arequest in campaign.adrequests:
    if arequest.status == 'ACCEPTED':
      flash("Sorry,cannot delete the campaign.")
      break
  else:
    campaign.status = 'DELETED'
    for adrequest in campaign.adrequests:
      adrequest.status = 'DELETED'
    db.session.commit()
  return redirect(url_for('show_campaign'))


#DELETE ADREQUEST BUTTON ON ADREQUEST TABLE IN CAMPAIGN SHOW
@app.route('/sponsor/delete/adrequest/<id>')
@login_required_sponsor
def delete_adrequest(id):
  adrequest = AdRequest.query.filter_by(adrequest_id=id).first()
  if adrequest.status == 'ACCEPTED':
    flash("Sorry,cannot delete the adrequest.")
  else:
    adrequest.status = 'DELETED'
    flash('Adrequest deleted successfully.')
    db.session.commit()
  return redirect(url_for('show_campaign'))


# VIEW BUTTON ON CAMPAIGN SHOW
@app.route('/sponsor/campaign/table/<id>')
@login_required_sponsor
def show_sponsor_details(id):
  campaigns = Campaign.query.filter_by(campaign_id=id).all()
  return render_template('/sponsor/sponsor_campaign_table.html',
                         campaigns=campaigns)


# ADREQUEST BUTTON ON CAMPAIGN SHOW
@app.route('/sponsor/adrequest/<id>', methods=['GET', 'POST'])
@login_required_sponsor
def adrequest(id):

  if request.method == 'POST':
    budget_spent = 0
    campaigns = Campaign.query.filter_by(campaign_id=id).first()
    for adrequest in campaigns.adrequests:
      budget_spent += adrequest.payment_amount
    message = request.form.get('message')
    requirements = request.form.get('requirements')
    payment_amount = request.form.get('payment_amount')
    status = 'PENDING'
    flag_status = "ACTIVE"
    if campaigns.visibility == "Private":
      influencer_id = request.form.get('influencer_id')
    else:
      influencer_id = None

    if budget_spent + float(payment_amount) >= campaigns.budget:
      flash("Budget Exceeded")
      return redirect(url_for('show_campaign'))
    new_adrequest = AdRequest(message=message,
                              requirements=requirements,
                              payment_amount=payment_amount,
                              status=status,
                              flag_status=flag_status,
                              influencer_id=influencer_id,
                              campaign_id=id)
    db.session.add(new_adrequest)
    db.session.commit()
    return redirect(url_for('show_campaign'))
  campaign = Campaign.query.filter_by(campaign_id=id).first()
  used_budget = 0
  campaigns = Campaign.query.filter_by(campaign_id=id).first()
  influencers = Influencer.query.all()
  for adrequest in campaigns.adrequests:
    used_budget += adrequest.payment_amount
  return render_template('/sponsor/adrequest.html',
                         campaign=campaign,
                         influencers=influencers,
                         used_budget=used_budget)


#ADREQUEST NEGOTIATION BY INFLUENCER
@app.route('/sponsor/adrequest/negotiation/<id>', methods=['GET', 'POST'])
@login_required_sponsor
def adrequestnegotiation(id):
  adrequests = AdRequest.query.filter_by(adrequest_id=id).first()
  return render_template('/sponsor/adrequest_negotiation.html',
                         adrequests=adrequests)


@app.route('/sponsor/show/<id>', methods=['GET', 'POST'])
def sponsorshow(id):
  adrequests = AdRequest.query.filter_by(adrequest_id=id).first()

  return render_template('/sponsor/adrequest_negotiation.html',
                         adrequests=adrequests)


#ADREQUEST NEGOTIATION ACCEPT BY SPONSOR
@app.route('/sponsor/negotiation/accept/<id>', methods=['GET', 'POST'])
@login_required_sponsor
def accept_negotiation(id):
  adrequests = AdRequest.query.filter_by(adrequest_id=id).first()
  negotiations = Negotiation.query.filter_by(adrequest_id=id).first()
  count = 0
  if adrequests.status == 'PENDING' and count == 0:
    adrequests.influencer_id = negotiations.influencer_id
    adrequests.status = 'ACCEPTED'
    count += 1
    db.session.commit()
  else:
    flash('AdRequest already accepted')
  return redirect(url_for('show_campaign'))


@app.route('/sponsor/negotiation/reject/<id>', methods=['GET', 'POST'])
@login_required_sponsor
def reject_negotiation(id):
  adrequests = AdRequest.query.filter_by(adrequest_id=id).first()
  negotiations = Negotiation.query.filter_by(adrequest_id=id).first()
  count = 0
  if adrequests.status == 'ACCEPTED' and count == 0:
    adrequests.status = 'PENDING'
    adrequests.influencer_id = None
    count += 1
    db.session.commit()
  else:
    flash('You have already rejected this negotiation')
  return redirect(url_for('show_campaign'))


# MODIFY BUTTON ON CAMAPIGN SHOW
@app.route('/sponsor/campaign/modify/<id>', methods=['GET', 'POST'])
@login_required_sponsor
def modify_campaign(id):
  campaigns = Campaign.query.filter_by(campaign_id=id).first()
  sponsors = Sponsor.query.filter_by(sponsor_id=campaigns.sponsor_id).first()
  # total_budget=0
  # for adrequest in campaigns.adrequests:
  #   total_budget+=adrequest.payment_amount
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
    if float(campaign.budget) + float(budget) >= sponsors.budget:
      flash('Budget Exceeded')
    else:
      db.session.commit()
    return redirect(url_for('show_campaign'))
  return render_template('/sponsor/campaign_modify_form.html',
                         campaigns=campaigns,
                         sponsors=sponsors)


# ADREQUEST EDIT BUTTON ON ADREQUEST TABLE
@app.route('/sponsor/adrequest/modify/<int:id>', methods=['GET', 'POST'])
@login_required_sponsor
def modify_adrequest(id):
  adrequest = AdRequest.query.filter_by(adrequest_id=id).first()
  influencers = Influencer.query.filter_by(status="ACTIVE").all()
  sponsor = Sponsor.query.filter_by(
      sponsor_id=adrequest.campaign.sponsor_id).first()
  negotiations = Negotiation.query.filter_by(adrequest_id=id).first()
  campaigns = Campaign.query.filter_by(
      campaign_id=adrequest.campaign_id).first()
  budget_spent = 0
  for adrequest in campaigns.adrequests:
    budget_spent += adrequest.payment_amount
  if request.method == 'POST':
    message = request.form.get('message')
    requirements = request.form.get('requirements')
    payment_amount = request.form.get('payment_amount')

    influencer_id = request.form.get('influencer_id')
    adrequest.message = message
    adrequest.requirements = requirements
    adrequest.payment_amount = payment_amount
    adrequest.influencer_id = influencer_id

    db.session.commit()
    return redirect(url_for('show_campaign'))
  return render_template('/sponsor/adrequest_modify_form.html',
                         adrequests=adrequest,
                         sponsor=sponsor,
                         budget_spent=budget_spent,
                         influencers=influencers)


#SEND BUTTON ON PRIVATE ADREQUESTS
@app.route('/sponsor/send/adrequest/<id>', methods=['GET', 'POST'])
@login_required_sponsor
def send_request(id):
  if request.method == 'POST':
    adrequests = AdRequest.query.filter_by(adrequest_id=id).first()
    influencer_id = request.form.get('influencer_id')
    adrequests.influencer_id = influencer_id
    db.session.commit()
    return redirect(url_for('show_campaign'))
  influencers = Influencer.query.filter_by(status="ACTIVE").all()
  adrequests = AdRequest.query.filter_by(adrequest_id=id).first()
  return render_template('/sponsor/send_adrequest.html',
                         adrequests=adrequests,
                         influencers=influencers)


# SPONSOR FIND
@app.route('/sponsor/find')
@login_required_sponsor
def find_sponsor():
  return render_template('/sponsor/sponsor_find.html')


# CAMPAIGN SEARCH OPTION ON SPONSOR FIND
@app.route("/sponsor/campaign/search", methods=['GET', 'POST'])
@login_required_sponsor
def sponsor_campaign_search():
  if request.method == 'POST':
    campaign_search_type = request.form.get('campaign_search_type')
    campaign_search = request.form.get('camapign_search')

    if campaign_search_type == 'name':
      campaigns = Campaign.query.filter(
          Campaign.name.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/sponsor/sponsor_find.html',
                               campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'budget':
      campaigns = Campaign.query.filter_by(budget=camapign_search).all()
      flash("Search Complete")
      return render_template('/sponsor/sponsor_find.html', campaigns=campaigns)
    elif campaign_search_type == 'visibility':
      campaigns = Campaign.query.filter(
          Campaign.visibility.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/sponsor/sponsor_find.html',
                               campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'start_date':
      campaigns = Campaign.query.filter(
          Campaign.start_date.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/sponsor/sponsor_find.html',
                               campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'end_date':
      campaigns = Campaign.query.filter(
          Campaign.end_date.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/sponsor/sponsor_find.html',
                               campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'expiry':
      campaigns = Campaign.query.filter_by(
          expiry=campaign_search.upper()).all()
      if campaigns:
        return render_template('/sponsor/sponsor_find.html',
                               campaigns=campaigns)
      else:
        flash('No campaigns found')
  return render_template('/sponsor/sponsor_find.html')


#INFLUENCER SEARCH OPTION ON SPONSOR FIND
@app.route("/sponsor/influencer/search", methods=['GET', 'POST'])
@login_required_sponsor
def sponsor_influencer_search():
  if request.method == 'POST':
    influencer_search_type = request.form.get('influencer_search_type')
    influencer_search = request.form.get('influencer_search')

    if influencer_search_type == 'name':
      influencers = Influencer.query.filter(
          Influencer.influencer_name.like("%" + influencer_search +
                                          "%")).all()
      if influencers:
        return render_template('/sponsor/sponsor_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
    elif influencer_search_type == 'category':
      influencers = Influencer.query.filter(
          Influencer.category.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/sponsor/sponsor_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
    elif influencer_search_type == 'niche':
      influencers = Influencer.query.filter(
          Influencer.niche.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/sponsor/sponsor_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
    elif influencer_search_type == 'reach':
      influencers = Influencer.query.filter(
          Influencer.reach.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/sponsor/sponsor_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
  return render_template('/sponsor/sponsor_find.html')


# ADREQUEST SEARCH OPTION ON SPONSOR FIND
@app.route("/sponsor/adrequest/search", methods=['GET', 'POST'])
@login_required_sponsor
def sponsor_adrequest_search():
  if request.method == 'POST':
    adrequest_search_type = request.form.get('adrequest_search_type')
    adrequest_search = request.form.get('adrequest_search')

    if adrequest_search_type == 'payment_amount':
      adrequests = AdRequest.query.filter(
          AdRequest.payment_amount.like("%" + adrequest_search + "%")).all()
      if adrequests:
        return render_template('/sponsor/sponsor_find.html',
                               adrequests=adrequests)
      else:
        flash('No adrequests found')
    elif adrequest_search_type == 'message':
      adrequests = AdRequest.query.filter(
          AdRequest.message.like("%" + adrequest_search + "%")).all()
      if adrequests:
        return render_template('/sponsor/sponsor_find.html',
                               adrequests=adrequests)
      else:
        flash('No adrequests found')
    elif adrequest_search_type == 'requirements':
      adrequests = AdRequest.query.filter(
          AdRequest.requirements.like("%" + adrequest_search + "%")).all()
      if adrequests:
        return render_template('/sponsor/sponsor_find.html',
                               adrequests=adrequests)
      else:
        flash('No adrequests found')
  return render_template('/sponsor/sponsor_find.html')


#SPONSOR STATS
@app.route('/sponsor/stats')
@login_required_sponsor
def sponsor_stats():
  return render_template('/sponsor/sponsor_stats.html')


#SPONSOR CAMPAIGN PROGRESS CHART ON SPONSOR STATS
@app.route('/sponsor/campaign/progress/chart')
@login_required_sponsor
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


#INFLUENCER CHARTS BASED ON NICHE ON SPONSOR STATS
@app.route('/sponsor/influencer/niche/chart')
@login_required_sponsor
def influencerNicheCount():
  data = []
  dict = {}
  query = db.session.query(
      Influencer.niche,
      func.count(Influencer.niche).label('count')).group_by(Influencer.niche)

  for niche, count in query:
    dict = {'name': niche, 'count': count}
    data.append(dict)

  return jsonify(data)
