from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_required
from flask import Blueprint, abort
import DocMind.config.utils as utils
from DocMind.models import *
from DocMind import db
import DocMind.config.DocTemplate as DocTemplates

DepartMemDetail = Blueprint("DepartMemDetail", __name__)

@DepartMemDetail.route('/staff')
def staff():
    if current_user.is_authenticated:
        jump = utils.information_completion(current_user)
        check_flag = current_user.flag
        if jump and check_flag:
            if current_user.role == 2:
                return render_template('DepartMemDetail/departDirector.html')
            elif current_user.role == 3 or current_user.role == 4:
                return render_template('DepartMemDetail/headManager.html')
            else:
                flash('您正在尝试访问只对管理人员和部门总监开放的界面，请确认权限', 'info')
                return redirect(url_for('main.index'))
        elif jump:
            flash('请等待或者联系管理员进行信息审核！', 'info')
            return redirect(url_for('main.index'))
        else:
            flash("请首先完善个人信息哦~", 'info')
            return redirect(url_for('User.setting'))
    else:
        flash("权限管理模块,请登录后访问！", 'info')
        return redirect(url_for('User.login'))


@DepartMemDetail.route('/staff/query/<flag>')
@login_required
def stuff_query(flag):
    create_staff_db()
    querydata = Staff.query.filter_by(quarter=utils.quarter_calc(),
                                      department=current_user.department).all()
    data1 = []
    data2 = []
    for data_ in querydata:
        if data_.other_score == "0":
            data1.append(data_.to_dict())
        else:
            data2.append(data_.to_dict())
    if flag == '1':
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = data1[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data1), "data": data_}
        return backdata
    else:
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = data2[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data2), "data": data_}
        return backdata


def create_staff_db():
    querydata = Oday.query.filter_by(quarter=utils.quarter_calc(),
                                     department=current_user.department).all()
    staff_name = []
    backdata = []
    for data in querydata:
        data = data.to_dict()
        confirm_data = Staff.query.filter_by(quarter=utils.quarter_calc(),
                                             name=data['member']).first()
        if confirm_data:
            continue
        if data['member'] in staff_name:
            for backdata_ in backdata:
                if backdata_['member'] == data['member']:
                    backdata_['score'] = str(
                        int(backdata_['score']) + int(data['score']))
                    backdata_[
                        'note'] += '{}:{}分;'.format(data['pname'], data['score'])
        else:
            data['note'] = '{}:{}分;'.format(data['pname'], data['score'])
            data['department_score'] = '0'
            staff_name.append(data['member'])
            backdata.append(data)
    for data in backdata:
        staff = Staff(quarter=utils.quarter_calc(), department=data['department'],
                      name=data['member'], project_score=data['score'],
                      other_score=data['department_score'], note=data['note'])
        db.session.add(staff)
        db.session.commit()


@DepartMemDetail.route('/staff_assess/<flag>', methods=['POST', 'GET'])
@login_required
def staff_assess(flag):
    if flag == 'iframe':
        operation = request.args.get('flag')
        if operation == "add":
            quarter = request.args.get('quiz1')
            name = request.args.get('quiz3')
            department = current_user.department
            project_score = request.args.get('project_score')
            other_score = request.args.get('department_score')
            staff = Staff(quarter=quarter, department=department,
                          name=name, project_score=project_score,
                          other_score=other_score, note="项目考核为0")
            db.session.add(staff)
            db.session.commit()
            return redirect(url_for('DepartMemDetail.employee_iframe'))
        else:
            modefy_id = int(operation)
            quarter = request.args.get('quiz1')
            name = request.args.get('quiz3')
            department = current_user.department
            project_score = request.args.get('project_score')
            department_score = request.args.get('department_score')
            staff = Staff.query.filter_by(id=modefy_id).first()
            staff.quarter = quarter
            staff.name = name
            staff.department = department
            staff.project_score = project_score
            staff.other_score = department_score
            db.session.commit()
            return redirect(url_for('DepartMemDetail.employee_iframe'))
    elif flag == "submit":
        id = request.form.get('id')
        department = request.form.get('department')
        member = request.form.get('member')
        project_score = request.form.get('project_score')
        department_score = request.form.get('department_score')
        note = request.form.get('note')
        if department_score != '0':
            staff = Staff.query.filter_by(id=int(id)).first()
            staff.other_score = department_score
            db.session.commit()
        backdata = {"code": 0, "msg": "", "count": 1000}
        return backdata
    elif flag == "del":
        delid = request.form.get('id')
        print(delid)
        modefy_id = int(delid)
        staffdb = Staff.query.filter_by(id=modefy_id).first()
        db.session.delete(staffdb)
        db.session.commit()
        backdata = {"code": 0, "msg": "", "count": 1000}
        return backdata
    else:
        return abort(404)


@DepartMemDetail.route('/employee_iframe')
@login_required
def employee_iframe():
    templates = DocTemplates.templates_vkreport()
    return render_template('DepartMemDetail/departDirector_iframeDetail.html', templates=templates)


@DepartMemDetail.route('/employee_detail')
@login_required
def employee_detail():
    templates = DocTemplates.templates_vkreport()
    return render_template('DepartMemDetail/departDirector_iframeDetail.html', templates=templates)


@DepartMemDetail.route('/employee_iframe_header')
@login_required
def employee_iframe_header():
    templates = DocTemplates.templates_vkreport()
    return render_template('DepartMemDetail/departDirector_iframeDetail_read.html', templates=templates)


@DepartMemDetail.route('/staff_manager')
@login_required
def staff_manager():
    querydata = Staff.query.filter_by(quarter=utils.quarter_calc()).all()
    data = []
    for qdata in querydata:
        qdata = qdata.to_dict()
        data.append(qdata)
    page = int(request.args["page"])
    limit = int(request.args["limit"])
    qdata = data[(page-1)*limit: page * limit]
    backdata = {"code": 0, "msg": "", "count": len(data), "data": qdata}
    return backdata
