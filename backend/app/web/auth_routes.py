import os
import platform
import random
import re
import smtplib
from email.mime.text import MIMEText

from flask import (
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)

from app.web import web_bp
from app import db
from app.models.user import User
from app.models.role import Role

# ------------------------------------------------------------------
# Approver email + email sending helpers
# ------------------------------------------------------------------

# You can override this via environment variable APPROVER_EMAIL
APPROVER_EMAIL = os.environ.get("APPROVER_EMAIL", "sri.sakthivel@tvsmotor.com")

# Try to import pywin32 Outlook client for Windows
try:
    import win32com.client  # type: ignore

    HAVE_OUTLOOK = True
except Exception:
    HAVE_OUTLOOK = False


def generate_approval_code() -> str:
    """Return a 6-digit numeric approval code as string."""
    return f"{random.randint(0, 999999):06d}"


def send_approval_email(
    approver_email: str,
    user_name: str,
    user_email: str,
    code: str,
) -> None:
    """
    Send approval code to approver.

    Priority:
    1) Windows + Outlook (pywin32)
    2) SMTP (any OS) using env vars:
       SMTP_HOST, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD,
       SMTP_FROM, SMTP_USE_TLS
    """

    subject = "Approval Required for New NIRIX Web Registration"
    body = (
        "Dear Approver,\n\n"
        "A new user has requested access to the NIRIX Diagnostic Web Tool.\n\n"
        f"Name   : {user_name}\n"
        f"Email  : {user_email}\n\n"
        f"Approval Code: {code}\n\n"
        "Please share this 6-digit code with the requester.\n"
        "They must enter it in the registration screen to complete registration.\n\n"
        "Regards,\n"
        "NIRIX Diagnostic Tool\n"
    )

    system_name = platform.system().lower()

    # ------------------------------------------------------------------
    # 1) Windows – use Outlook via pywin32 (like Raspberry-Pi)
    # ------------------------------------------------------------------
    if HAVE_OUTLOOK and system_name == "windows":
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)  # 0 = olMailItem
            mail.To = approver_email
            mail.Subject = subject
            mail.Body = body
            mail.Send()
            return
        except Exception as e:
            # Fall through to SMTP
            print(f"[EMAIL] Outlook send failed: {e}")

    # ------------------------------------------------------------------
    # 2) SMTP fallback (any OS)
    # ------------------------------------------------------------------
    smtp_host = os.environ.get("SMTP_HOST")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USERNAME")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    smtp_from = os.environ.get("SMTP_FROM") or smtp_user
    smtp_use_tls = os.environ.get("SMTP_USE_TLS", "1") == "1"

    if not smtp_host or not smtp_from:
        # No SMTP config -> fail clearly
        raise RuntimeError(
            "SMTP not configured. Set SMTP_HOST, SMTP_USERNAME, "
            "SMTP_PASSWORD, SMTP_FROM (and optionally SMTP_PORT, SMTP_USE_TLS)."
        )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = smtp_from
    msg["To"] = approver_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        if smtp_use_tls:
            server.starttls()
        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)
        server.send_message(msg)


# ------------------------------------------------------------------
# Web routes
# ------------------------------------------------------------------


@web_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard"))
    return redirect(url_for("web.login"))


@web_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        pin = (request.form.get("pin") or "").strip()

        if not email or not pin:
            flash("Email and PIN are required.", "error")
            return render_template("login.html")

        if not pin.isdigit() or len(pin) != 4:
            flash("PIN must be a 4-digit number.", "error")
            return render_template("login.html")

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(pin):
            flash("Invalid email or PIN.", "error")
            return render_template("login.html")

        if not user.is_approved:
            flash("Your account is pending approval.", "warning")
            return render_template("login.html")

        if not user.is_active:
            flash("Your account has been deactivated.", "error")
            return render_template("login.html")

        login_user(user)
        flash(f"Welcome, {user.full_name}!", "success")
        return redirect(url_for("web.dashboard"))

    return render_template("login.html")


