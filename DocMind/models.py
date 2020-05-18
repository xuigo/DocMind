from datetime import datetime
from DocMind import db, login_manager
from flask_login import UserMixin
import json
import random
from DocMind.config.utils import quarter_calc, virtualName

from DocMind import app


from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@login_manager.user_loader
def load_user(user_id):
    return UserDB.query.get(int(user_id))


def to_json(all_vendors):
    v = [ven.dobule_to_dict() for ven in all_vendors]
    return v


def dobule_to_dict(self):
    result = {}
    for key in self.__mapper__.c.keys():
        if getattr(self, key) is not None:
            result[key] = str(getattr(self, key))
        else:
            result[key] = getattr(self, key)
    return result


class UserDB(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(64), unique=True, nullable=False)
    image = db.Column(db.String(120), nullable=False,
                      default='{}/{}/{}.png'.format('static', 'avater', random.randint(1, 19)))
    password = db.Column(db.String(64), nullable=False)
    role = db.Column(db.SmallInteger)
    sex = db.Column(db.String(10))
    department = db.Column(db.String(64))
    project = db.Column(db.String(64))
    sign = db.Column(db.String(120))
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    flag = db.Column(db.SmallInteger, default=0)

    def get_reset_token(self, expires_sec=600):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        user_id = s.loads(token)['user_id']
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return UserDB.query.get(user_id)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'UserDB:({}, {}, {}, {})'.format(self.username, self.email, self.image, self.role)


class Project(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    pname = db.Column(db.String(64), nullable=False)
    manager = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(64))
    schedule = db.Column(db.Integer, nullable=False, default=0)
    prate = db.Column(db.Integer, nullable=False, default=0)
    result = db.Column(db.Integer, nullable=False, default=0)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    submitor = db.Column(db.String(20))
    qplan = db.relationship("Qplan", backref="qplan", lazy=True)
    vkreport = db.relationship("Vkreport", backref="vkreport", lazy=True)
    oday = db.relationship("Oday", backref="oday", lazy=True)
    score = db.relationship("Score", backref="score", lazy=True)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'ProjectDB:({}, {}, {}, {})'.format(self.quarter, self.manager, self.pname, self.schedule)


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    pname = db.Column(db.String(64), nullable=False)
    manager = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(64))
    name = db.Column(db.String, nullable=False)
    result = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'ScoreDB:({}, {})'.format(self.name, self.result)


class Qplan(db.Model):
    __tablename__ = 'qplan'
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    pname = db.Column(db.String(64), nullable=False)
    manager = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(64))
    qplanContent = db.Column(db.Text, nullable=False)
    checker1 = db.Column(db.String(20), nullable=False)
    checker2 = db.Column(db.String(20), nullable=False)
    implementer = db.Column(db.String(20), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'QplanDB:({}, {}, {})'.format(self.checker1, self.checker2, self.implementer)


class Vkreport(db.Model):
    __tablename__ = 'vkreport'
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    pname = db.Column(db.String(64), nullable=False)
    manager = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(64))
    schedule = db.Column(db.String(20), unique=False, nullable=False)
    lastContent = db.Column(db.Text, nullable=False)
    thisContent = db.Column(db.Text, nullable=False)
    nextContent = db.Column(db.Text, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'VkreportDB:({})'.format(self.schedule)


class Oday(db.Model):
    __tablename__ = 'oday'
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    pname = db.Column(db.String(64), nullable=False)
    manager = db.Column(db.String(20), nullable=False)
    department = db.Column(db.String(64))
    member = db.Column(db.String(20), nullable=False)
    rate = db.Column(db.String(20), nullable=False, default=0)
    days = db.Column(db.String(20), nullable=False, default=0)
    score = db.Column(db.String(20), nullable=False, default=0)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey(
        'project.id'), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'OdayDB:({}, {}, {})'.format(self.member, self.rate, self.days)


class Staff(db.Model):
    __tablename__ = 'staff'
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    department = db.Column(db.String(64), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    project_score = db.Column(db.String(20), nullable=False, default=0)
    other_score = db.Column(db.String(20), nullable=False, default=0)
    note = db.Column(db.String(120))
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'StaffDB:({}, {}, {})'.format(self.name, self.project_score, self.other_score)


class Discipline(db.Model):
    __tablename__ = 'discipline'
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    department = db.Column(db.String(64), nullable=False)
    manager = db.Column(db.String(64), nullable=False)
    score = db.Column(db.String(64), nullable=False, default="0")
    note = db.Column(db.String(120))
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'DisciplineDB:({}, {}, {})'.format(self.quarter, self.department, self.score)


class Performance(db.Model):
    __tablename__ = 'performance'
    id = db.Column(db.Integer, primary_key=True)
    quarter = db.Column(db.String(64), nullable=False, default=quarter_calc())
    department = db.Column(db.String(64), nullable=False)
    manager = db.Column(db.String(64), nullable=False)
    score = db.Column(db.String(64), nullable=False, default="0")
    note = db.Column(db.String(120))
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'PerformanceDB:({}, {}, {})'.format(self.quarter, self.department, self.score)


class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), nullable=False)
    calss = db.Column(db.String(10), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(20), nullable=False)
    playname = db.Column(db.String(40), nullable=False, default=virtualName())
    top = db.Column(db.Integer, nullable=False)
    marrow = db.Column(db.Integer, nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'PerformanceDB:({}, {}, {})'.format(self.quarter, self.department, self.score)


class NoticeDB(db.Model):
    __tablename__ = 'noticeDB'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    rank = db.Column(db.String(64), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    poster = db.Column(db.String(64), nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return 'NoticeDB:({}, {}, {})'.format(self.title, self.poster, self.time)

