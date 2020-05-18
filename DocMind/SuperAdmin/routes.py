from flask_mail import Message

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user, login_required, logout_user

from flask import Blueprint

from DocMind.models import *

import DocMind.config.DocTemplate as DocTemplate
from DocMind import db

from DocMind.SuperAdmin.time_task.weekreport_template import weekly_report_template
from DocMind.SuperAdmin.time_task.quarter_plan_template import quarter_plan_template

from DocMind import app, mail

import os

SuperAdmin = Blueprint("SuperAdmin", __name__)


@SuperAdmin.route('/admin', methods=['POST', 'GET'])
def admin():
    if current_user.is_authenticated and current_username == 'admin_docmind':
        return redirect(url_for('SuperAdmin.noticeManager'))
    elif current_user.is_authenticated:
        logout_user()
        return redirect(url_for('User.login'))
    else:
        return redirect(url_for('User.login'))


@SuperAdmin.route('/noticeManager', methods=['POST', 'GET'])
@login_required
def noticeManager():
    if current_user.username != "admin_docmind":
        abort(404)
    ranks = DocTemplate.notice_type()
    return render_template('SuperAdmin/notice.html', ranks=ranks)


@SuperAdmin.route('/userManager', methods=['POST', 'GET'])
@login_required
def userManager():
    if current_user.username != "admin_docmind":
        abort(404)
    return render_template('SuperAdmin/user.html')


@SuperAdmin.route('/dataManager', methods=['POST', 'GET'])
@login_required
def dataManager():
    if current_user.username != "admin_docmind":
        abort(404)
    return render_template('SuperAdmin/data.html')


@SuperAdmin.route('/communityManager', methods=['POST', 'GET'])
@login_required
def communityManager():
    if current_user.username != "admin_docmind":
        abort(404)
    return render_template('SuperAdmin/community.html')


@SuperAdmin.route('/superadmin_query/<flag>', methods=['POST', 'GET'])
@login_required
def superadmin_query(flag):
    if current_user.username != "admin_docmind":
        abort(404)
    if flag == 'notice_query':
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = NoticeDB.query.order_by(NoticeDB.time.desc()).all()
        datas = []
        for data in querydata:
            data = data.to_dict()
            data['time'] = data['time'].strftime('%Y-%m-%d-%H')
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == 'notice_insert':
        user = 'SuperAdmin'
        title = request.args.get('title')
        content = request.args.get('content')
        rank = request.args.get('rank')
        notice = NoticeDB(title=title, content=content, rank=rank, poster=user)
        db.session.add(notice)
        db.session.commit()
        return redirect(url_for('SuperAdmin.noticeManager'))
    elif flag == 'notice_del':
        id = request.form.get('id')
        data = NoticeDB.query.filter_by(id=int(id)).first()
        db.session.delete(data)
        db.session.commit()
        return {'code': 0}
    elif flag == 'user_query':
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = UserDB.query.order_by(UserDB.time.desc()).all()
        datas = []
        for data in querydata:
            data = data.to_dict()
            data['time'] = data['time'].strftime('%Y-%m-%d-%H')
            data['state'] = '已审核' if data['flag'] == 1 else '未审核'
            if data['role'] == 1:
                data['role'] = '项目负责人'
            elif data['role'] == 2:
                data['role'] = '部门总监'
            elif data['role'] == 3:
                data['role'] = '人事经理'
            elif data['role'] == 4:
                data['role'] = '研发经理'
            else:
                data['role'] = '技术负责人'
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == 'user_verify':
        id = request.form.get('id')
        data = UserDB.query.filter_by(id=int(id)).first()
        data.flag = 1
        db.session.commit()
        backdata = {"code": 0}
        return backdata
    elif flag == "qplan_query":
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = Qplan.query.order_by(Qplan.time.desc()).all()
        datas = []
        for data in querydata:
            data = data.to_dict()
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == "qplan_time_value":
        start = request.form.get('start')
        end = request.form.get('end')
        # Set deadline
        # Call modules
        return {'code': 0}
    elif flag == "weekreport_query":
        if request.method == 'GET':
            page = int(request.args["page"])
            limit = int(request.args["limit"])
            querydata = Vkreport.query.order_by(Vkreport.time.desc()).all()
            datas = []
            for data in querydata:
                data.time = data.time.strftime('%Y-%m-%d %H:%M:%S')
                data = data.to_dict()
                datas.append(data)
            data_ = datas[(page-1)*limit: page * limit]
            backdata = {"code": 0, "msg": "",
                        "count": len(datas), "data": data_}
            return backdata
        if request.method == 'POST':
            time_start = request.form.get('start')
            time_end = request.form.get('end')
            time_start = time_start + ' ' + '0:0:0'
            time_end = time_end + ' ' + '23:59:59'
            datas = []
            querydata = Vkreport.query.filter(Vkreport.time >= time_start).filter(
                Vkreport.time <= time_end).all()
            for data in querydata:
                data.time = data.time.strftime('%Y-%m-%d %H:%M:%S')
                data = data.to_dict()
                datas.append(data)
            backdata = {"code": 0, "msg": "",
                        "count": len(datas), "data": datas}
            return backdata

    elif flag == "weekreport_time_value":
        id = request.form.get('value')  # str
        # Set deadline
        # Call modules
        return {'code': 0}
    elif flag == "overcalc_query":
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = Project.query.order_by(Project.time.desc()).all()
        datas = []
        for data in querydata:
            data.time = data.time.strftime('%Y-%m-%d %H:%M:%S')
            data = data.to_dict()
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == "Oday_time_value":
        id = request.form.get('value')  # str
        # Set deadline
        # Call modules
        return {'code': 0}
    elif flag == "pro_query":
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = Project.query.order_by(Project.time.desc()).all()
        datas = []
        for data in querydata:
            data.time = data.time.strftime('%Y-%m-%d %H:%M:%S')
            data = data.to_dict()
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == "pro_time_value":
        id = request.form.get('value')  # str
        # Set deadline
        # Call modules
        return {'code': 0}
    elif flag == "emplo_query":
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = Staff.query.order_by(Staff.time.desc()).all()
        datas = []
        for data in querydata:
            data.time = data.time.strftime('%Y-%m-%d %H:%M:%S')
            data = data.to_dict()
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == "emplo_time_value":
        id = request.form.get('value')  # str
        # Set deadline
        # Call modules
        return {'code': 0}
    elif flag == "depart_query":
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = Performance.query.order_by(Performance.time.desc()).all()
        datas = []
        for data in querydata:
            data.time = data.time.strftime('%Y-%m-%d %H:%M:%S')
            data = data.to_dict()
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == "depart_time_value":
        id = request.form.get('value')  # str
        # Set deadline
        # Call modules
        return {'code': 0}
    elif flag == "team_query":
        page = int(request.args["page"])
        limit = int(request.args["limit"])
        querydata = Discipline.query.order_by(Discipline.time.desc()).all()
        datas = []
        for data in querydata:
            data.time = data.time.strftime('%Y-%m-%d %H:%M:%S')
            data = data.to_dict()
            datas.append(data)
        data_ = datas[(page-1)*limit: page * limit]
        backdata = {"code": 0, "msg": "", "count": len(datas), "data": data_}
        return backdata
    elif flag == "team_time_value":
        id = request.form.get('value')  # str
        # Set deadline
        # Call modules
        return {'code': 0}


