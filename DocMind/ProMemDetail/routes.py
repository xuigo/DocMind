from flask_login import current_user, login_required
from flask import render_template, url_for, redirect, request, flash, session
from flask import Blueprint, abort

import DocMind.config.utils as utils
from DocMind.models import *
from DocMind import db
import DocMind.config.DocTemplate as DocTemplates

ProMemDetail = Blueprint("ProMemDetail", __name__)


@ProMemDetail.route('/overcalc')
def overcalc():
    if current_user.is_authenticated:
        flag = utils.information_completion(current_user)
        check_flag = current_user.flag
        if flag and check_flag:
            if current_user.role == 1:
                return render_template('ProMemDetail/proManager.html')
            elif current_user.role == 2 or current_user.role == 5:
                return render_template('ProMemDetail/departDirector.html')
            elif current_user.role == 3 or current_user.role == 4:
                return render_template('ProMemDetail/headManager.html')
            else:
                abort(404)
        elif flag:
            flash("请等待或者联系管理员进行信息审核", 'info')
            return redirect(url_for('main.index'))
        else:
            flash('请首先完善个人信息，实名认证，绑定部门', 'danger')
            return redirect(url_for('User.setting'))
    else:
        flash("权限分层页面，请登录后在查看！", 'info')
        return redirect(url_for('User.login'))


@ProMemDetail.route('/overtime/query/<flag>')
@login_required
def oquery(flag):
    if flag == '1':
        project_id = Project.query.filter_by(manager=current_user.username,
                                             quarter=utils.quarter_calc()).first().id
        querydata = Oday.query.filter_by(project_id=project_id).all()
        data = []
        for msg in querydata:
            msg = msg.to_dict()
            if msg['rate'] == '0' and msg['days'] == '0' and msg['score'] == '0':
                data.append(msg)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = data[(page-1)*limit: page * limit]

        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    elif flag == '2':
        project_id = Project.query.filter_by(manager=current_user.username,
                                             quarter=utils.quarter_calc()).first().id
        querydata = Oday.query.filter_by(project_id=project_id).all()
        data = []
        for msg in querydata:
            msg = msg.to_dict()
            if msg['rate'] == '0' and msg['days'] == '0' and msg['score'] == '0':
                pass
            else:
                data.append(msg)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    elif flag == '3':
        querydata = Oday.query.filter_by(
            department=current_user.department).all()
        data = []
        for data_ in querydata:
            data_ = data_.to_dict()
            data.append(data_)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    elif flag == '4':
        querydata = Oday.query.filter().all()
        data = []
        for data_ in querydata:
            data_ = data_.to_dict()
            data.append(data_)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    else:
        abort(404)


@ProMemDetail.route('/overtime/<flag>', methods=['POST', 'GET'])
@login_required
def overtime(flag):
    if flag == "submit":
        delid = request.get_data('id').decode('utf-8').split('&')
        did = int(delid[0].split('id=')[-1])
        rate = delid[1].split('rate=')[-1]
        days = delid[2].split('days=')[-1]
        score = delid[3].split('score=')[-1]
        querydata = Oday.query.filter_by(id=did).first()
        querydata.rate = rate
        querydata.days = days
        querydata.score = score
        db.session.commit()
        backdata = {"code": 0, "msg": "删除"}
        return backdata
    elif flag == "delete":
        delid = int(request.get_data('id').decode('utf-8').split('id=')[-1])
        querydata = Oday.query.filter_by(id=delid).first()
        db.session.delete(querydata)
        db.session.commit()
        backdata = {"code": 0, "msg": "删除"}
        return backdata
    else:
        abort(404)


@ProMemDetail.route('/overtime_iframe')
@login_required
def overtime_iframe():
    templates = DocTemplates.templates_vkreport()
    return render_template("ProMemDetail/proManager_iframeDetail.html", templates=templates)


@ProMemDetail.route('/overtime_iframe_add')
@login_required
def overtime_iframe_add():
    templates = DocTemplates.templates_vkreport()
    return render_template("ProMemDetail/proManager_iframeAdd.html", templates=templates)


@ProMemDetail.route('/overtime_iframe_data', methods=['POST', 'GET'])
@login_required
def overtime_iframe_data():
    templates = DocTemplates.templates_vkreport()
    data = {}
    data['manager'] = request.args.get('manager')
    data['add'] = request.args.get('add')
    data['overrate'] = request.args.get('overrate')
    data['overdays'] = request.args.get('overdays')
    data['score'] = request.args.get('score')
    project_id = Project.query.filter_by(manager=current_user.username,
                                         quarter=utils.quarter_calc()).first()
    data['quarter'] = utils.quarter_calc()
    data['project'] = project_id.pname
    if data['add'] == "add":
        db.create_all()
        oday = Oday(quarter=data['quarter'], pname=data['project'],
                    manager=project_id.manager, department=project_id.department,
                    member=data['manager'], rate=data['overrate'],
                    days=data['overdays'], score=data['score'],
                    project_id=project_id.id)
        db.session.add(oday)
        db.session.commit()
    else:
        delid = int(data['add'])
        oday = Oday.query.filter_by(id=delid).first()
        oday.rate = request.args.get('overrate')
        oday.days = request.args.get('overdays')
        oday.score = request.args.get('score')
        db.session.commit()
    return render_template("ProMemDetail/proManager_iframeAdd.html",
                           templates=templates)
