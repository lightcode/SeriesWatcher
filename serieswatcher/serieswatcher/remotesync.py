#!/usr/bin/env python

import json
import urllib
import httplib


KEY = '64bd795efb2dc7c1ab9eeeafec3c9884c345fc6bad4c9328d841fd8efccc7626'

class RemoteSyncApi(object):
    def __init__(self, server):
        self._server = server
        self._token = None
    
    def _makeRequest(self, method, url, params, headers={}):
        if self._token:
            params.update({'token': self._token})
        params = urllib.urlencode(params)
        conn = httplib.HTTPConnection(self._server)
        
        if method == 'GET':
            conn.request('GET', '%s?%s' % (url, params))
        elif method == 'POST':
            conn.request("POST", url, params, headers)
        else:
            print 'Not implemented'
        
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
    
    def _makeGetRequest(self, url, params={}):
        return self._makeRequest('GET', url, params)
    
    def _makePostRequest(self, url, params={}):
        headers = {"Content-type": "application/x-www-form-urlencoded"}
        return self._makeRequest('POST', url, params, headers)
    
    def authenticate(self):
        r = self._makePostRequest("/auth/connection", {'key': KEY})
        if r['status'] == 200:
            self._token = r['token']


if __name__ == '__main__':
    rsapi = RemoteSyncApi('localhost:81')
    rsapi.authenticate()
    print rsapi._makeGetRequest("/test")