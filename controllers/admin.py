from flask import Flask, render_template, request, url_for, flash, session, jsonify

from werkzeug.utils import redirect
from application.config import LocalDevelopmentConfig

import json
from flask import current_app as app

from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest
from controllers.usermanager import userlogin, login_required, userlogout

fatalerror="Error Occured. Please contact Administrator"
# ADMIN REGISTER
@app.route('/admin/register', methods=['GET', 'POST'])
def adminregister():
  if request.method == 'POST':
    try:
      admin_id = request.form['admin_id']
      admin_name = request.form['admin_name']
      admin_password = request.form['admin_password']
      admin_register = Admin(admin_name=admin_name,
                             admin_id=admin_id,
                             admin_password=admin_password)
      db.session.add(admin_register)
      db.session.commit()
      return render_template('login.html')
    except:
      flash(fatalerror)
  return render_template('register.html')


# ADMIN LOGIN
@app.route('/admin/login', methods=['GET', 'POST'])
def checkAdminLogin():
  if request.method == 'POST':
    try:
      admin_id = request.form.get('admin_id')
      password = request.form.get('admin_password')
      if admin_id == '' or password == '':
        flash("Please enter all the fields")
        return render_template('login.html')
      admin = Admin.query.filter_by(admin_id=admin_id).first()
      if admin:
        if admin.admin_password == password:
          userlogin(admin, 'admin')
          return redirect(url_for('admindashboard'))
        else:
          flash("Password is wrong")
          return render_template('login.html')
      else:
        flash("User ID not registered")
        return render_template('login.html')
    except:
      flash(fatalerror)
  return render_template("login.html")


# ADMIN DASHBOARD
@app.route('/admin/dashboard')
@login_required
def admindashboard():
  user_id = session['user_id']
  return render_template('/admin/admin_dashboard.html', user_id=user_id)


# ADMIN PROFILE
@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
  try:
    admin_id = session["user_id"]
    if request.method == 'POST':
      new_password = request.form.get('new_password')
      confirm_new_password = request.form.get('confirm_new_password')
      admin_password = request.form.get('admin_password')
  
      admin = Admin.query.filter_by(admin_id=admin_id).first()
      if admin:
        if admin.admin_password == admin_password:
          if new_password == confirm_new_password:
            admin.admin_password = new_password
            db.session.commit()
            flash("Password Successfully Updated")
            return render_template('admin/admin_profile.html', admin_id=admin_id)
          else:
            flash("Your Passwords do not match")
            return render_template('admin/admin_profile.html', admin_id=admin_id)
        else:
          flash(
              "The Password entered is Incorrect. You are not allowed to change password"
          )
          return render_template('admin/admin_profile.html', admin_id=admin_id)
      else:
        flash("User ID not registered")
        return render_template('admin/admin_profile.html', admin_id=admin_id)
  except:
    flash(fatalerror)
  return render_template('/admin/admin_profile.html', admin_id=admin_id)


# ADMIN INFO
@app.route('/admin/info')
def admin_info():
  admin_id = session["user_id"]
  sponsors = Sponsor.query.all()
  influencers = Influencer.query.all()
  campaigns = Campaign.query.all()
  adrequests = AdRequest.query.all()
  return render_template('/admin/admin_info.html',
                         admin_id=admin_id,
                         sponsors=sponsors,
                         influencers=influencers,
                         campaigns=campaigns,
                         adrequests=adrequests)


# FLAG SPONSOR BUTTON ON ADMIN INFO
@app.route('/admin/sponsor/flag/<id>')
def flagsponsor(id):
  try:
    sponsor = Sponsor.query.filter_by(sponsor_id=id).first()
    if sponsor.status == 'ACTIVE':
      sponsor.status = 'INACTIVE'
      db.session.commit()
    else:
      sponsor.status = 'ACTIVE'
      db.session.commit()
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


