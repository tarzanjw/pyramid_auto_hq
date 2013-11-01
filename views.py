__author__ = 'tarzan'

from pyramid.view import view_config
from velruse.providers.google_oauth2 import GoogleAuthenticationComplete
from models import HQUser
from pyramid.httpexceptions import HTTPFound
from pyramid.security import remember
import json
from pyramid_auto_hq import AutoHQResource

def index_view(request):
    return {
        'models': AutoHQResource.children,
    }

@view_config(context=GoogleAuthenticationComplete,
             renderer='json')
def google_oauth2_login_complete_view(request):
    profile = request.context.profile
    #return profile
    r = {
        'email': profile['accounts'][0]['username'],
        'name': profile['displayName'],
    }
    user = HQUser.import_from_dict(r)
    headers = remember(request, user.id)
    return HTTPFound('/_/', headers=headers)