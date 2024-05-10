import sys
import os

try:
    PLUGIN_ROOT = os.path.dirname(os.path.abspath(__file__))
    if PLUGIN_ROOT not in sys.path:
        sys.path.append(PLUGIN_ROOT)
    from .nextPCB_plugin.plugin_nextpcb.kicad_amf_action_plugin import NextPCBPlugin
    NextPCBPlugin().register()
    


except Exception as e:
    import logging

    logger = logging.getLogger()
    logger.debug(repr(e))
