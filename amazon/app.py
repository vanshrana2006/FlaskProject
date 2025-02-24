from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from flask_wtf import CSRFProtect
import os
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
import openai
from datetime import timedelta

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Secret Key for Flask and CSRF Protection
app.secret_key = os.getenv("FLASK_SECRET_KEY", "your_secret_key_here")
csrf = CSRFProtect(app)  # Enable CSRF Protection

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set session lifetime (if desired)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

# Define User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    dob = db.Column(db.String(10), nullable=False)  # Assuming date of birth as a string (YYYY-MM-DD)
    gender = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<User {self.email}>"

# Initialize Database
with app.app_context():
    db.create_all()

# Generate 6-digit OTP
def generate_otp():
    return str(random.randint(100000, 999999))

# Send OTP via Email
def send_otp_email(email, otp):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    if not sender_email or not sender_password:
        print("Error: Missing EMAIL_ADDRESS or EMAIL_PASSWORD in .env")
        return False
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = "Your OTP Code"
        msg.attach(MIMEText(f"Your OTP is: {otp}", "plain"))
        server.sendmail(sender_email, email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Configure Chatbot API key
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_ai_response', methods=['POST'])
def get_ai_response():
    user_message = request.json.get('message')
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Change to "gpt-3.5-turbo" if needed
            messages=[{"role": "user", "content": user_message}]
        )
        ai_reply = response['choices'][0]['message']['content']
        return jsonify({"response": ai_reply})
    except Exception as e:
        print(f"Error fetching AI response: {e}")
        return jsonify({"response": "An error occurred while processing your request."})

# Root Route (Home Page)
@app.route('/', endpoint='index')  # Explicitly name the endpoint 'index'
def home():
    user_email = session.get('user')
    user = User.query.filter_by(email=user_email).first() if user_email else None
    
    # Retrieve the Google Maps API key from environment variables
    google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    
    return render_template('index.html', user=user, google_maps_api_key=google_maps_api_key)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        email = form.email.data.strip().lower()
        phone = form.phone.data.strip()
        dob = form.dob.data
        gender = form.gender.data
        password = form.password.data.strip()
        confirm_password = form.confirm_password.data.strip()
        if password != confirm_password:
            flash("Passwords do not match!", "error")
            return redirect(url_for('signup'))
        existing_user = User.query.filter((User.email == email) | (User.phone == phone)).first()
        if existing_user:
            flash("User already registered with this email or phone!", "error")
            return redirect(url_for('signup'))
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            dob=dob,
            gender=gender,
            password=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        identifier = form.identifier.data.strip().lower()
        password = form.password.data.strip()
        user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()
        if user and check_password_hash(user.password, password):
            session['user'] = user.email
            session.permanent = True  # Make the session permanent (persist across browser sessions)
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        flash("Invalid credentials!", "error")
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully!", "info")
    return redirect(url_for('index'))

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    session.pop('reset_email', None)  # Clear previous session data
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        identifier = form.identifier.data.strip().lower()
        user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()
        if not user:
            flash("No account found with this email or phone!", "error")
        else:
            otp = generate_otp()
            session['reset_email'] = user.email
            session[f'otp_{user.email}'] = otp
            if send_otp_email(user.email, otp):
                flash("OTP has been sent to your email.", "info")
                return redirect(url_for('reset_password'))
            flash("Failed to send OTP. Please try again.", "error")
    return render_template('forgot_password.html', form=form)

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = session.get('reset_email')
    if not email:
        flash("Session expired. Please request a new OTP.", "error")
        return redirect(url_for('forgot_password'))
    stored_otp = session.get(f'otp_{email}')
    form = ResetPasswordForm()
    if form.validate_on_submit():
        otp = form.otp.data.strip()
        new_password = form.new_password.data.strip()
        confirm_password = form.confirm_password.data.strip()
        if otp != stored_otp:
            flash("Invalid OTP!", "error")
        elif new_password != confirm_password:
            flash("Passwords do not match!", "error")
        elif len(new_password) < 8:
            flash("Password must be at least 8 characters long!", "error")
        else:
            user = User.query.filter_by(email=email).first()
            if user:
                user.password = generate_password_hash(new_password)
                db.session.commit()
                flash("Password reset successfully! Please log in.", "success")
                session.pop('reset_email', None)
                session.pop(f'otp_{email}', None)
                return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

@app.route('/profile')
def profile():
    if 'user' not in session:
        flash("You need to log in to view your profile.", "warning")
        return redirect(url_for('login'))
    user_email = session['user']
    user = User.query.filter_by(email=user_email).first()
    if not user:
        flash("User not found. Please log in again.", "error")
        return redirect(url_for('login'))
    return render_template('profile.html', user=user)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    # Retrieve the cart from the session
    cart = session.get('cart', [])
    
    # Calculate total price from the cart
    total_price = sum(item['price'] * item['quantity'] for item in cart)
    
    # Define delivery charges logic
    if total_price >= 500:  # Free delivery for orders above ₹500
        delivery_charges = 0
    else:
        delivery_charges = 50  # Fixed delivery charge for orders below ₹500
    
    # Calculate grand total
    grand_total = total_price + delivery_charges

    if request.method == 'POST':
        # Process payment and save order details
        return render_template(
            'order_confirmation.html',
            grand_total=grand_total,
            delivery_charges=delivery_charges
        )

    return render_template(
        'checkout.html',
        cart=cart,
        total_price=total_price,
        delivery_charges=delivery_charges,
        grand_total=grand_total
    )

@app.route('/order-confirmation')
def order_confirmation():
    return render_template('order_confirmation.html')

@app.route('/clothes')
def clothes():
    return render_template('clothes.html')

@app.route('/health')
def health():
    return render_template('health.html')

@app.route('/beauty')
def beauty():
    return render_template('beauty.html')

@app.route('/orders')
def orders():
    return render_template('order.html')

@app.route('/fashion_trends')
def fashion_trends():
    return render_template('fashion_trends.html')

@app.route('/mobiles')
def mobiles():
    return render_template('mobiles.html')

@app.route('/new_arrival_toys')
def new_arrival_toys():
    return render_template('new_arrival_toys.html')

@app.route('/pet_care')
def pet_care():
    return render_template('pet_care.html')

@app.route('/furniture')
def furniture():
    return render_template('furniture.html')

@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    return render_template('cart.html', cart_items=cart_items)

if __name__ == '__main__':
    app.run(debug=True)