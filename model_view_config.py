#!coding=utf8
__author__ = 'tarzan'

from . import ModelResource, DBSession
import venusian
from view_config import auto_view_config

class model_view_config(object):
    """
    Cho phép quản lý tự động một model trên hệ thống.
    """
    model = None
    path = None
    info = None
    schema = None
    actions = {}

    def __init__(self, model, path=None, actions=None):
        assert model, "You have to specify model"
        self.model = model
        self.path = path
        self.actions = actions

    def view_config(self, scanner, name, wrapped):
        # add registerd class to HQ's context tree
        auto_view_config(scanner.config,
                         self.model,
                         self.path,
                         self.actions,
                         wrapped)

    def register_view(self, config, cls):
        cls.DBSession = DBSession
        cls.Object = self.model
        cls.Resource = self.model
        cls.ResourceList = ModelResource
        cls.ObjectSchema = self.schema

        for a, cfg in self.actions.iteritems():
            config.add_view(view=cls, **cfg)

    def __call__(self, wrapped):
        self.info = venusian.attach(wrapped, self.view_config)
        return wrapped