from nextPCB_plugin.language_pcb.lang_const import LANG_DOMAIN

import builtins
import sys
import os
from nextPCB_plugin import PLUGIN_ROOT
from nextPCB_plugin.kicad_pcb.board_manager import load_board_manager
from nextPCB_plugin.utils_nextpcb.combo_box_ignore_wheel import ComboBoxIgnoreWheel

import wx

# add translation macro to builtin similar to what gettext does
builtins.__dict__["_"] = wx.GetTranslation
wx.Choice = ComboBoxIgnoreWheel


def _displayHook(obj):
    if obj is not None:
        print(repr(obj))


class NextPCBApp(wx.EvtHandler):
    def __init__(self):
        super().__init__()
        sys.displayhook = _displayHook
        wx.Locale.AddCatalogLookupPathPrefix(
            os.path.join(PLUGIN_ROOT, "language_pcb", "locale")
        )
        existing_locale = wx.GetLocale()
        if existing_locale is not None:
            existing_locale.AddCatalog(LANG_DOMAIN)
        self.progress_dialog = wx.ProgressDialog(_("Open Software"), _("In progress") )
        self.progress_dialog.Update( 30 )

    def load_success(self):
        from nextPCB_plugin.settings_nextpcb.setting_manager import SETTING_MANAGER
        from nextPCB_plugin.settings_nextpcb.supported_layer_count import AVAILABLE_LAYER_COUNTS
        SETTING_MANAGER.register_app(self)
        self.board_manager = load_board_manager()
        if self.board_manager.board.GetCopperLayerCount() not in AVAILABLE_LAYER_COUNTS:
            wx.MessageBox(_("Unsupported layer count!"))
            return False
        return True

    def startup_dialog(self):
        from nextPCB_plugin.gui_pcb.main_frame import MainFrameNextpcb
        from nextPCB_plugin.settings_nextpcb.setting_manager import SETTING_MANAGER
        from nextPCB_plugin.icon_pcb import GetImagePath
        from nextPCB_plugin.kicad_nextpcb_new.mainwindow import NextPCBTools

        
        # dlg = NextPCBTools(None, self.board_manager)
        # dlg.ShowModal()

                
        self.progress_dialog.Update( 60 )
        self.main_wind = MainFrameNextpcb(
            self.board_manager, SETTING_MANAGER.get_window_size()
        )
        self.main_wind.SetIcon(wx.Icon(GetImagePath("Huaqiu.ico")))
        self.main_wind.Show()
        
        self.progress_dialog.Update( 100 )
        self.progress_dialog.Destroy()
