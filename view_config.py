# coding=utf-8
__author__ = 'tarzan'

from . import ModelResource, AutoHQResource, ObjectResource
from lib import text
from model_view import ModelView
from pyramid.security import Allow, ALL_PERMISSIONS
from pyramid_auto_hq.models import HQUser

def get_model_url_path(model):
    """
    Lấy đường dẫn trên URL cho 1 model
    :param model: model cần lấy đường dẫn
    :type model: class
    :rtype: int
    """
    try:
        return model.__hq_urlkey__
    except AttributeError:
        return text.camel_case_to_underscore(model.__name__)

def _context_match_path_predicate(path):
    def compare_function(context, request):
        list_cxt = context if isinstance(context, ModelResource) \
            else context.__parent__
        return list_cxt.__name__ == path
    return compare_function

def _build_actions(actions, defaults):
    if not actions:
        return defaults

    def fill_action_defaults(action, default):
        for k, v in default.iteritems():
            action.setdefault(k, v)

    if isinstance(actions, (list, tuple)):
        actions = {a:{} for a in actions}
    for name in actions:
        if name in defaults:
            fill_action_defaults(actions[name], defaults[name])
    return actions

_AUTO_CLASSES = {}

def _auto_model_view_cls(model):
    cls_name = model.__name__ + '_ModelView'
    if cls_name not in _AUTO_CLASSES:
        _AUTO_CLASSES[cls_name] = type(cls_name, (ModelView,), {})

    try:
        _AUTO_CLASSES[cls_name].__acl__ = model.__hq_acl__
    except AttributeError:
        _AUTO_CLASSES[cls_name].__acl__ = [
            (Allow, HQUser.GROUP_SUPER_SAIYAN, ALL_PERMISSIONS)
        ]

    return _AUTO_CLASSES[cls_name]

def _auto_model_resource(model, object_resource):
    cls_name = model.__name__ + '_ModelResource'
    if cls_name not in _AUTO_CLASSES:
        _AUTO_CLASSES[cls_name] = type(cls_name, (ModelResource,), {
            '__object_resource__': object_resource
        })

    try:
        _AUTO_CLASSES[cls_name].__acl__ = model.__hq_acl__
    except AttributeError:
        _AUTO_CLASSES[cls_name].__acl__ = [
            (Allow, HQUser.GROUP_SUPER_SAIYAN, ALL_PERMISSIONS)
        ]

    return _AUTO_CLASSES[cls_name]

def _auto_object_resource(model):
    cls_name = model.__name__ + '_ObjectResource'
    if cls_name not in _AUTO_CLASSES:
        _AUTO_CLASSES[cls_name] = type(cls_name, (ObjectResource, ), {})
    return _AUTO_CLASSES[cls_name]

def auto_view_config(config, model, path=None, actions=None, view_cls=None):
    if path is None:
        path = get_model_url_path(model)

    if view_cls is None:
        view_cls = _auto_model_view_cls(model)

    resource = _auto_object_resource(model)
    resource_list = _auto_model_resource(model, resource)

    AutoHQResource.children[path] = {
        'model': model,
        'resource': resource_list,
    }

    from . import DBSession
    view_cls.DBSession = DBSession
    view_cls.Object = model
    view_cls.ResourceList = resource_list
    view_cls.Resource = resource
    view_cls.ObjectSchema = getattr(model, '__hq_schema__') \
        if hasattr(model, '__hq_schema__') else None
    if view_cls.ObjectSchema:
        view_cls.ObjectSchema.allow_extra_fields = True
    actions = _build_actions(actions, view_cls.default_actions())
    view_cls.actions = actions

    for a, cfg in actions.iteritems():
        config.add_view(view=view_cls, **cfg)