@SuperAdmin.route('/quater_plan_time_post', methods=['POST', 'GET'])
@login_required
def quater_plan_time_post():
    if current_user.username != "admin_docmind":
        abort(404)
    time_start = request.form.get('start')
    time_end = request.form.get('end')
    year = time_end.split('-')[0]
    month = time_end.split('-')[1]
    quarter = (int(month)-1) // 3 + 1
    if quarter == 1:
        quarter = year+'-第一季度'
    elif quarter == 2:
        quarter = year+'-第二季度'
    elif quarter == '3':
        quarter = year+'-第三季度'
    else:
        quarter = year+'-第四季度'
    doc_template = quarter_plan_template(quarter)
    # doc_template=weekly_report_template(time_start,time_end)
    filepath = os.path.join(os.getcwd(), doc_template)
    send_quarter_plan_email(filepath)
    return {'time': time_end}


def send_quarter_plan_email(doc_template):
    msg = Message('北京研发中心季度计划汇总', sender='wave_dss@163.com',
                  recipients=['soheyi@163.com'])
    msg.body = '各位领导好：\n 附件为本季度各部门季度计划汇总，请及时查收！:\n \n\n\n  ————————————————————如果您非本邮件目标接收人，请忽略此份邮件，顺颂时祺————————————————————'
    with app.open_resource(doc_template) as fp:
        msg.attach(filename=os.path.basename(doc_template),
                   content_type='application/octet-stream', data=fp.read())
    mail.send(msg)


@SuperAdmin.route('/week_plan_time_post', methods=['POST', 'GET'])
@login_required
def week_plan_time_post():
    if current_user.username != "admin_docmind":
        abort(404)
    time_start = request.form.get('start')
    time_end = request.form.get('end')
    doc_template = weekly_report_template(time_start, time_end)
    if doc_template == None:
        return None
    filepath = os.path.join(os.getcwd(), doc_template)
    send_week_plan_email(filepath)
    return {'time': time_end}


def send_week_plan_email(doc_template):
    msg = Message('北京研发中心周报汇总', sender='wave_dss@163.com',
                  recipients=['soheyi@163.com'])
    msg.body = '各位领导好：\n 附件为本季度各部门本周周报汇总，请及时查收！:\n \n\n\n  ————————————————————如果您非本邮件目标接收人，请忽略此份邮件，顺颂时祺————————————————————'
    with app.open_resource(doc_template) as fp:
        msg.attach(filename=os.path.basename(doc_template),
                   content_type='application/octet-stream', data=fp.read())
    mail.send(msg)
