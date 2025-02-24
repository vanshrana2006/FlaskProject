Flask E-Commerce & Chatbot App
This is a Flask-based e-commerce application with user authentication, chatbot integration, OTP-based password reset, and product categories.

Features
User Authentication: Sign up, login, logout, profile management
OTP-based Password Reset: Secure password recovery using email OTP
Chatbot: Integrated OpenAI-powered chatbot
Product Categories: Clothes, Health, Beauty, Mobiles, Furniture, Pet Care, and more
Shopping Cart & Checkout: Add items to cart, calculate total, and process checkout
Google Maps Integration: API support for location-based services
Tech Stack
Backend: Flask, Flask-SQLAlchemy, Flask-WTF, OpenAI API
Database: SQLite
Frontend: Jinja Templates, Bootstrap
Security: CSRF Protection, Password Hashing
Email: SMTP for OTP verification
Installation
Clone the repository

bash
Copy
Edit
git clone https://github.com/vanshrana2006/FlaskProject
cd flask-ecommerce
Create a virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

nginx
Copy
Edit
pip install -r requirements.txt
Set up environment variables
Create a .env file and add:

ini
Copy
Edit
FLASK_SECRET_KEY=your_secret_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_email_password
OPENAI_API_KEY=your_openai_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
Initialize the database

nginx
Copy
Edit
flask db upgrade  # If using Flask-Migrate
Run the application

nginx
Copy
Edit
python app.py
Open in browser

cpp
Copy
Edit
http://127.0.0.1:5000
Usage
Sign up with name, email, phone, DOB, and gender.
Login using email or phone and password.
Reset password using OTP sent via email.
Browse products in different categories.
Add to cart and checkout with automatic delivery charge calculation.
Chatbot support for user queries.
API Endpoints
Endpoint	Method	Description
/signup	POST	User registration
/login	POST	User login
/logout	GET	Logout user
/forgot-password	POST	Request OTP for password reset
/reset-password	POST	Reset password with OTP
/cart	GET	View cart items
/checkout	GET/POST	Checkout process
/chatbot	GET	Chatbot UI
/get_ai_response	POST	Get AI chatbot response
Contributions
Feel free to fork, improve, and submit pull requests.

License
This project is licensed under the MIT License.
