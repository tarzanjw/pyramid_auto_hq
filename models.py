__author__ = 'tarzan'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, types
from datetime import datetime
from pyramid.security import Everyone, Authenticated, authenticated_userid

Base = declarative_base()

class HQUser(Base):
    __tablename__ = 'hq_user'

    GROUP_SUPER_SAIYAN = 'g.SuperSaiyan'
    GROUP_ADMIN = 'g.Admin'
    GROUP_MODERATOR = 'g.Moderator'

    GROUPS = [
        GROUP_SUPER_SAIYAN,
        GROUP_ADMIN,
        GROUP_MODERATOR,
    ]

    id = Column(types.Integer, primary_key=True, autoincrement=True)
    name = Column(types.VARCHAR(length=255), nullable=False)
    email = Column(types.VARCHAR(length=255))
    avatar = Column(types.Text())
    last_modified_time = Column(types.DateTime, nullable=False,
                                default=datetime.now, onupdate=datetime.now)
    groups = Column(types.Text())

    @property
    def principals(self):
        groups = self.groups
        if not groups:
            groups = ''
        if not isinstance(groups, str):
            groups = groups.encode('utf-8')
        groups = groups.split(',')
        return set([Everyone, Authenticated] + groups)

    def merge_from_dict(self, dict):
        if 'name' not in dict:
            dict.setdefault('first_name', '')
            dict.setdefault('last_name', '')
            dict['name'] = ' '.join(
                [dict.get('first_name', ''), dict.get('last_name', '')])
        for c in self.__table__.columns:
            attr_name = c.name
            if not attr_name in dict:
                continue
            new_value = dict[attr_name]
            if new_value:
                setattr(self, attr_name, new_value)

    @classmethod
    def import_from_dict(cls, dict):
        assert 'email' in dict, "Unknow email from dict %s" % dict
        obj = cls.get_by_email(dict['email'])
        if obj is None:
            from pyramid_auto_hq import DBSession
            obj = cls()
            obj.merge_from_dict(dict)
            DBSession.add(obj)
            DBSession.flush()
        else:
            obj.merge_from_dict(dict)
        obj.id = int(obj.id)

        return obj

    @classmethod
    def get_by_email(cls, email):
        if not email:
            return None
        from pyramid_auto_hq import DBSession
        return DBSession.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_id(cls, id):
        if not id:
            return None
        from pyramid_auto_hq import DBSession
        return DBSession.query(cls).get(id)

def get_user_callback_for_auth_policy(user_id, request):
    user = HQUser.get_by_id(user_id)
    if user is None:
        return None
    request.__hq_user__ = user
    print user.principals
    return user.principals

def get_user_for_request(request):
    user_id = authenticated_userid(request)
    try:
        return request.__hq_user__
    except AttributeError:
        user = HQUser.get_by_id(user_id)
        request.__hq_user__ = user
    return request.__hq_user__