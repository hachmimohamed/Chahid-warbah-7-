import os
import urllib.parse
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
import bot

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
if not os.path.exists(INSTANCE_DIR): os.makedirs(INSTANCE_DIR)
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(INSTANCE_DIR, 'database.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

EXE_API_TOKEN = "6c401e5e9895709c3a0ac136b273049bb08ababf"
LINKJUST_API_TOKEN = "a7cca9f244769bf43cbdd4a4f560630b2cb9dd5a"

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(50), unique=True)
    balance = db.Column(db.Integer, default=0)
    multitap_level = db.Column(db.Integer, default=1)
    referral_count = db.Column(db.Integer, default=0)
    last_linkjust_1 = db.Column(db.String(50))
    last_linkjust_2 = db.Column(db.String(50))
    last_exe_1 = db.Column(db.String(50))
    last_exe_2 = db.Column(db.String(50))

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_balance/<tg_id>', methods=['GET'])
def get_balance(tg_id):
    user = User.query.filter_by(telegram_id=str(tg_id)).first()
    if not user:
        user = User(telegram_id=str(tg_id))
        db.session.add(user)
        db.session.commit()
    return jsonify({"success": True, "balance": user.balance, "click_value": user.multitap_level})

@app.route('/api/update_balance', methods=['POST'])
def update_balance():
    data = request.json or {}
    user = User.query.filter_by(telegram_id=str(data.get('user_id'))).first()
    if user:
        user.balance += user.multitap_level
        db.session.commit()
        return jsonify({"success": True, "new_balance": user.balance})
    return jsonify({"success": False}), 404

@app.route('/api/get_short_link', methods=['POST'])
def get_short_link():
    try:
        data = request.json or {}
        mission = data.get('mission_type')
        tg_id = str(data.get('user_id', '12345'))
        url_cible = "https://t.me/ChahidWarbah7"
        
        if 'exe' in mission:
            res = requests.get(f"https://exe.io/api?api={EXE_API_TOKEN}&url={urllib.parse.quote(url_cible)}&subid={tg_id}", timeout=10)
            if res.status_code == 200: return jsonify({"success": True, "short_url": res.json().get('shortenedUrl', url_cible)})
        
        elif 'linkjust' in mission:
            url_encoded = urllib.parse.quote(url_cible, safe='')
            res = requests.get(f"https://linkjust.com/api?api={LINKJUST_API_TOKEN}&url={url_encoded}&subid={tg_id}", timeout=10)
            if res.status_code == 200:
                data = res.json()
                short_url = data.get('shortenedUrl') or data.get('short_url')
                return jsonify({"success": True, "short_url": short_url or url_cible})
        
        return jsonify({"success": True, "short_url": url_cible})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/complete_mission', methods=['POST'])
def complete_mission():
    try:
        data = request.json or {}
        tg_id = str(data.get('user_id'))
        mission = data.get('mission_type')
        user = User.query.filter_by(telegram_id=tg_id).first()
        if not user: return jsonify({"success": False}), 404
        
        maintenant = datetime.now()
        last_date_str = getattr(user, f"last_{mission}", None)
        if last_date_str:
            if maintenant - datetime.strptime(last_date_str, "%Y-%m-%d %H:%M:%S") < timedelta(hours=24):
                return jsonify({"success": False, "error": "Reviens dans 24h"}), 400

        user.balance += 500
        setattr(user, f"last_{mission}", maintenant.strftime("%Y-%m-%d %H:%M:%S"))
        db.session.commit()
        bot.send_notification(tg_id, "Félicitations ! Mission validée +500 DZ.")
        return jsonify({"success": True, "new_balance": user.balance})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/get_referral_info/<tg_id>', methods=['GET'])
def get_referral_info(tg_id):
    return jsonify({"success": True, "referral_count": 0, "referral_link": "https://t.me/ChahidWarbah7_bot?start=" + str(tg_id)})

@app.route('/api/buy_item', methods=['POST'])
def buy_item():
    return jsonify({"success": False, "error": "Boutique en maintenance"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
