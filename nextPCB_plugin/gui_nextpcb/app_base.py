from nextPCB_plugin.language_trans.lang_const import LANG_DOMAIN
from nextPCB_plugin.settings.supported_layer_count import AVAILABLE_LAYER_COUNTS
import builtins
import sys
import os
from nextPCB_plugin import PLUGIN_ROOT
from nextPCB_plugin.kicad.board_manager import load_board_manager
from nextPCB_plugin.utils.combo_box_ignore_wheel import ComboBoxIgnoreWheel
from nextPCB_plugin.icon import GetImagePath
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
            os.path.join(PLUGIN_ROOT, "language", "locale")
        )
        existing_locale = wx.GetLocale()
        if existing_locale is not None:
            existing_locale.AddCatalog(LANG_DOMAIN)

    def load_success(self):
        from nextPCB_plugin.settings.setting_manager import SETTING_MANAGER

        SETTING_MANAGER.register_app(self)
        self.board_manager = load_board_manager()
        if self.board_manager.board.GetCopperLayerCount() not in AVAILABLE_LAYER_COUNTS:
            wx.MessageBox(_("Unsupported layer count!"))
            return False
        return True

    def startup_dialog(self):
        from nextPCB_plugin.gui_nextpcb.main_frame import MainFrame
        from nextPCB_plugin.settings.setting_manager import SETTING_MANAGER

        self.main_wind = MainFrame(
            self.board_manager, SETTING_MANAGER.get_window_size()
        )
        self.main_wind.SetIcon(wx.Icon(GetImagePath("Huaqiu.ico")))
        self.main_wind.Show()
