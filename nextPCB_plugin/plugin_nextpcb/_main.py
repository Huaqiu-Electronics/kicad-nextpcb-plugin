DEFAULT_CERTIFICATION = None
if DEFAULT_CERTIFICATION is None:
    import certifi
    import ssl
    ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())
DEFAULT_CERTIFICATION = True
from nextPCB_plugin.settings_nextpcb.single_plugin import SINGLE_PLUGIN
import wx


def _main():
    if not SINGLE_PLUGIN.show_existing():
        from nextPCB_plugin.gui_pcb.app_base import NextPCBApp
        import wx
        progress_dialog = wx.ProgressDialog(_("Open Software"), _("In progress") )
        app = NextPCBApp()
        if app.load_success():
            progress_dialog.Update( 50 )
            app.startup_dialog()
            progress_dialog.Update( 100 )
            progress_dialog.Destroy()
