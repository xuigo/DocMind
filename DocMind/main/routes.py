from flask import render_template, url_for, redirect, flash, abort
from flask import Blueprint
from flask_login import current_user

import DocMind.config.utils as utils
import DocMind.config.DocTemplate as DocTemplates

main = Blueprint("main", __name__)


@main.route('/')
def index():
    if current_user.is_authenticated:
        flag = utils.information_completion(current_user)
        if flag:
            temps = DocTemplates.templates_index()
            return render_template('main/index.html', title="首页", DocTemplates=temps)
        else:
            flash('请首先完善个人信息，实名认证，绑定部门', 'danger')
            return redirect(url_for('User.setting'))
    else:
        temps = DocTemplates.templates_index()
        return render_template('main/index.html', title="首页", DocTemplates=temps)


@main.route('/development')
def development():
    return render_template('main/development.html')
