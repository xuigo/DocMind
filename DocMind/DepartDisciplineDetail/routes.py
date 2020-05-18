from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_required
from flask import Blueprint
import DocMind.config.utils as utils
from DocMind.models import *
from DocMind import db
import DocMind.config.DocTemplate as DocTemplates
from flask import abort

DepartDisciplineDetail = Blueprint("DepartDisciplineDetail", __name__)

@DepartDisciplineDetail.route('/teamcheck')  
def teamcheck():
    if current_user.is_authenticated:
        flag = utils.information_completion(current_user)
        check_flag = current_user.flag
        if flag and check_flag:
            current_user.role = 3
            if current_user.role == 3:
                return render_template('DepartDisciplineDetail/headManager.html')
            else:
                flash("权限不足，此界面只有人事负责人可以查看", 'danger')
                return redirect(url_for('main.index'))
        elif flag:
            flash('请等待或联系管理员进行信息审核', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('请首先完善个人信息进行审核', 'danger')
            return redirect(url_for('User.setting'))
    else:
        flash("权限管理模块,请登录后访问！", 'info')
        return redirect(url_for('User.login'))


@DepartDisciplineDetail.route('/discipline/query/<flag>')
@login_required
def discipline_query(flag):
    querydata = Discipline.query.filter_by(quarter=utils.quarter_calc()).all()
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


@DepartDisciplineDetail.route('/discipline_iframe')
@login_required
def discipline_iframe():
    jump = utils.information_completion(current_user)
    if not jump:
        flash("请首先完善个人信息哦~", 'info')
        return redirect(url_for('User.setting'))
    print('#'*10)
    templates = DocTemplates.templates_vkreport()
    return render_template('DepartDisciplineDetail/headManager_iframeDetail.html', templates=templates)


@DepartDisciplineDetail.route('/discipline/<flag>', methods=['POST', 'GET'])
@login_required
def discipline_flag(flag):
    if flag == 'iframe':
        operation = request.args.get('flag')
        if operation == "add":
            quarter = request.args.get('quiz1')
            department = request.args.get('quiz2')
            name = request.args.get('quiz3')
            department_score = request.args.get('department_score')
            note = request.args.get('note')
            discipline = Discipline(quarter=quarter, department=department,
                                    manager=name, score=department_score,
                                    note=note)
            db.session.add(discipline)
            db.session.commit()
            return redirect(url_for('DepartDisciplineDetail.discipline_iframe'))
        else:
            modefy_id = int(operation)
            quarter = request.args.get('quiz1')
            department = request.args.get('quiz2')
            name = request.args.get('quiz3')
            department_score = request.args.get('department_score')
            note = request.args.get('note')
            discipline = Discipline.query.filter_by(id=modefy_id).first()
            discipline.quarter = quarter
            discipline.department = department
            discipline.manager = name
            discipline.score = department_score
            discipline.note = note
            db.session.commit()
            return redirect(url_for('DepartDisciplineDetail.discipline_iframe'))
    elif flag == "submit":
        id = request.form.get('id')
        score = request.form.get('score')
        note = request.form.get('note')
        if score != '0':
            discipline = Discipline.query.filter_by(id=int(id)).first()
            discipline.score = score
            discipline.note = note
            db.session.commit()
        backdata = {"code": 0, "msg": "", "count": 1000}
        return backdata
    elif flag == "del":
        delid = request.form.get('id')
        print(delid)
        modefy_id = int(delid)
        discipline = Discipline.query.filter_by(id=modefy_id).first()
        db.session.delete(discipline)
        db.session.commit()
        backdata = {"code": 0, "msg": "", "count": 1000}
        return backdata
    else:
        abort(404)