#FLAG INFLUENCER BUTTON ON ADMIN INFO
@app.route('/admin/influencer/flag/<id>')
def flaginfluencer(id):
  try:
    influencer = Influencer.query.filter_by(influencer_id=id).first()
    if influencer.status == 'ACTIVE':
      influencer.status = 'INACTIVE'
      db.session.commit()
    else:
      influencer.status = 'ACTIVE'
      db.session.commit()
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


#FLAG CAMPAIGN BUTTON ON ADMIN INFO
@app.route('/admin/campaign/flag/<id>')
def flagcampaign(id):
  try:
    campaign = Campaign.query.filter_by(campaign_id=id).first()
    if campaign.status == 'ACTIVE':
      campaign.status = 'INACTIVE'
      db.session.commit()
    else:
      campaign.status = 'ACTIVE'
      db.session.commit()
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


#FLAG ADREQUEST BUTTON ON ADMIN INFO
@app.route('/admin/adrequest/flag/<id>')
def flagadrequest(id):
  try:
    adrequest = AdRequest.query.filter_by(adrequest_id=id).first()
    if adrequest.status == 'ACTIVE':
      adrequest.status = 'INACTIVE'
      db.session.commit()
    else:
      adrequest.status = 'ACTIVE'
      db.session.commit()
  except:
    flash(fatalerror)
  return redirect(url_for('admin_info'))


#ADMIN FIND
@app.route('/admin/find')
def admin_find():
  admin_id = session["user_id"]
  return render_template('/admin/admin_find.html', admin_id=admin_id)


#SPONSOR SEARCH OPTION ON ADMIN FIND
@app.route("/admin/sponsor/search", methods=['GET', 'POST'])
def sponsor_search():
  if request.method == 'POST':
    sponsor_search_type = request.form.get('sponsor_search_type')
    sponsor_search = request.form.get('sponsor_search')

    if sponsor_search_type == 'name':
      sponsors = Sponsor.query.filter(
          Sponsor.sponsor_name.like("%" + sponsor_search + "%")).all()
      if sponsors:
        return render_template('/admin/admin_find.html', sponsors=sponsors)
      else:
        flash('No Sponsors Found')
    elif sponsor_search_type == 'industry':
      sponsors = Sponsor.query.filter(
          Sponsor.industry.like("%" + sponsor_search + "%")).all()
      if sponsors:
        return render_template('/admin/admin_find.html', sponsors=sponsors)
      else:
        flash('No Sponsors Found')
    elif sponsor_search_type == 'budget':
      sponsors = Sponsor.query.filter_by(budget=sponsor_search).all()
      if sponsors:
        return render_template('/admin/admin_find.html', sponsors=sponsors)
      else:
        flash('No Sponsors Found')
    elif sponsor_search_type == 'status':
      sponsors = Sponsor.query.filter_by(status=sponsor_search).all()
      if sponsors:
        return render_template('/admin/admin_find.html', sponsors=sponsors)
      else:
        flash('No Sponsors Found')
  return render_template('/admin/admin_find.html')


