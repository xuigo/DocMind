import json
import random
import os
from DocMind import db
from DocMind.models import UserDB


def templates_index():
    DocTemplates = []
    # quarter plan
    template1 = {}
    template1['bg_image'] = "static/images/fly.jpg"
    template1['alt'] = "季度计划"
    template1['href'] = "QuarterPlan.qplan"
    template1['desc'] = "以各项目为最小单元，包含部门、项目名称、负责人、子任务、验收人一、验收人二 等内容的极简模板。"
    template1['headimg'] = "static/images/docmind.jpg"
    template1['time'] = "2020-03-21"
    template1['uptimes'] = "666"
    # weekly report
    template2 = {}
    template2['bg_image'] = "static/images/fly.jpg"
    template2['alt'] = "周报"
    template2['href'] = 'WeeklyReport.vkreport'
    template2['desc'] = "以各项目为最小单元，包含部门、项目名称、负责人、上周计划、本周工作、下周安排、项目进度 等内容的极简模板。"
    template2['headimg'] = "static/images/docmind.jpg"
    template2['time'] = "2020-03-21"
    template2['uptimes'] = "666"
    # reputation of projects
    template5 = {}
    template5['bg_image'] = "static/images/fly.jpg"
    template5['alt'] = "项目评审"
    template5['href'] = "ProDetail.procheck"
    template5['desc'] = "各评审人员，秉持客观公正态度，对参加评审的项目进行打分，均分80。"
    template5['headimg'] = "static/images/docmind.jpg"
    template5['time'] = "2020-03-21"
    template5['uptimes'] = "666"
    # Overtime statistics
    template4 = {}
    template4['bg_image'] = "static/images/fly.jpg"
    template4['alt'] = "加班统计"
    template4['href'] = "ProMemDetail.overcalc"
    template4['desc'] = "以各项目为最小单元，统计核算本季度项目加班情况，包含成员加班比例，投入比例。"
    template4['headimg'] = "static/images/docmind.jpg"
    template4['time'] = "2020-03-21"
    template4['uptimes'] = "666"
    # Employee evaluation
    template6 = {}
    template6['bg_image'] = "static/images/fly.jpg"
    template6['alt'] = "员工考评"
    template6['href'] = "DepartMemDetail.staff"
    template6['desc'] = "各部门总监，根据本部门各项目完成情况，对本部门所有人员进行考评。"
    template6['headimg'] = "static/images/docmind.jpg"
    template6['time'] = "2020-03-21"
    template6['uptimes'] = "666"
    # Department Assessment
    template7 = {}
    template7['bg_image'] = "static/images/fly.jpg"
    template7['alt'] = "部门考评"
    template7['href'] = "DepartAchieveDetail.departmentcheck"
    template7['desc'] = "由研发经理，综合考评个部门季度计划完成情况。"
    template7['headimg'] = "static/images/docmind.jpg"
    template7['time'] = "2020-03-21"
    template7['uptimes'] = "666"
    # Team building
    template8 = {}
    template8['bg_image'] = "static/images/fly.jpg"
    template8['alt'] = "团队建设"
    template8['href'] = "DepartDisciplineDetail.teamcheck"
    template8['desc'] = "由人事经理，综合考评个部门季度团队建设和纪律考勤。"
    template8['headimg'] = "static/images/docmind.jpg"
    template8['time'] = "2020-03-21"
    template8['uptimes'] = "666"

    DocTemplates.append(template1)
    DocTemplates.append(template2)
    DocTemplates.append(template4)
    DocTemplates.append(template5)
    DocTemplates.append(template6)
    DocTemplates.append(template7)
    DocTemplates.append(template8)
    return DocTemplates


def templates_vkreport():
    templates = {}
    quarters = ['2020-第一季度', '2020-第二季度', '2020-第三季度', '2020-第四季度']
    departments = os.environ.get('DEPARTMENT')
    projects = os.environ.get('PROJECTS')
    querydata = UserDB.query.filter().all()
    managers = list(set([data.name for data in querydata]))
    schedules = ['0%', '20%', '40%', '60%', '80%', '100%']
    templates['quarters'] = quarters
    templates['departments'] = departments
    templates['projects'] = projects
    templates['managers'] = managers
    templates['schedules'] = schedules
    return templates


def notice_type():
    return ['通知', '制度', '建议']
