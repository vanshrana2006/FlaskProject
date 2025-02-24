from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class SignupForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    phone = StringField(
        "Phone Number",
        validators=[
            DataRequired(),
            Regexp(r"^\d{10}$", message="Phone number must be exactly 10 digits."),
        ],
    )
    dob = DateField("Date of Birth", format="%Y-%m-%d", validators=[DataRequired()])
    gender = SelectField(
        "Gender",
        choices=[("male", "Male"), ("female", "Female"), ("other", "Other")],
        validators=[DataRequired()],
    )
    password = PasswordField(
        "Create Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create Your Amazon Account")


class LoginForm(FlaskForm):
    identifier = StringField("Email or Phone", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")


class ForgotPasswordForm(FlaskForm):
    identifier = StringField("Email or Phone", validators=[DataRequired()])
    submit = SubmitField("Send OTP")


class ResetPasswordForm(FlaskForm):
    otp = StringField("OTP", validators=[DataRequired(), Regexp(r"^\d{6}$", message="Enter a valid 6-digit OTP.")])
    new_password = PasswordField(
        "New Password",
        validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")],
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("new_password", message="Passwords must match.")],
    )
    submit = SubmitField("Reset Password")
