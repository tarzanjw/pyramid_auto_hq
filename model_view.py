#!coding=utf8
__author__ = 'tarzan'

from pyramid.decorator import reify
from pyramid_simpleform import Form
from pyramid.renderers import render_to_response
from lib.bootstrap_renderer import HorizontalFormRenderer
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from webhelpers.paginate import Page, PageURL_WebOb
from . import AutoHQResource, ModelResource
from sqlalchemy.orm.properties import RelationProperty, ColumnProperty
from sqlalchemy.orm.attributes import InstrumentedAttribute
import inspect

class ModelView(object):
    list__items_per_page = 50

    Object = None
    DBSession = None
    ObjectSchema = None
    ForeignKeys = []
    Relations = []

    ResourceList = None
    Resource = None

    actions = {}

    @classmethod
    def default_actions(cls):
        return {
        'list': {
            'route_name': 'auto_hq',
            'context': cls.ResourceList,
            'attr': 'list',
            'renderer': 'auto_hq/list.mak',
            'permission': 'list',
        },
        'create': {
            'route_name': 'auto_hq',
            'context': cls.ResourceList,
            'name': 'create',
            'attr': 'create',
            'renderer': 'auto_hq/create.mak',
            'permission': 'create',
        },
        'detail': {
            'route_name': 'auto_hq',
            'context': cls.Resource,
            'attr': 'detail',
            'renderer': 'auto_hq/detail.mak',
            'permission': 'detail',
        },
        'update': {
            'route_name': 'auto_hq',
            'context': cls.Resource,
            'name': 'update',
            'attr': 'update',
            'renderer': 'auto_hq/update.mak',
            'permission': 'update',
        },
        'delete': {
            'route_name': 'auto_hq',
            'context': cls.Resource,
            'name': 'delete',
            'attr': 'delete',
            'renderer': 'auto_hq/update.mak',
            'permission': 'delete',
        },
    }

    @property
    def object_name(self):
        return self.Object.__class__.__name__

    @property
    def breadcrumbs(self):
        r = self.request.context
        if self.request.view_name:
            entries = [{
                'label': str(r),
                'url': self.request.resource_url(r),
            }, self.request.view_name]
        else:
            entries = [str(r), ]
        while r and not isinstance(r, AutoHQResource):
            r = r.__parent__
            entries.insert(0, {
                'label': str(r),
                'url': self.request.resource_url(r),
            })

        return entries

    def __init__(self, request):
        self.request = request

    def __call__(self, request):
        self.request = request
        return self

    @property
    def obj_attr_names(self):
        attr_names = dir(self.Object)
        c2a = {}
        for name in attr_names:
            attr = getattr(self.Object, name)
            if not isinstance(attr, InstrumentedAttribute):
                continue
            p = attr.property
            if not isinstance(p, ColumnProperty):
                continue
            c2a[p.expression.name] = name
        col_names = [c.name for c in self.Object.__table__.columns]
        return map(c2a.__getitem__, col_names)

    def _get_object(self):
        if not isinstance(self.request.context, self.Resource):
            return None

        o = self.DBSession.query(self.Object).get(self.request.context.__name__)
        if o is None:
            raise HTTPNotFound("%s #%d does not exist" % (self.Object.__class__, id))
        return o

    @property
    def list_attr_names(self):
        return self.obj_attr_names

    @property
    def detail_attr_names(self):
        return self.obj_attr_names

    @reify
    def current_object(self):
        return self._get_object()

    @property
    def object_name(self):
        return self.Object.__name__

    @property
    def commands(self):
        req = self.request
        cxt = req.context
        commands = []
        obj_cxt = isinstance(cxt, self.Resource)
        if not obj_cxt:
            list_rs = cxt
        else:
            list_rs = cxt.__parent__

        if 'list' in self.actions:
            commands.append({'label': 'View List',
                             'url': req.resource_url(list_rs),
                             'icon': 'list'})
        if 'create' in self.actions:
            commands.append({'label': 'Create New',
                             'url': req.resource_url(list_rs, 'create'),
                             'icon': 'plus'})
        if obj_cxt and ('update' in self.actions):
            commands.append({'label': 'Update',
                             'url': req.resource_url(cxt, 'update'),
                             'icon': 'edit'})
        if obj_cxt and ('detail' in self.actions):
            commands.append({'label': 'View Detail',
                             'url': req.resource_url(cxt),
                             'icon': 'eye-open'})

        return commands

    @staticmethod
    def get_foreign_key_column(model, fk_model):
        fk_model_id_column = "%s.id" % fk_model.__tablename__
        for attr_name in dir(model):
            attr = getattr(model, attr_name)
            if isinstance(attr, InstrumentedAttribute):
                try:
                    fks = attr.foreign_keys
                except AttributeError:
                    fks = ()
                    pass
                for fk in fks:
                    if str(fk.column) == fk_model_id_column:
                        return attr_name

    @property
    def foreign_keys(self):
        _fks = []
        model = self.Object
        for attr_name in dir(model):
            attr = getattr(model, attr_name)
            if isinstance(attr, InstrumentedAttribute):
                p = attr.property
                if isinstance(p, RelationProperty):
                    if not p.uselist:
                        _fks.append(attr_name)
        return _fks

    @property
    def relations(self):
        _rels = []
        model = self.Object
        for attr_name in dir(model):
            attr = getattr(self.Object, attr_name)
            if isinstance(attr, InstrumentedAttribute):
                p = attr.property
                if isinstance(p, RelationProperty):
                    if p.uselist:
                        rel_model = p.argument() if inspect.isroutine(p.argument) \
                            else p.argument

                        fk_column = ModelView.get_foreign_key_column(rel_model, model)
                        if fk_column:
                            _rels.append((
                                attr_name,
                                rel_model,
                                fk_column,
                            ))
        return _rels

    def list(self):
        cur_page = int(self.request.params.get("page", 1))
        objs = self.DBSession.query(self.Object)
        attr_names = self.obj_attr_names

        for name, value in self.request.params.mixed().iteritems():
            if name in attr_names:
                objs = objs.filter(getattr(self.Object, name).like("%%%s%%" % value))

        from sqlalchemy import func
        objs = objs.order_by(self.Object.id.desc())
        item_count = self.DBSession.query(func.count(self.Object.id))
        for name, value in self.request.params.mixed().iteritems():
            if name in attr_names:
                item_count = item_count.filter(getattr(self.Object, name).like("%%%s%%" % value))
        item_count = item_count.scalar()

        page = Page(objs, page=cur_page,
                    item_count=item_count,
                    items_per_page=self.list__items_per_page,
                    url=PageURL_WebOb(self.request)
                    )

        return {
            "page": page,
            "view": self,
        }

    def detail(self):
        return {
            "obj": self._get_object(),
            "view": self,
        }

    def create(self):
        if self.ObjectSchema is None:
            return self.no_schema()
        schema = self.ObjectSchema()
        default_values = schema.__default_values__ \
            if hasattr(schema, '__default_values__') else None
        form = Form(request=self.request, schema=schema,
                    defaults=default_values,
                    variable_decode=True)

        if 'submit' in self.request.POST and form.validate():
            obj = self.Object()
            form.bind(obj)
            self.DBSession.add(obj)
            self.DBSession.flush()
            obj_cxt = self.request.context[obj.id]
            self.request.session.flash('%s #%s was created sucessfully.' % (self.object_name, obj))
            return HTTPFound(self.request.resource_url(obj_cxt))

        return {
            "view": self,
            "form_renderer": HorizontalFormRenderer(form),
        }

    def update(self):
        if self.ObjectSchema is None:
            return self.no_schema()
        schema = self.ObjectSchema()
        obj = self._get_object()
        default_values = schema.__default_values__ \
            if hasattr(schema, '__default_values__') else None
        form = Form(request=self.request, schema=schema,
                    obj=obj, defaults=default_values, state=obj,
                    variable_decode=True)

        if 'submit' in self.request.POST and form.validate():
            form.bind(obj)
            self.DBSession.merge(obj)
            self.DBSession.flush()
            obj_cxt = self.request.context
            self.request.session.flash('%s #%s was updated sucessfully.' % (self.object_name, obj))
            return HTTPFound(self.request.resource_url(obj_cxt))

        return {
            "view": self,
            "form_renderer": HorizontalFormRenderer(form),
        }

    def delete(self):
        obj = self._get_object()
        self.DBSession.delete(obj)
        self.DBSession.flush()
        self.request.session.flash('%s #%s was history!' % (self.object_name, self.request.context.__name__))
        return HTTPFound(self.request.resource_url(self.request.context.__parent__))

    def no_schema(self):
        return render_to_response('auto_hq/no_schema.mak', {
            'view': self,
        }, self.request)