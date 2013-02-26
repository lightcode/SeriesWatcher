#!/usr/bin/env python

import json
import httplib
import urllib


KEY = '64bd795efb2dc7c1ab9eeeafec3c9884c345fc6bad4c9328d841fd8efccc7626'

class RemoteSyncApi(object):
    def __init__(self, server):
        self._server = server
        self._token = None
    
    
    def _makeGetRequest(self, ressource, params={}):
        if self._token:
            params.update({'token': self._token})
        params = urllib.urlencode(params)
        conn = httplib.HTTPConnection(self._server)
        conn.request("GET", '%s?%s' % (ressource, params))
        response = conn.getresponse()
        data = response.read()
        res = {}
        res['status'] = response.status
        if response.status == 200:
            try:
                res.update(json.loads(data))
            except ValueError:
                res['status'] = 500
                return res
        return res
    
    
    def _makePostRequest(self, ressource, params={}):
        if self._token:
            params.update({'token': self._token})
        params = urllib.urlencode(params)
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        conn = httplib.HTTPConnection(self._server)
        conn.request("POST", ressource, params, headers)
        response = conn.getresponse()
        data = response.read()
        res = {}
        res['status'] = response.status
        if response.status == 200:
            try:
                res.update(json.loads(data))
            except ValueError:
                res['status'] = 500
                return res
        return res
    
    
    def authenticate(self):
        r = self._makePostRequest("/auth/connection", {'key': KEY})
        if r['status'] == 200:
            self._token = r['token']


if __name__ == '__main__':
    rsapi = RemoteSyncApi('localhost:81')
    rsapi.authenticate()
    print rsapi._makeGetRequest("/test")