#INFLUENCER SEARCH OPTION ON ADMIN FIND
@app.route("/admin/influencer/search", methods=['GET', 'POST'])
def influencer_search():
  if request.method == 'POST':
    influencer_search_type = request.form.get('influencer_search_type')
    influencer_search = request.form.get('influencer_search')

    if influencer_search_type == 'name':
      influencers = Influencer.query.filter(
        Influencer.influencer_name.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/admin/admin_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
    elif influencer_search_type == 'category':
      influencers = Influencer.query.filter(
        Influencer.category.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/admin/admin_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
    elif influencer_search_type == 'niche':
      influencers = Influencer.query.filter(
        Influencer.niche.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/admin/admin_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
    elif influencer_search_type == 'reach':
      influencers = Influencer.query.filter(
        Influencer.reach.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/admin/admin_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
    elif influencer_search_type == 'status':
      influencers = Influencer.query.filter(
        Influencer.status.like("%" + influencer_search + "%")).all()
      if influencers:
        return render_template('/admin/admin_find.html',
                               influencers=influencers)
      else:
        flash('No influencers found')
  return render_template('/admin/admin_find.html')





#CAMPAIGN SEARCH OPTION ON ADMIN FIND
@app.route("/admin/campaign/search", methods=['GET', 'POST'])
def campaign_search():
  if request.method == 'POST':
    campaign_search_type = request.form.get('campaign_search_type')
    campaign_search = request.form.get('campaign_search')

    if campaign_search_type == 'name':
      campaigns = Campaign.query.filter(
        Campaign.name.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/admin/admin_find.html', campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'budget':
      campaigns = Campaign.query.filter(
        Campaign.budget.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/admin/admin_find.html', campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'visibility':
      campaigns = Campaign.query.filter(
        Campaign.visibility.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/admin/admin_find.html', campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'start_date':
      campaigns = Campaign.query.filter(
        Campaign.start_date.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/admin/admin_find.html', campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'end_date':
      campaigns = Campaign.query.filter(
        Campaign.end_date.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/admin/admin_find.html', campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'description':
      campaigns = Campaign.query.filter(
        Campaign.des.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/admin/admin_find.html', campaigns=campaigns)
      else:
        flash('No campaigns found')
    elif campaign_search_type == 'status':
      campaigns = Campaign.query.filter(
          Campaign.status.like("%" + campaign_search + "%")).all()
      if campaigns:
        return render_template('/admin/admin_find.html', campaigns=campaigns)
      else:
        flash('No campaigns found')
  return render_template('/admin/admin_find.html')


#ADREQUEST SEARCH OPTION ON ADMIN FIND
@app.route("/admin/adrequest/search", methods=['GET', 'POST'])
def adrequest_search():
  if request.method == 'POST':
    adrequest_search_type = request.form.get('adrequest_search_type')
    adrequest_search = request.form.get('adrequest_search')

    if adrequest_search_type == 'payment_amount':
      adrequests = AdRequest.query.filter_by(
          payment_amount=adrequest_search).all()
      if adrequests:
        return render_template('/admin/admin_find.html', adrequests=adrequests)
      else:
        flash('No adrequests found')
    elif adrequest_search_type == 'message':
      adrequests = AdRequest.query.filter(
          AdRequest.message.like("%" + adrequest_search + "%")).all()
      if adrequests:
        return render_template('/admin/admin_find.html', adrequests=adrequests)
      else:
        flash('No adrequests found')
    elif adrequest_search_type == 'requirements':
      adrequests = AdRequest.query.filter(
          AdRequest.requirements.like("%" + adrequest_search + "%")).all()
      if adrequests:
        return render_template('/admin/admin_find.html', adrequests=adrequests)
      else:
        flash('No adrequests found')
  return render_template('/admin/admin_find.html')


#ADMIN STATS LINK ON DASHBOARD
@app.route('/admin/show/stats')
def show_stats():
  return render_template('/admin/admin_chart.html')


#ADMIN STATS
@app.route('/admin/stats')
@login_required
def admin_stats():
  admin_id = session["user_id"]
  sponsors = Sponsor.query.all()
  data = []
  for sponsor in sponsors:
    data.append({'users': sponsor.sponsor_name, 'value': sponsor.budget})
  data.sort(key=lambda x: x['value'], reverse=True)

  return data
 


# ADMIN STATS FETCH CHART BUTTON
@app.route('/admin/fetchChart')
def fetchChart():
  noOfSponsors = Sponsor.query.count()
  noOfInfluencers = Influencer.query.count()
  data_labels = {'users': "Sponsors", "value": noOfSponsors}
  data_values = {"users": "Influencers", "value": noOfInfluencers}
  data = []
  data.append(data_labels)
  data.append(data_values)
  return data
