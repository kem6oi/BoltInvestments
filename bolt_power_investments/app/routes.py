from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User, db # Import User model and db instance

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
