from flask import Flask, render_template, request, redirect, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import smtplib, os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "rpgreens_secret_2026_secure")

# ── DATABASE: use /tmp for Railway (ephemeral), or local for dev ──
db_path = os.environ.get("DATABASE_URL", "sqlite:///database.db")
# Railway sometimes gives postgres:// — convert to sqlite for simplicity
if db_path.startswith("postgres://"):
    db_path = db_path.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ── MODEL ──
class Inquiry(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100))
    phone    = db.Column(db.String(20))
    email    = db.Column(db.String(120))
    space    = db.Column(db.String(100))
    business = db.Column(db.String(100))
    message  = db.Column(db.Text)
    status   = db.Column(db.String(50), default="New")
    date     = db.Column(db.DateTime, default=datetime.utcnow)

# ── HOME ──
@app.route("/")
def home():
    return render_template("index.html")
    @app.route('/robots.txt')
def robots():
    content = "User-agent: *\nAllow: /\n\nUser-agent: facebookexternalhit\nAllow: /\n\nUser-agent: Googlebot\nAllow: /"
    return content, 200, {'Content-Type': 'text/plain'}
# ── SUBMIT ──
@app.route("/submit", methods=["POST"])
def submit():
    inquiry = Inquiry(
        name     = request.form.get('name',''),
        phone    = request.form.get('phone',''),
        email    = request.form.get('email',''),
        space    = request.form.get('space',''),
        business = request.form.get('business',''),
        message  = request.form.get('message','')
    )
    db.session.add(inquiry)
    db.session.commit()
    # Email notification — set GMAIL_USER and GMAIL_PASS in Railway env vars
    try:
        gmail_user = os.environ.get("GMAIL_USER", "")
        gmail_pass = os.environ.get("GMAIL_PASS", "")
        if gmail_user and gmail_pass:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(gmail_user, gmail_pass)
            msg = (f"Subject: New Inquiry - RP Greens Complex\n\n"
                   f"Name: {inquiry.name}\nPhone: {inquiry.phone}\n"
                   f"Email: {inquiry.email}\nSpace: {inquiry.space}\n"
                   f"Business Type: {inquiry.business}\nMessage: {inquiry.message}")
            server.sendmail(gmail_user, "srivastava.vibhuti@gmail.com", msg)
            server.quit()
    except:
        pass
    return redirect("/?submitted=1")

# ── ADMIN LOGIN ──
@app.route("/admin", methods=["GET","POST"])
def admin():
    error = None
    if request.method == "POST":
        admin_user = os.environ.get("ADMIN_USER", "admin")
        admin_pass = os.environ.get("ADMIN_PASS", "rpgreens2026")
        if request.form.get('user') == admin_user and request.form.get('pass') == admin_pass:
            session['admin'] = True
            return redirect("/dashboard")
        error = "Invalid credentials. Please try again."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop('admin', None)
    return redirect("/admin")

# ── DASHBOARD ──
@app.route("/dashboard")
def dashboard():
    if 'admin' not in session:
        return redirect("/admin")
    sf        = request.args.get("status","All")
    data      = (Inquiry.query.filter_by(status=sf).order_by(Inquiry.date.desc()).all()
                 if sf != "All" else
                 Inquiry.query.order_by(Inquiry.date.desc()).all())
    total     = Inquiry.query.count()
    new_count = Inquiry.query.filter_by(status="New").count()
    contacted = Inquiry.query.filter_by(status="Contacted").count()
    closed    = Inquiry.query.filter_by(status="Closed").count()
    return render_template("dashboard.html", data=data, total=total,
                           new_count=new_count, contacted=contacted,
                           closed=closed, status_filter=sf)

# ── UPDATE STATUS ──
@app.route("/update/<int:id>/<status>")
def update(id, status):
    if 'admin' not in session: return redirect("/admin")
    inq = db.session.get(Inquiry, id)
    if inq:
        inq.status = status
        db.session.commit()
    return redirect("/dashboard")

# ── DELETE ──
@app.route("/delete/<int:id>")
def delete(id):
    if 'admin' not in session: return redirect("/admin")
    inq = db.session.get(Inquiry, id)
    if inq:
        db.session.delete(inq)
        db.session.commit()
    return redirect("/dashboard")

# ── INIT DB & RUN ──
with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
