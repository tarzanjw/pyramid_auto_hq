# coding=utf-8
__author__ = 'Tarzan'

import re
import importlib
from pyramid.url import urlencode


ROOT_URL = None
DBSession = None

class AutoHQResource(object):
    __parent__ = None
    __name__ = None

    children = {}

    def __init__(self, request):
        self.request = request
        # self.__name__ = ROOT_URL.rstrip('/')

    def __getitem__(self, key):
        if not isinstance(key, basestring):
            for k, x in self.children.iteritems():
                if x['model'] is key:
                    key = k
                    break
        if key in self.children:
            cfg = self.children[key]
            return cfg['resource'](cfg['model'], self, key)
        raise KeyError

    def __str__(self):
        return 'AutoHQ'

    def __resource_url__(self, *args, **kwargs):
        return ROOT_URL

class ModelResource(object):
    __model__ = None
    __parent__ = None
    __name__ = None
    __object_resource__ = None

    def __init__(self, model, parent, name):
        self.__model__ = model
        self.__parent__ = parent
        self.__name__ = name

    def __resource_url__(self, *args, **kwargs):
        return model_url(self.__model__)

    def __getitem__(self, key):
        try:
            int(key)
            r = self.__object_resource__()
            r.__name__ = str(key)
            r.__parent__ = self
            r.__model__ = self.__model__
        except ValueError:
            raise KeyError
        return r

    def __str__(self):
        return self.__model__.__name__ + ' list'

class ObjectResource(object):
    __model__ = None

    def __resource_url__(self, *args, **kwargs):
        return object_url(self.__model__, self.__name__)

    def __str__(self):
        return self.__model__.__name__ + '#' + self.__name__

def index_view(request):
    return {
        'models': AutoHQResource.children,
    }

import view_config

def register_model(config, model, path=None, actions=None):
    view_config.auto_view_config(config, model, path, actions)

def model_url(model, query=None):
    for urlkey, cfg in AutoHQResource.children.iteritems():
        if cfg['model'] is model:
            queries = ('?' + urlencode(query)) if query else ''
            return ROOT_URL + urlkey + '/' + queries
    raise KeyError('Model %s has not been registered in AutoHQ' % model)

def object_url(obj, id_value=None):
    if isinstance(obj, type):
        model = obj
        assert id_value is not None
    else:
        model = obj.__class__
        id_value = obj.id
    murl = model_url(model)
    return '%s%s/' % (murl, id_value)

def includeme(config):
    global ROOT_URL
    global DBSession
    settings = config.registry.settings
    ROOT_URL = settings.get('auto_hq.root_url')
    _vroot = settings.get('auto_hq.virtual_root', '')
    if _vroot and ROOT_URL.startswith(_vroot):
        ROOT_URL = ROOT_URL[len(_vroot):]

    dbsession_path = settings.get('auto_hq.dbsession')
    _module, _var = dbsession_path.rsplit('.', 1)
    _module = importlib.import_module(_module, package=None)
    DBSession = getattr(_module, _var)

    models_list = settings.get('auto_hq.models', '')
    models_list = [m.strip() for m in re.split(r'[^[\w_\.#,]+', models_list)]
    models_list = filter(bool, models_list)
    for model in models_list:
        parts = model.split('#')
        if len(parts) > 1:
            model, action_names = parts
            actions = {n.strip():{} for n in action_names.split(',')}
        else:
            actions = None
        module_name, model_name = model.rsplit('.', 1)
        module = importlib.import_module(module_name, package=None)
        model = getattr(module, model_name)
        register_model(config, model, actions=actions)

    print ROOT_URL
    config.add_route('auto_hq',
                     ROOT_URL.rstrip('/') + '/*traverse',
                     factory=AutoHQResource)
    config.add_view(index_view, context=AutoHQResource,
                    route_name='auto_hq',
                    renderer='auto_hq/index.mak')

from model_view import ModelView
from view_config import _auto_object_resource as get_object_resource
from view_config import _auto_model_resource as get_model_resource
from model_view_config import model_view_config