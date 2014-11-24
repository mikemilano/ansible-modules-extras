#!/usr/bin/python
# -*- coding: utf-8 -*-

DOCUMENTATION = '''
---
module: hipchat
version_added: "1.2"
short_description: Send a message to hipchat
description:
   - Send a message to hipchat
options:
  token:
    description:
      - API token.
    required: true
  room:
    description:
      - ID or name of the room.
    required: true
  from:
    description:
      - Name the message will appear be sent from. max 15 characters. (V1 Only)
        Over 15, will be shorten.
    required: false
    default: Ansible
  msg:
    description:
      - The message body.
    required: true
    default: null
  color:
    description:
      - Background color for the message. Default is yellow.
    required: false
    default: yellow
    choices: [ "yellow", "red", "green", "purple", "gray", "random" ]
  msg_format:
    description:
      - message format. html or text. Default is text.
    required: false
    default: text
    choices: [ "text", "html" ]
  notify:
    description:
      - notify or not (change the tab color, play a sound, etc)
    required: false
    default: 'yes'
    choices: [ "yes", "no" ]
  validate_certs:
    description:
      - If C(no), SSL certificates will not be validated. This should only be used
        on personally controlled sites using self-signed certificates.
    required: false
    default: 'yes'
    choices: ['yes', 'no']
    version_added: 1.5.1
  version:
    description:
      - API version
    required: false
    default: 1
    choices: [ 1, 2 ]
  api:
    description:
      - API url if using a self-hosted hipchat server
    required: false
    default: 'https://api.hipchat.com/v1/rooms/message'
    version_added: 1.6.0


# informational: requirements for nodes
requirements: [ urllib, urllib2 ]
author: WAKAYAMA Shirou
'''

EXAMPLES = '''
- hipchat: token=AAAAAA room=notify msg="Ansible task finished"
'''

# ===========================================
# HipChat module specific support methods.
#

V1_MSG_URI = "https://api.hipchat.com/v1/rooms/message"


def msg_uri(version, room="notify"):
    ''''message uri based on version'''
    if version == "2":
        return "https://api.hipchat.com/v2/room/" + room + "/notification"
    return V1_MSG_URI


def send_msg(module, token, room, msg_from, msg, msg_format='text',
             color='yellow', notify=False, version=1, api=False):
    '''sending message to hipchat'''

    params = {}
    params['message'] = msg
    params['message_format'] = msg_format
    params['color'] = color

    if version == "1":
        params['room_id'] = room
        params['api'] = api
        params['from'] = msg_from[:15]  # max length is 15
        if notify:
            params['notify'] = 1
        else:
            params['notify'] = 0

    url = api + "?auth_token=%s" % (token)
    data = urllib.urlencode(params)

    headers = {'content-type': 'application/x-www-form-urlencoded'}

    response, info = fetch_url(module, url, data=data, headers=headers, method='POST')
    if info['status'] == 200:
        return response.read()
    else:
        module.fail_json(msg="failed to send message, return status=%s" % str(params))


# ===========================================
# Module execution.
#

def main():

    module = AnsibleModule(
        argument_spec=dict(
            token=dict(required=True),
            room=dict(required=True),
            msg=dict(required=True),
            msg_from=dict(default="Ansible", aliases=['from']),
            color=dict(default="yellow", choices=["yellow", "red", "green",
                                                  "purple", "gray", "random"]),
            msg_format=dict(default="text", choices=["text", "html"]),
            notify=dict(default=True, type='bool'),
            validate_certs=dict(default='yes', type='bool'),
            version=dict(default=1),
            api=dict(default=None),
        ),
        supports_check_mode=True
    )

    token = module.params["token"]
    room = module.params["room"]
    msg = module.params["msg"]
    msg_from = module.params["msg_from"]
    color = module.params["color"]
    msg_format = module.params["msg_format"]
    notify = module.params["notify"]
    version = module.params["version"]
    api = module.params["api"]
    if api is None:
        api = msg_uri(version, room)

    try:
        send_msg(module, token, room, msg_from, msg, msg_format, color, notify, version, api)
    except Exception, e:
        module.fail_json(msg="unable to send msg: %s" % e)

    changed = True
    module.exit_json(changed=changed, room=room, msg_from=msg_from, msg=msg)

# import module snippets
from ansible.module_utils.basic import *
from ansible.module_utils.urls import *

main()
