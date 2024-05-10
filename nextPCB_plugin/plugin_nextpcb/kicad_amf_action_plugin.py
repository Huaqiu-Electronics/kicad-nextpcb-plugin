# Inspired by https://github.com/AislerHQ/PushForKiCad/blob/main/src/plugin.py

import pcbnew
import os


from nextPCB_plugin.icon_pcb import ICON_ROOT
from nextPCB_plugin.settings_nextpcb.timestamp import TimeStamp

class NextPCBPlugin(pcbnew.ActionPlugin):
    def __init__(self):
        self.name = "NextPCB"
        self.category = "Manufactur"
        self.description = "Quote and place order with one button click."
        self.pcbnew_icon_support = hasattr(self, "nextpcb_button")
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(ICON_ROOT, "nextpcb_icon.png")
        self.dark_icon_file_name = os.path.join(ICON_ROOT, "nextpcb_icon.png")

        timestamp=TimeStamp()
        timestamp.log( " init Plugin ", level='info')


    def Run(self):
        from nextPCB_plugin.plugin_nextpcb._main import _main
        timestamp=TimeStamp()
        timestamp.log( " upload _main ", level='info')
        _main()
