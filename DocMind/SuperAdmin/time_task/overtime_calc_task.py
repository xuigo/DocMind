from DocMind.models import *
from DocMind import db


def calc_overtime_rate(quarter):
    result = {}
    querydata = Oday.query.filter_by(quarter=quarter).all()
    # data preprocess
    for data in querydata:
        if data.pname in result.keys():
            result[data.name].append((rate, days))
        else:
            result[data.name] = []
            result[data.name].append((rate, days))
    for key, value in result.items():
        score = 0
        for _value in value:
            score += _value
        score /= len(value)
        querydata = Project.query.filter_by(pname=key, quarter=quarter).first()
        if querydata is None:
            continue
        querydata.prate = score
        db.session.commit()
