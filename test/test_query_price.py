from .test_utils import TestUtils
from . import TEST_ROOT
from nextPCB_plugin.utils_nextpcb.request_helper import RequestHelper
from nextPCB_plugin.order_nextpcb.supported_region import SupportedRegion
from nextPCB_plugin.order_nextpcb.order_region import OrderRegion, URL_KIND

import requests

import urllib
import os
import json

REQUESTS = {
    SupportedRegion.CHINA_MAINLAND: "hq_pcb.json",
    SupportedRegion.JAPAN: "next_pcb_jp.json",
    SupportedRegion.EUROPE_USA: "next_pcb_en.json",
}


def test_query_price():
    for i in REQUESTS:
        form = TestUtils.read_json(os.path.join(TEST_ROOT, "query_price", REQUESTS[i]))
        rep = urllib.request.Request(
            OrderRegion.get_url(i, URL_KIND.QUERY_PRICE),
            data=RequestHelper.convert_dict_to_request_data(form),
        )
        fp = urllib.request.urlopen(rep)
        data = fp.read()
        encoding = fp.info().get_content_charset("utf-8")
        content = data.decode(encoding)
        quote = json.loads(content)
        if "code" in quote:
            assert quote["code"] == 200
        else:
            assert quote["total"] > 0
