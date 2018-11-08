import jwt
import json
from flask import g, request
import requests

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

    base_url = 'https://graph.facebook.com/me?fields=id,first_name,last_name,email,picture&access_token={}'
    r = requests.get(base_url.format(access_token))
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
      'id': user.id,
      'is_admin': False
    }

    g.user_id = user.id

    token = jwt.encode(token_data, self.secret, algorithm='HS256')

    return token, user
  
  def get_current_user(self):
    if g.user is not None:
      return g.user
    
    user_id = self.get_current_user_id()
    if user_id is not None:
      user = self.user_store.query.get(g.user_id)
      g.user = user
      return user

    return None

  def get_current_user_id(self):
    if g.user_id is not None:
      return g.user_id
    elif request.headers.get('Authorization') is not None:
      g.user_id = request.headers.get('Authorization')
      return g.user_id

    return None


