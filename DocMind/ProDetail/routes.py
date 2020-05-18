from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_required
from flask import Blueprint, abort

import DocMind.config.utils as utils
from DocMind.models import *
from DocMind import db

ProDetail = Blueprint("ProDetail", __name__)


@ProDetail.route('/procheck')
def procheck():
    if current_user.is_authenticated:
        jump = utils.information_completion(current_user)
        check_flag = current_user.flag
        if jump and check_flag:
            # time is a param that get the value from admin
            time = False
            if time:
                return render_template('ProDetail/ProEveryFinish.html')
            else:
                return render_template('ProDetail/ProEvery.html')
        elif jump:
            flash('请等待或者联系管理员进行信息审核', 'info')
            return redirect(url_for('main.index'))

        else:
            flash("请首先完善个人信息哦~", 'info')
            return redirect(url_for('User.setting'))
    else:
        flash("权限管理模块,请登录后访问！", 'info')
        return redirect(url_for('User.login'))


@ProDetail.route('/project/query/<flag>')
@login_required
def project_query(flag):
    if flag == '1':
        projects = Project.query.filter_by(quarter=utils.quarter_calc()).all()
        datas = []
        for data in projects:
            msg = data.to_dict()
            datas.append(msg)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == '2':
        querydata = Score.query.filter_by(
            quarter=utils.quarter_calc(), name=current_user.username).all()
        datas = []
        for data_ in querydata:
            project_id = data_.project_id
            project = Project.query.filter_by(id=project_id).first()
            data_ = data_.to_dict()
            data_['prate'] = project.prate
            data_['schedule'] = project.schedule
            datas.append(data_)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == '3':
        querydata = Score.query.filter_by(quarter=utils.quarter_calc()).all()
        datas = []
        for data_ in querydata:
            project_id = data_.project_id
            project = Project.query.filter_by(id=project_id).first()
            data_ = data_.to_dict()
            data_['prate'] = project.prate
            data_['schedule'] = project.schedule
            datas.append(data_)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    else:
        abort(404)


@ProDetail.route('/project/<flag>', methods=['POST', 'GET'])
@login_required
def project(flag):
    if flag == "submit":
        delid = request.get_data('id').decode('utf-8').split('&')
        uid = int(delid[0].split('id=')[-1])
        result = delid[1].split('result=')[-1]
        project = Project.query.filter_by(id=int(uid)).first()
        quarter = utils.quarter_calc()
        pname = project.pname
        manager = project.manager
        department = current_user.department
        name = current_user.username
        project_id = project.id
        result = int(result)
        submit_score = Score.query.filter_by(project_id=project.id).first()
        if submit_score != None and submit_score.name == current_user.username:
            return {"code": 1}
        score = Score(quarter=quarter, pname=pname,
                      manager=manager, department=department,
                      name=name, result=result, project_id=project.id)
        db.session.add(score)
        db.session.commit()
        return {"code": 0}
    else:
        abort(404)