@web_bp.route("/register", methods=["GET", "POST"])
def register():
    """
    Two-step registration flow with approval code:

    Step 1 (action=start):
        - User enters First Name, Last Name, Email, PIN, Confirm PIN
        - System generates approval code and emails it to APPROVER_EMAIL
        - Data stored in session["pending_registration"]
        - Page shows "enter approval code" screen

    Step 2 (action=verify):
        - User enters 6-digit approval code
        - If matches pending data, user is created with is_approved = True

    Extra: action=resend
        - Generates new approval code
        - Sends again to approver
    """
    # Allow reset of pending registration
    if request.method == "GET":
        if request.args.get("reset") == "1":
            session.pop("pending_registration", None)

        pending = session.get("pending_registration")
        return render_template(
            "register.html",
            pending=pending,
        )

    # POST
    action = request.form.get("action", "start")
    pending = session.get("pending_registration")

    # ------------------------------------------------------------------
    # STEP 1: Start registration – collect details & send approval code
    # ------------------------------------------------------------------
    if action == "start":
        first_name = (request.form.get("first_name") or "").strip()
        last_name = (request.form.get("last_name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        pin = (request.form.get("pin") or "").strip()
        confirm_pin = (request.form.get("confirm_pin") or "").strip()

        # Validate fields
        if not all([first_name, last_name, email, pin, confirm_pin]):
            flash("All fields are required.", "error")
            return render_template("register.html", pending=None)

        if pin != confirm_pin:
            flash("PIN and Confirm PIN do not match.", "error")
            return render_template("register.html", pending=None)

        if not re.fullmatch(r"\d{4}", pin):
            flash("PIN must be a 4-digit number.", "error")
            return render_template("register.html", pending=None)

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("An account already exists with this email.", "error")
            return render_template("register.html", pending=None)

        # Ensure Engineer role exists
        user_role = Role.query.filter_by(name="User").first()
        if user_role is None:
            user_role = Role(name="User", description="Standard user with test execution rights")
            db.session.add(user_role)
            db.session.commit()

        # Generate approval code
        approval_code = generate_approval_code()

        # Save pending registration in session
        pending = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "pin": pin,
            "role_id": user_role.id,
            "approval_code": approval_code,
        }
        session["pending_registration"] = pending

        # Send approval code email
        try:
            approver_email = os.environ.get("APPROVER_EMAIL", APPROVER_EMAIL)
        except NameError:
            approver_email = os.environ.get("APPROVER_EMAIL", APPROVER_EMAIL if 'APPROVER_EMAIL' in globals() else "approver@example.com")

        try:
            full_name = f"{first_name} {last_name}".strip()
            send_approval_email(
                approver_email=approver_email,
                user_name=full_name,
                user_email=email,
                code=approval_code,
            )
            flash(
                "Approval code has been sent to the approver. "
                "Please enter the code to complete registration.",
                "info",
            )
        except Exception as e:
            # Clear pending state on failure
            session.pop("pending_registration", None)
            flash(
                f"Failed to send approval email: {e}. "
                "Please contact your administrator.",
                "error",
            )
            return render_template("register.html", pending=None)

        # Show Step 2 (enter approval code)
        return render_template("register.html", pending=pending)

    # ------------------------------------------------------------------
    # STEP 2A: Resend approval code
    # ------------------------------------------------------------------
    if action == "resend":
        if not pending:
            flash(
                "No pending registration found. Please start registration again.",
                "error",
            )
            return render_template("register.html", pending=None)

        # Generate a NEW approval code
        new_code = generate_approval_code()
        pending["approval_code"] = new_code
        session["pending_registration"] = pending

        try:
            approver_email = os.environ.get("APPROVER_EMAIL", APPROVER_EMAIL)
        except NameError:
            approver_email = os.environ.get("APPROVER_EMAIL", APPROVER_EMAIL if 'APPROVER_EMAIL' in globals() else "approver@example.com")

        try:
            full_name = f"{pending['first_name']} {pending['last_name']}".strip()
            send_approval_email(
                approver_email=approver_email,
                user_name=full_name,
                user_email=pending["email"],
                code=new_code,
            )
            flash("Approval code resent to approver.", "info")
        except Exception as e:
            flash(
                f"Failed to resend approval email: {e}. "
                "Please contact your administrator.",
                "error",
            )

        return render_template("register.html", pending=pending)

    # ------------------------------------------------------------------
    # STEP 2B: Verify approval code
    # ------------------------------------------------------------------
    if action == "verify":
        if not pending:
            flash(
                "No pending registration found. Please start registration again.",
                "error",
            )
            return render_template("register.html", pending=None)

        entered_code = (request.form.get("approval_code") or "").strip()

        if not re.fullmatch(r"\d{6}", entered_code):
            flash("Approval code must be a 6-digit number.", "error")
            return render_template("register.html", pending=pending)

        if entered_code != pending.get("approval_code"):
            flash("Invalid approval code. Please check and try again.", "error")
            return render_template("register.html", pending=pending)

        # Code matches – create user and mark as approved
        user = User(
            first_name=pending["first_name"],
            last_name=pending["last_name"],
            email=pending["email"],
            role_id=pending["role_id"],
            is_active=True,
            is_approved=True,  # <-- auto-approved here
        )
        user.password = pending["pin"]  # 4-digit PIN hashing

        db.session.add(user)
        db.session.commit()

        # Clear pending registration
        session.pop("pending_registration", None)

        flash("Registration completed successfully. You can now log in.", "success")
        return redirect(url_for("web.login"))

    # Fallback – unknown action
    flash("Invalid registration action.", "error")
    return render_template("register.html", pending=pending)


@web_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("web.login"))
