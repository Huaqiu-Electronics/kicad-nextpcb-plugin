# Inspired by https://github.com/AislerHQ/PushForKiCad/blob/main/src/plugin.py

import pcbnew
import os


from nextPCB_plugin.icon_pcb import ICON_ROOT

class NextPCBPlugin(pcbnew.ActionPlugin):
    def __init__(self):
        self.name = "NextPCB"
        self.category = "Manufactur"
        self.description = "Quote and place order with one button click."
        self.pcbnew_icon_support = hasattr(self, "nextpcb_button")
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(ICON_ROOT, "nextpcb_icon.png")
        self.dark_icon_file_name = os.path.join(ICON_ROOT, "nextpcb_icon.png")


    def Run(self):
        from nextPCB_plugin.plugin_nextpcb._main import _main
        _main()
