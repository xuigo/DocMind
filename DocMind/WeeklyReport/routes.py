from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_required
from flask import Blueprint, abort

import DocMind.config.utils as utils
from DocMind.models import *
from DocMind import db
import DocMind.config.DocTemplate as DocTemplates

WeeklyReport = Blueprint("WeeklyReport", __name__)


@WeeklyReport.route('/vkreport', methods=['POST', 'GET'])
def vkreport():
    if current_user.is_authenticated:

        flag = utils.information_completion(current_user)
        check_flag = current_user.flag
        if flag and check_flag:
            if current_user.role == 1:
                templates = DocTemplates.templates_vkreport()
                querydata = Project.query.filter_by(manager=current_user.username,
                                                    quarter=utils.quarter_calc()).first()
                if querydata == None:
                    flash("部门总监暂未创建由您负责的项目，所以暂时还不能访问", 'danger')
                    return redirect(url_for('main.index'))
                else:
                    data = querydata.to_dict()
                    return render_template('WeeklyReport/proManager.html', templates=templates, msg=data)
            elif current_user.role == 2:
                return render_template('WeeklyReport/departDirector.html')
            elif current_user.role == 3 or current_user.role == 4:
                return render_template('WeeklyReport/headManager.html')
            elif current_user.role == 5:
                return render_template('WeeklyReport/techDirector.html')
        elif flag:
            flash('请等待或者联系管理员进行信息审核', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('请首先完善个人信息，实名认证，绑定部门', 'danger')
            return redirect(url_for('User.setting'))
    else:
        flash("权限管理页面,请登录后访问！", 'info')
        return redirect(url_for('User.login'))


@WeeklyReport.route('/vkreport_query/<flag>')
def vkreport_query(flag):
    if flag == "director" or flag == "techdirector":
        querydata = Vkreport.query.filter_by(
            department=current_user.department).all()
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data = []
        for data_ in querydata:
            data_temp = data_.to_dict()
            data_temp['time'] = data_temp['time'].strftime("%Y-%m-%d %H:%M:%S")
            data.append(data_temp)
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    elif flag == "manager":
        querydata = Vkreport.query.filter().all()
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data = []
        for data_ in querydata:
            data.append(data_.to_dict())
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    else:
        abort(404)


@WeeklyReport.route('/weeklyreport/<flag>')
@login_required
def weeklyreport(flag):
    if flag == "submit":
        templates = DocTemplates.templates_vkreport()
        data = {}
        data['schedule'] = request.args.get('quiz4')
        data['lastPlan'] = request.args.get('lastPlan')
        data['thisWork'] = request.args.get('thisWeek')
        data['nextPlan'] = request.args.get('nextPlan')
        project = Project.query.filter_by(manager=current_user.username,
                                          quarter=utils.quarter_calc()).first()
        project.schedule = data['schedule']
        db.session.commit()
        vkinformation = Vkreport(quarter=project.quarter,
                                 pname=project.pname,
                                 department=project.department,
                                 manager=project.manager,
                                 schedule=data['schedule'],
                                 lastContent=data['lastPlan'],
                                 thisContent=data['thisWork'],
                                 nextContent=data['nextPlan'],
                                 project_id=project.id)
        db.session.add(vkinformation)
        db.session.commit()
        return redirect(url_for('WeeklyReport.vkreport'))
    elif flag == "query":
        project_id = Project.query.filter_by(manager=current_user.username,
                                             quarter=utils.quarter_calc()).first().id
        querydata = Vkreport.query.filter_by(project_id=project_id).all()
        data = []
        if querydata != None:
            for msg in querydata:
                msg = msg.to_dict()
                msg['time'] = msg['time'].strftime("%Y-%m-%d %H:%M:%S")
                data.append(msg)
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    else:
        abort(404)


@WeeklyReport.route('/weeklyreportdelete', methods=['POST', 'GET'])
@login_required
def weeklyreportdelete():
    delid = int(request.get_data('id').decode('utf-8').split('id=')[-1])
    querydata = Vkreport.query.filter_by(id=delid).first()
    db.session.delete(querydata)
    db.session.commit()
    backdata = {"code": 0, "msg": "删除"}
    return backdata


@WeeklyReport.route('/weeklyreportiframe_read')
@login_required
def weeklyreportiframe_read():
    templates = DocTemplates.templates_vkreport()
    return render_template("WeeklyReport/iframeRead.html", templates=templates)


@WeeklyReport.route('/vkreport_iframe')
@login_required
def vkreport_iframe():
    templates = DocTemplates.templates_vkreport()
    return render_template("WeeklyReport/iframeDetail.html", templates=templates)


@WeeklyReport.route('/v_iframe_msg')
@login_required
def v_iframe_msg():
    id_ = request.args.get('flag')
    schedule = request.args.get('schedule')
    lastPlan = request.args.get('lastPlan')
    thisWeek = request.args.get('thisWeek')
    nextPlan = request.args.get('nextPlan')
    querydata = Vkreport.query.filter_by(id=id_).first()
    querydata.schedule = schedule
    querydata.lastContent = lastPlan
    querydata.thisContent = thisWeek
    querydata.nextContent = nextPlan
    db.session.commit()
    project = Project.query.filter_by(id=querydata.project_id).first()
    project.schedule = schedule
    db.session.commit()
    return redirect(url_for('WeeklyReport.vkreport_iframe'))
