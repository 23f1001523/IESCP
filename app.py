from flask import Flask, render_template, request, url_for
from flask_migrate import Migrate
from werkzeug.utils import redirect

from application.config import LocalDevelopmentConfig

from models.model import Sponsor, db, Influencer, Admin,Campaign,AdRequest
from controllers.usermanager import userlogin, userlogout,login_required
app=None
migrate=Migrate()


def createApp():
  app = Flask(__name__, template_folder='templates')
  app.config.from_object(LocalDevelopmentConfig)
  app.app_context().push()
  db.init_app(app)
  db.create_all()
  admin=Admin.query.filter_by(admin_id="admin").first()
  if not admin:
    admin=Admin(admin_id="admin",admin_name="admin",admin_password="admin")
    db.session.add(admin)
    db.session.commit()
  migrate.init_app(app, db)
  return app

app=createApp()

@app.route('/base_dashboard')
def index():
  return render_template('base_dashboard.html')


@app.route('/')
def home():
  return render_template('index.html')

  # return render_template('users.html', admins=admins)


@app.route('/register', methods=['GET', 'POST'])
def register():
  return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
  return render_template('login.html')


@app.route('/logout', methods=['GET', 'POST'])
def logout():
  userlogout()
  return render_template('login.html')



# @app.route('/showchart')
# def showChart():
#   # ucount = db.session.query(User).count()
#   # scount = db.session.query(Sponsor).count()
#   # icount = db.session.query(Influencer).count()

#   # xdata = np.array(["Uers", "Sponsors", "Influencers"])
#   # ydata = np.array([ucount, scount, icount])

#   # plt.bar(xdata, ydata)
#   # # plt.savefig("/static/charts/user.png")
#   # plt.show()
#   xdata = np.array(["A", "B", "C", "D"])
#   ydata = np.array([3, 8, 1, 10])

#   plt.bar(xdata, ydata)
#   plt.savefig("/static/charts/user.png")
#   plt.show()

#   return render_template('index.html')


from controllers.admin import *
from controllers.sponsor import *
from controllers.influencer import *

if __name__ == '__main__':
  app.run('0.0.0.0', debug=True)
