import json

import pytest

from court.users.models import User

def test_login(app, requests_mock):
  facebook_token = 'mocksodoesntmatter'
  facebook_url = 'https://graph.facebook.com/me?fields=id,first_name,last_name,email,picture.height(300).width(300)&access_token=' + facebook_token
  mocked_fb_resp = {
    "id": "102773437400251",
    "first_name": "Will",
    "last_name": "Occhinoberg",
    "email": "kfgzlneeuo_1541453454@fbnw.net",
    "picture": {
      "data": {
        "height": 320,
        "is_silhouette": True,
        "url": "https://platform-lookaside.fbsbx.com/platform/profilepic/?asid=102773437400251&height=300&width=300&ext=1544820162&hash=AeQxhrUl0nPxIQDA",
        "width": 320
      }
    }
  }
  court_jwt = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTAyNzczNDM3NDAwMjUxLCJpc19hZG1pbiI6ZmFsc2V9.qVJ99o4cG1xsHAac2ztrBsyExST76pDlzhnJx9Nxt0s'
  requests_mock.get(facebook_url, json=mocked_fb_resp)

  with app.app_context():
    # ensure the user is not in the db
    user = User.query.filter(User.id == '102773437400251').one_or_none()
    assert user is None

  with app.test_client() as client:
    params = { 'access_token': facebook_token }
    resp = client.post('/api/users', query_string=params)
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data['success']
    assert data['token'] == court_jwt
    assert data['user']['email'] == 'kfgzlneeuo_1541453454@fbnw.net'
    assert data['user']['id'] == '102773437400251'

    with app.app_context():
      # user should now be in db
      user = User.query.filter(User.id == '102773437400251').one_or_none()
      assert user is not None
    
    # ensure an already created user can login again
    resp = client.post('/api/users', query_string=params)
    data = json.loads(resp.data)
    assert resp.status_code == 200
    assert data['success']
    assert data['token'] == court_jwt
    assert data['user']['email'] == 'kfgzlneeuo_1541453454@fbnw.net'
    assert data['user']['id'] == '102773437400251'

def test_login_bad_token(app, requests_mock):
  facebook_token = 'mocksodoesntmatter'
  facebook_url = 'https://graph.facebook.com/me?fields=id,first_name,last_name,email,picture.height(300).width(300)&access_token=' + facebook_token
  mocked_fb_resp = {
    "error": {
        "message": "Error validating access token",
        "type": "OAuthException",
        "code": 190,
        "error_subcode": 463,
        "fbtrace_id": "BjLAceHW1lJ"
    }  
  }
  requests_mock.get(facebook_url, json=mocked_fb_resp, status_code=400)
  with app.test_client() as client:
    params = { 'access_token': facebook_token }
    resp = client.post('/api/users', query_string=params)
    data = json.loads(resp.data)
    assert resp.status_code == 401
    assert not data['success']
    assert data['error'] == 'Not authorized'