import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for session

# === Database Configuration ===
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///appointments.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# === Appointment Model ===
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    contact = db.Column(db.String(100))
    datetime = db.Column(db.String(100))
    issue = db.Column(db.String(200))

    def __init__(self, name, contact, datetime, issue):
        self.name = name
        self.contact = contact
        self.datetime = datetime
        self.issue = issue

# === Routes ===
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_msg = request.json['message'].lower()

    if "appointment" in user_msg or "book" in user_msg:
        reply = ("Sure! Please <a href='/book-appointment'>click here to book an appointment</a>.")
    
    elif "hospital" in user_msg or "clinic" in user_msg:
        reply = "Let me suggest some nearby hospitals. Please share your location or city."

    else:
        reply = google_search(user_msg)

    return jsonify({'reply': reply})

# === Google Search (Web Scraping) ===
API_KEY = 'AIzaSyDYM4kXkKvCMslpQ0BeClMX_BgFmCeEORc'  # Replace with your actual API key
SEARCH_ENGINE_ID = '5758578959a254c5e'  # Replace with your actual Search Engine ID

def google_search(query):
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': API_KEY,
        'cx': SEARCH_ENGINE_ID,
        'q': query
    }

    response = requests.get(url, params=params)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        result = data['items'][0]
        snippet = result['snippet']

        # ✅ Remove date patterns like "Jan 3, 2020 ..."
        import re
        snippet = re.sub(r'^[A-Za-z]{3,9} \d{1,2}, \d{4}[\s.–-]*', '', snippet)

        return f"{snippet.strip()}\nMore info: {result['link']}"
    else:
        return "Sorry, I couldn't find a relevant answer right now. Try rephrasing your question."

# === Appointment Form Save Route ===
@app.route('/book-appointment', methods=['GET', 'POST'])
def book_appointment():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        datetime_ = request.form['datetime']
        issue = request.form['issue']

        appointment = Appointment(name, contact, datetime_, issue)
        db.session.add(appointment)
        db.session.commit()
        return render_template('appointment_success.html', name=name)

    return render_template('book_appointment.html')

# === Admin: View, Edit, Delete Appointments ===
@app.route('/admin/appointments')
def view_appointments():
    if session.get('role') != 'admin':
        return redirect('/login_admin')
    appointments = Appointment.query.all()
    return render_template('admin_appointments.html', appointments=appointments)

@app.route('/delete_appointment/<int:id>', methods=['POST'])
def delete_appointment(id):
    if session.get('role') != 'admin':
        return redirect('/login_admin')
    appt = Appointment.query.get_or_404(id)
    db.session.delete(appt)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/edit_appointment/<int:id>', methods=['POST'])
def edit_appointment(id):
    if session.get('role') != 'admin':
        return redirect('/login_admin')
    appt = Appointment.query.get_or_404(id)
    appt.name = request.form['name']
    appt.contact = request.form['contact']
    appt.datetime = request.form['datetime']
    appt.issue = request.form['issue']
    db.session.commit()
    return jsonify({'success': True})

@app.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "admin123":
            session['role'] = 'admin'
            return redirect('/admin/appointments')
        else:
            return render_template("login.html", error="Invalid credentials")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# === Main ===
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)