from flask import render_template, url_for, redirect, request, flash, session
from flask_login import current_user, login_required
from flask import Blueprint, abort

import DocMind.config.utils as utils
from DocMind.models import *
from DocMind import db
import DocMind.config.DocTemplate as DocTemplates

import time
QuarterPlan = Blueprint("QuarterPlan", __name__)

@QuarterPlan.route('/qplan', methods=['POST', 'GET'])
def qplan():
    if current_user.is_authenticated:
        flag = utils.information_completion(current_user)
        check_flag = current_user.flag
        if flag and check_flag:
            temps = DocTemplates.templates_index()
            quarter = utils.quarter_calc()
            templates = DocTemplates.templates_vkreport()
            if current_user.role == 1:
                querydata = Project.query.filter_by(manager=current_user.username,
                                                    quarter=utils.quarter_calc()).first()
                if (querydata) != None:
                    data = querydata.to_dict()
                    return render_template('QuarterPlan/proManager.html', templates=templates, msg=data)
                else:
                    flash("请确认用户名是否正确，或部门总监暂未创建项目", 'info')
                    return redirect(url_for('main.index'))
            elif current_user.role == 2:
                return render_template('QuarterPlan/departDirector.html',
                                       templates=templates, quarter=quarter)
            elif current_user.role == 3 or current_user.role == 4:
                return render_template('QuarterPlan/headManager.html',
                                       templates=templates)
            elif current_user.role == 5:
                return render_template('QuarterPlan/techDirector.html',
                                       templates=templates, quarter=quarter)
            else:
                abort(404)
        elif flag:
            flash('请等待或者联系管理员进行信息审核', 'info')
            return redirect(url_for('main.index'))
        else:
            flash('请首先完善个人信息，实名认证，绑定部门', 'danger')
            return redirect(url_for('User.setting'))
    else:
        flash("权限管理模块,请登录后访问！", 'info')
        return redirect(url_for('User.login'))


@QuarterPlan.route('/qplan/query/<flag>')
def qplan_query(flag):
    if flag == "manager":
        querydata = Qplan.query.filter().all()
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data = []
        print('请求数据')
        for data_ in querydata:
            data_temp = data_.to_dict()
            data_temp['time'] = data_temp['time'].strftime("%Y-%m-%d %H:%M:%S")
            data.append(data_temp)
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    elif flag == "techdirector":
        if current_user.department == '':
            flash("请先绑定你的部门", 'danger')
            return redirect(url_for('User.setting'))
        querydata = Qplan.query.filter_by(
            department=current_user.department).all()
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data = []
        for data_ in querydata:
            data_temp = data_.to_dict()
            data_temp['time'] = data_temp['time'].strftime("%Y-%m-%d %H:%M:%S")
            data.append(data_temp)
        data_ = data[(page-1)*limit: page * limit]
        print(data_)
        print('-'*10)
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        return backdata
    else:
        abort(404)


@QuarterPlan.route('/qplan_iframe')
def qplan_iframe():
    templates = DocTemplates.templates_vkreport()
    return render_template('QuarterPlan/headManager_iframe.html', templates=templates)


@QuarterPlan.route('/quarter/<flag>', methods=['POST', 'GET'])  # 季度计划
@login_required
def quarter(flag):
    if flag == "submit":
        data = {}
        data['qplan'] = request.args.get('QPlan')
        data['checker1'] = request.args.get('quiz5')
        data['checker2'] = request.args.get('quiz6')
        data['implementer'] = request.args.get('quiz7')
        project = Project.query.filter_by(manager=current_user.username,
                                          quarter=utils.quarter_calc()).first()
        oday = Oday(quarter=project.quarter,
                    pname=project.pname,
                    manager=project.manager,
                    member=data['implementer'],
                    department=project.department,
                    project_id=project.id)

        db.session.add(oday)
        db.session.commit()
        db.create_all()
        qplandb = Qplan(quarter=project.quarter,
                        pname=project.pname,
                        manager=project.manager,
                        department=project.department,
                        qplanContent=data['qplan'],
                        checker1=data['checker1'],
                        checker2=data['checker2'],
                        implementer=data['implementer'],
                        project_id=project.id)
        db.session.add(qplandb)
        db.session.commit()
        flash("数据提交成功", 'success')
        return redirect(url_for('QuarterPlan.qplan'))
    elif flag == "query":
        project_id = Project.query.filter_by(manager=current_user.username,
                                             quarter=utils.quarter_calc()).first().id
        querydata = Qplan.query.filter_by(project_id=project_id).all()
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        data = []
        for msg in querydata:
            msg = msg.to_dict()
            data.append(msg)
        data_ = data[(page-1)*limit: page * limit]
        print(data_)
        print('-------------------------')
        backdata = {"code": 0, "msg": "", "count": len(data), "data": data_}
        print(backdata)
        return backdata
    elif flag == "delete":
        delid = int(request.get_data('id').decode('utf-8').split('id=')[-1])
        querydata = Qplan.query.filter_by(id=delid).first()
        db.session.delete(querydata)
        db.session.commit()
        project_id = Project.query.filter_by(manager=current_user.username,
                                             quarter=utils.quarter_calc()).first().id
        querydata = Qplan.query.filter_by(project_id=project_id).all()
        data = []
        for msg in querydata:
            msg = msg.to_json()
            data.append(msg)
        backdata = {"code": 0, "msg": "删除", "count": 1000, "data": data}
        return backdata
    else:
        abort(404)


@QuarterPlan.route('/prodirect/<flag>', methods=['POST', 'GET'])  # 部门总监安排季度任务
@login_required
def prodirect(flag):
    if flag == "submit":
        quarter = request.args.get('quiz1')
        department = request.args.get('quiz2')
        project = request.args.get('quiz3')
        manager = request.args.get('quiz4')
        projectdb = Project(quarter=utils.quarter_calc(),
                            department=department,
                            pname=project, manager=manager,
                            submitor=current_user.username)
        db.session.add(projectdb)
        db.session.commit()
        return redirect(url_for('QuarterPlan.qplan'))
    elif flag == "query":
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = Project.query.filter_by(
            submitor=current_user.username).all()
        data = []
        for msg in querydata:
            msg = msg.to_dict()
            data.append(msg)
        data_ = data[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(data),
                    "data": data_}
        print(backdata)
        return backdata
    elif flag == "delete":
        delid = int(request.get_data('id').decode('utf-8').split('id=')[-1])
        querydata = Project.query.filter_by(id=delid).first()
        db.session.delete(querydata)
        db.session.commit()
        querydata = Project.query.filter_by(
            submitor=current_user.username).all()
        data = []
        for msg in querydata:
            msg = msg.to_dict()
            data.append(msg)
        backdata = {"code": 0, "msg": "删除", "count": 1000, "data": data}
        return backdata
    else:
        abort(404)
