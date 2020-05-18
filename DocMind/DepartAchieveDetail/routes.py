from flask import render_template, url_for, redirect, request, session, flash
from flask import Blueprint
from flask_login import current_user, login_required
from DocMind import db
import DocMind.config.utils as utils
from DocMind.models import *
import DocMind.config.DocTemplate as DocTemplates
from flask import abort

DepartAchieveDetail = Blueprint("DepartAchieveDetail", __name__)

@DepartAchieveDetail.route('/departmentcheck')
def departmentcheck():
    if current_user.is_authenticated:
        flag = utils.information_completion(current_user)
        check_flag = current_user.flag
        if flag and check_flag:
            if current_user.role == 4:
                return render_template('DepartAchieveDetail/headManager.html')
            else:
                flash("权限不足，此界面只有研发经理可以查看", 'danger')
                return redirect(url_for('main.index'))
        elif flag:
            flash('请等待或联系管理员进行信息审核', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('请首先完善个人信息', 'danger')
            return redirect(url_for('User.setting'))
    else:
        flash("权限管理模块,请登录后访问！", 'info')
        return redirect(url_for('User.login'))


@DepartAchieveDetail.route('/performance/query/<flag>')
@login_required
def performance_query(flag):
    querydata = Performance.query.filter_by(quarter=utils.quarter_calc()).all()
    data1 = []
    data2 = []
    for data_ in querydata:
        data_ = data_.to_dict()
        if data_['score'] == '0':
            data1.append(data_)
        else:
            data2.append(data_)
    if flag == '1':
        backdata = {"code": 0, "msg": "", "count": 1000, "data": data1}
        return backdata
    else:
        backdata = {"code": 0, "msg": "", "count": 1000, "data": data2}
        return backdata


@DepartAchieveDetail.route('/performance_iframe')
@login_required
def performance_iframe():
    templates = DocTemplates.templates_vkreport()
    return render_template('DepartAchieveDetail/headManger_iframeAdd.html', templates=templates)


@DepartAchieveDetail.route('/performance/<flag>', methods=['POST', 'GET'])
@login_required
def performance_flag(flag):
    if flag == 'iframe':
        operation = request.args.get('flag')
        if operation == "add":
            quarter = request.args.get('quiz1')
            department = request.args.get('quiz2')
            name = request.args.get('quiz3')
            department_score = request.args.get('department_score')
            note = request.args.get('note')
            performance = Performance(quarter=quarter, department=department,
                                      manager=name, score=department_score,
                                      note=note)
            db.session.add(performance)
            db.session.commit()
            return redirect(url_for('DepartAchieveDetail.performance_iframe'))
        else:
            modefy_id = int(operation)
            quarter = request.args.get('quiz1')
            department = request.args.get('quiz2')
            name = request.args.get('quiz3')
            department_score = request.args.get('department_score')
            note = request.args.get('note')
            performance = Performance.query.filter_by(id=modefy_id).first()
            performance.quarter = quarter
            performance.department = department
            performance.manager = name
            performance.score = department_score
            performance.note = note
            db.session.commit()
            return redirect(url_for('DepartAchieveDetail.performance_iframe'))
    elif flag == "submit":
        id = request.form.get('id')
        score = request.form.get('score')
        note = request.form.get('note')
        if score != '0':
            performance = Performance.query.filter_by(id=int(id)).first()
            performance.score = score
            performance.note = note
            db.session.commit()
        backdata = {"code": 0, "msg": "", "count": 1000}
        return backdata
    elif flag == "del":
        delid = request.form.get('id')
        print(delid)
        modefy_id = int(delid)
        performance = Performance.query.filter_by(id=modefy_id).first()
        db.session.delete(performance)
        db.session.commit()
        backdata = {"code": 0, "msg": "", "count": 1000}
        return backdata
    else:
        abort(404)
