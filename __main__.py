from wx import App, Locale

class StandAloneApp(App):
    def __init__(
        self, redirect=False, filename=None, useBestVisual=False, clearSigInt=True
    ):
        super().__init__(redirect, filename, useBestVisual, clearSigInt)

    def OnInit(self):
        from nextPCB_plugin.settings_nextpcb.setting_manager import SETTING_MANAGER

        self.locale = Locale(SETTING_MANAGER.get_language())
        return True


if __name__ == "__main__":
    from nextPCB_plugin.plugin_nextpcb._main import _main


    app = StandAloneApp()
    _main()
    app.MainLoop()
    