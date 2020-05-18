import json
import random
from bson import ObjectId
from flask_mail import Message
from threading import Thread
from flask import current_app, request, session
import datetime


def quarter_calc():
    today = datetime.date.today()
    quarter = (today.month-1) // 3 + 1
    if quarter == 1:
        cquarter = "第一季度"
    elif quarter == 2:
        cquarter = "第二季度"
    elif quarter == 3:
        cquarter = "第三季度"
    else:
        cquarter = "第四季度"
    return '{}-{}'.format(today.year, cquarter)


def gen_verify_num():
    a = random.randint(-20, 20)
    b = random.randint(0, 50)
    data = {'question': str(a) + ' + ' + str(b) + " = ?", 'answer': str(a + b)}
    return data


def gen_cache_key():
    return 'view//' + request.full_path


def vkmsg_validator(data, flag):
    # Information verification
    if data['department'] == '':
        return "请选择所属部门", "danger"
    elif data['project'] == '':
        return "请选择项目名称", "danger"
    elif data['manager'] == '':
        return "请选择项目经理", "danger"
    else:
        if flag == "vkreport":  # 校验周报信息
            if data['schedule'] == '':
                return "请选择项目完成度", "danger"
            elif data['lastPlan'] == '':
                return "请填写上周计划", "danger"
            elif data['thisWork'] == '':
                return "请填写本周工作", "danger"
            elif data['lastPlan'] == '':
                return "请填写下周安排", "danger"
            else:
                return "提交成功", "success"
        elif flag == "qplan":  # 校验季度计划
            if data['quarter'] == '':
                return "请选择所属季度", 'danger'
            elif data['qplan'] == '':
                return "请填写季度计划的内容", "danger"
            elif data['checker2'] == '':
                return "请输入第一验收人", "danger"
            elif data['checker2'] == '':
                return "请输入第二验收人", "danger"
            else:
                return "提交成功", "success"
        else:
            return "校验错误", "danger"


def information_completion(current_user):
    role = current_user.role
    if role in [1, 2, 5]:
        if current_user.department == "":
            return 0
        else:
            return 1
    else:
        return 1


def information_completion(current_user):
    if current_user.role == 1 and current_user.department == None:
        return False
    elif current_user.role == 2 and current_user.department == None:
        return False
    elif current_user.role == 5 and current_user.department == None:
        return False
    else:
        return True


def virtualName():
    playnames = ['李瑞宝', '许有庆']
    return random.choice(playnames)
