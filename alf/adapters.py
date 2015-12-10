# -*- coding: utf-8 -*-

import requests


def mount_retry_adapter(session, retries):
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)

    session.mount('http://', adapter)
    session.mount('https://', adapter)
