from flask import Flask, render_template, request, url_for, flash, session
from flask_migrate import Migrate
from werkzeug.utils import redirect
from application.config import LocalDevelopmentConfig
from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest
import json
from flask import current_app as app

from models.model import Sponsor, db, Influencer, Admin, Campaign, AdRequest
from controllers.usermanager import userlogin, login_required, userlogout


# ADMIN REGISTER
@app.route('/admin/register', methods=['GET', 'POST'])
def adminregister():
  if request.method == 'POST':
    admin_id = request.form['admin_id']
    admin_name = request.form['admin_name']
    admin_password = request.form['admin_password']
    admin_register = Admin(admin_name=admin_name,
                           admin_id=admin_id,
                           admin_password=admin_password)
    db.session.add(admin_register)
    db.session.commit()
    return render_template('login.html')
  return render_template('register.html')


# ADMIN LOGIN
@app.route('/admin/login', methods=['GET', 'POST'])
def checkAdminLogin():
  if request.method == 'POST':
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
  admin_id = session["user_id"]
  if request.method == 'POST':
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')
    # admin_id = request.form.get('admin_id')
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
        flash("You are not allowed to change password")
        return render_template('admin/admin_profile.html', admin_id=admin_id)
    else:
      flash("User ID not registered")
      return render_template('admin/admin_profile.html', admin_id=admin_id)

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
  sponsor = Sponsor.query.filter_by(sponsor_id=id).first()
  if sponsor.status == 'ACTIVE':
    sponsor.status = 'INACTIVE'
    db.session.commit()
  else:
    sponsor.status = 'ACTIVE'
    db.session.commit()
  return redirect(url_for('admindashboard'))




#FLAG INFLUENCER BUTTON ON ADMIN INFO
@app.route('/admin/influencer/flag/<id>')
def flaginfluencer(id):
  influencer = Influencer.query.filter_by(influencer_id=id).first()
  if influencer.status == 'ACTIVE':
    influencer.status = 'INACTIVE'
    db.session.commit()
  else:
    influencer.status = 'ACTIVE'
    db.session.commit()
  return redirect(url_for('admindashboard'))




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
      # sponsors = Sponsor.query.filter_by(sponsor_name=sponsor_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', sponsors=sponsors)
    elif sponsor_search_type == 'industry':
      sponsors = Sponsor.query.filter_by(industry=sponsor_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', sponsors=sponsors)

  return render_template('/admin/admin_find.html')




#INFLUENCER SEARCH OPTION ON ADMIN FIND
@app.route("/admin/influencer/search", methods=['GET', 'POST'])
def influencer_search():
  if request.method == 'POST':
    influencer_search_type = request.form.get('influencer_search_type')
    influencer_search = request.form.get('influencer_search')

    if influencer_search_type == 'name':
      influencers = Influencer.query.filter_by(
          influencer_name=influencer_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', influencers=influencers)
    elif influencer_search_type == 'category':
      influencers = Influencer.query.filter_by(
          category=influencer_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', influencers=influencers)
    elif influencer_search_type == 'niche':
      influencers = Influencer.query.filter_by(niche=influencer_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', influencers=influencers)
    elif influencer_search_type == 'reach':
      influencers = Influencer.query.filter_by(reach=influencer_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', influencers=influencers)
  return render_template('/admin/admin_find.html')




#CAMPAIGN SEARCH OPTION ON ADMIN FIND
@app.route("/admin/campaign/search", methods=['GET', 'POST'])
def campaign_search():
  if request.method == 'POST':
    campaign_search_type = request.form.get('campaign_search_type')
    camapign_search = request.form.get('camapign_search')

    if campaign_search_type == 'name':
      campaigns = Campaign.query.filter_by(name=camapign_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', campaigns=campaigns)
    elif campaign_search_type == 'budget':
      campaigns = Campaign.query.filter_by(budget=camapign_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', campaigns=campaigns)
    elif campaign_search_type == 'visibility':
      campaigns = Campaign.query.filter_by(visibility=campaign_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', campaigns=campaigns)
    elif campaign_search_type == 'start_date':
      campaigns = Campaign.query.filter_by(start_date=camapign_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', campaigns=campaigns)
    elif campaign_search_type == 'end_date':
      campaigns = Campaign.query.filter_by(end_date=camapign_search).all()
      flash("Search Complete")
      return render_template('/admin/admin_find.html', campaigns=campaigns)
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
      flash("Search Complete")
      return render_template('/admin/admin_find.html', adrequests=adrequests)
  return render_template('/admin/admin_find.html')



#ADMIN STATS
@app.route('/admin/stats')
@login_required
def admin_stats():
  admin_id = session["user_id"]
  noOfSponsors = Sponsor.query.count()
  noOfInfluencers = Influencer.query.count()

  data_labels = ["Sponsors", "Influencers"]
  data_values = [noOfSponsors, noOfInfluencers]
  return render_template('/admin/admin_chart.html',
                         admin_id=admin_id,
                         dlabels=json.dumps(data_labels),
                         data_values=json.dumps(data_values))







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
















