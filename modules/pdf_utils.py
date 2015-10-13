# -*- coding: utf-8 -*-
import os

PROJECT_ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(PROJECT_ROOT_PATH, '../uploads').replace('\\','/')
def fetch_resources(uri, rel):
    if not os.path.isfile(os.path.join(MEDIA_ROOT,uri)):
        return "http://www.portalpet.feis.unesp.br%s" %uri
    return os.path.join(MEDIA_ROOT,uri)
