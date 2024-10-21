from enum import Enum
from .supported_region import SupportedRegion


class URL_KIND(Enum):
    QUERY_PRICE = 0
    PLACE_ORDER = 1
    SMT_QUERY_PRICE = 2
    SMT_PLACE_ORDER = 3


class OrderRegion:
    AVAILABLE_URLS = {
        SupportedRegion.EUROPE_USA: {
            URL_KIND.PLACE_ORDER: "https://www.eda.cn/openapi/api/nextpcb/Upfile/kiCadUpFile",
            URL_KIND.QUERY_PRICE: "https://www.eda.cn/openapi/api/nextpcb/ajax/valuation",
            URL_KIND.SMT_QUERY_PRICE: "https://www.eda.cn/openapi/api/api-nextpcb/assembly/compute/?appid=7d1b25dce0b410dc588181713afe3465",
            URL_KIND.SMT_PLACE_ORDER: "https://www.eda.cn/openapi/api/api-nextpcb/analyze/upfile/?appid=7f94517ab22cdec82cfcbd09bbed1400"
        },
        SupportedRegion.JAPAN: {
            URL_KIND.PLACE_ORDER: "https://www.eda.cn/openapi/api/jp-nextpcb/Upfile/kiCadUpFile",
            URL_KIND.QUERY_PRICE: "https://www.eda.cn/openapi/api/jp-nextpcb/ajax/valuation",
            URL_KIND.SMT_QUERY_PRICE: "https://www.eda.cn/openapi/api/api-nextpcb/assembly/compute/?appid=7d1b25dce0b410dc588181713afe3465",
            URL_KIND.SMT_PLACE_ORDER: "https://www.eda.cn/openapi/api/api-nextpcb/analyze/upfile/?appid=7f94517ab22cdec82cfcbd09bbed1400"
        },
        # SupportedRegion.CHINA_MAINLAND: {
        #     URL_KIND.PLACE_ORDER: "https://www.hqpcb.com/External/fileQuote",
        #     URL_KIND.QUERY_PRICE: "https://www.hqpcb.com/public/ajax_valuation",
        #     URL_KIND.SMT_QUERY_PRICE: "https://smt.hqchip.com/smtservice/app/price/pricing",
        #     URL_KIND.SMT_PLACE_ORDER: "https://smt.hqchip.com/userCenterApi/DfmOrder/saveDfmSmtTmpOrder",
        # },
    }

    @staticmethod
    def get_url(region: SupportedRegion, kind: URL_KIND):
        if region in OrderRegion.AVAILABLE_URLS:
            return OrderRegion.AVAILABLE_URLS[region][kind]
