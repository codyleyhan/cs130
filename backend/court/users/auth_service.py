import jwt
import json
from flask import g, request
import requests
from functools import wraps

from court.database import db
from court.errors import AuthorizationError, ValidationError
from court.users.models import User, Profile

# TODO(codyleyhan): Need to add tons of try catches

class AuthService:
  def __init__(self, secret, user_store=User, db_conn=db):
    self.secret = secret
    self.user_store = user_store
    self.db = db_conn

  def login(self, access_token):
    if access_token.strip() == '':
      raise ValidationError()

    base_url = 'https://graph.facebook.com/me?fields={}&access_token={}'
    fields = [ 'id', 'first_name', 'last_name', 'email',
               'picture.height(300).width(300)' ]
    r = requests.get(base_url.format(','.join(fields), access_token))
    if r.status_code != 200:
      raise AuthorizationError()

    facebook_user_data = json.loads(r.text)

    user = self.user_store.query.filter(User.id == facebook_user_data['id']).one_or_none()
    if user is None: # user is new so insert into DB
      user = User()
      user.id = facebook_user_data['id']
      user.email = facebook_user_data['email']
      # TODO(codyleyhan) tons of exception handling
      self.db.session.add(user)
      self.db.session.commit()

    # TODO(anthonymirand): store user profile in database
    token_data = {
      'id': int(user.id),
      'is_admin': False
    }

    g.user_id = int(user.id)

    token = jwt.encode(token_data, self.secret, algorithms=['HS256'])

    return token, user

  def validate_token(self, token):
    try:
      data = jwt.decode(token, self.secret, algorithms=['HS256'])
      g.user_id = data['id']
    except Exception as e:
      raise AuthorizationError()

  def get_current_user(self):
    if 'user' in g:
      return g.user

    user_id = self.get_current_user_id()
    if user_id is not None:
      user = self.user_store.query.get(user_id)
      g.user = user
      return user

    return None

  def get_current_user_id(self):
    if 'user_id' in g:
      return g.user_id

    return None

  def login_required(self, f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in g:
            raise AuthorizationError()
        return f(*args, **kwargs)
    return decorated_function



