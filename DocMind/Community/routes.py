from flask import render_template, url_for, redirect, flash
from flask_login import current_user, login_required
from flask import Blueprint

import DocMind.config.utils as utils

Community = Blueprint("Community", __name__)

# view of community
@Community.route("/community")
def community():
    if current_user.is_authenticated:
        return render_template('Community/community.html')
    else:
        flash("权限分层页面，请登录后在查看！", 'info')
        return redirect(url_for('User.login'))

