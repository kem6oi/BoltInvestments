from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, db, Invitation # Import User, db, and Invitation
import uuid
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_admin:
            flash('Login successful!', 'success')
            # Placeholder for session management
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid credentials or not an admin. Please try again.', 'danger')
    return render_template('admin_login.html')

@admin_bp.route('/dashboard')
def dashboard():
    # TODO: Implement proper admin authentication check here
    total_users = User.query.count()
    # Placeholder data for other metrics
    total_investments_value = "N/A (Feature not implemented)"
    pending_verifications = User.query.filter_by(status='PendingVerification').count() # Actual count for this one
    active_investment_plans = "N/A (Feature not implemented)"

    return render_template('admin_dashboard.html',
                           title="Admin Dashboard",
                           total_users=total_users,
                           total_investments_value=total_investments_value,
                           pending_verifications=pending_verifications,
                           active_investment_plans=active_investment_plans)

@admin_bp.route('/users')
def list_users():
    # TODO: Implement proper admin authentication check here
    # For now, assuming admin is logged in if they can reach this.
    # A more robust temporary check for development could be:
    # admin_user = User.query.filter_by(is_admin=True, email="your_cli_created_admin_email@example.com").first()
    # if not admin_user: # or some other check indicating no admin is "active"
    #     flash("Admin access required.", "danger")
    #     return redirect(url_for('admin.login'))

    users = User.query.all()
    return render_template('admin_users.html', users=users, title="Manage Users")

@admin_bp.route('/invites/generate', methods=['POST'])
def generate_invitation():
    # Placeholder for admin authentication:
    # Replace 'admin@example.com' with the actual email of an admin user
    # or implement proper session management.
    admin_user = User.query.filter_by(email='admin@example.com', is_admin=True).first()
    if not admin_user:
        flash('Admin authentication required to generate invitation codes.', 'danger')
        return redirect(url_for('admin.login')) # Or a more appropriate error page

    uses_left = request.form.get('uses_left', default=1, type=int)
    expiration_days = request.form.get('expiration_days', type=int, default=None)
    expiration_date = None
    if expiration_days is not None:
        expiration_date = datetime.utcnow() + timedelta(days=expiration_days)

    # Generate unique code
    while True:
        new_code = uuid.uuid4().hex[:10].upper()
        if not Invitation.query.filter_by(code=new_code).first():
            break
    
    invitation = Invitation(
        code=new_code,
        uses_left=uses_left,
        expiration_date=expiration_date,
        generated_by_admin_id=admin_user.id,
        is_active=True # Default to active
    )
    
    db.session.add(invitation)
    db.session.commit()
    
    flash(f"Invitation code {new_code} generated successfully. Uses: {uses_left}, Expires: {expiration_date.strftime('%Y-%m-%d') if expiration_date else 'Never'}.", 'success')
    # Assuming admin.list_invitations will be created next.
    # For now, redirecting to dashboard or a placeholder.
    return redirect(url_for('admin.list_invitations')) # Updated redirect

@admin_bp.route('/invites', methods=['GET'])
def list_invitations():
    # Placeholder for admin authentication:
    admin_user = User.query.filter_by(email='admin@example.com', is_admin=True).first()
    if not admin_user:
        flash('Admin authentication required.', 'danger')
        return redirect(url_for('admin.login'))

    invitations = Invitation.query.order_by(Invitation.created_at.desc()).all()
    return render_template('admin_invites.html',
                           invitations=invitations,
                           title="Manage Invitation Codes",
                           now_utc=datetime.utcnow())

@admin_bp.route('/invites/<int:invite_id>/revoke', methods=['GET']) # TODO: Change to POST & add CSRF
def revoke_invitation(invite_id):
    # TODO: Implement proper admin authentication check here
    # Using the same placeholder as other admin routes for now
    admin_user = User.query.filter_by(email='admin@example.com', is_admin=True).first()
    if not admin_user:
        flash("Admin access required.", "danger")
        return redirect(url_for('admin.login'))

    invitation = Invitation.query.get_or_404(invite_id)
    invitation.is_active = False
    db.session.commit()
    flash(f"Invitation code {invitation.code} has been revoked.", 'success')
    return redirect(url_for('admin.list_invitations'))

@admin_bp.route('/users/<int:user_id>/activate', methods=['GET']) # TODO: Change to POST and add CSRF
def activate_user(user_id):
    # TODO: Implement proper admin authentication check here
    user = User.query.get_or_404(user_id)
    # Example check to prevent changing status of a "super admin"
    # This email should be configured, not hardcoded, or use a different flag.
    if user.email == 'admin@example.com' and user.is_admin:
         flash('Cannot change status of the primary admin account.', 'danger')
         return redirect(url_for('admin.list_users'))
    user.status = 'Active'
    db.session.commit()
    flash(f'User {user.email} activated successfully.', 'success')
    return redirect(url_for('admin.list_users'))

@admin_bp.route('/users/<int:user_id>/deactivate', methods=['GET']) # TODO: Change to POST and add CSRF
def deactivate_user(user_id):
    # TODO: Implement proper admin authentication check here
    user = User.query.get_or_404(user_id) # Fetches user or returns 404 if not found
    # Example check to prevent deactivating a "super admin"
    if user.email == 'admin@example.com' and user.is_admin:
        flash('Cannot deactivate the primary admin account.', 'danger')
        return redirect(url_for('admin.list_users'))
    user.status = 'Inactive'
    db.session.commit()
    flash(f'User {user.email} deactivated successfully.', 'success')
    return redirect(url_for('admin.list_users'))

# Add other admin routes here in the future
