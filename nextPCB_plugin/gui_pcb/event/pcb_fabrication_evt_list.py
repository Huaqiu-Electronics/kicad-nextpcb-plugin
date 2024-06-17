import wx.lib.newevent as ne


LocaleChangeEvent, EVT_LOCALE_CHANGE = ne.NewCommandEvent()

UpdatePrice, EVT_UPDATE_PRICE = ne.NewCommandEvent()

PlaceOrder, EVT_PLACE_ORDER = ne.NewCommandEvent()

MaskColorChange, EVT_MASK_COLOR_CHANGE = ne.NewCommandEvent()

LayerCountChange, EVT_LAYER_COUNT_CHANGE = ne.NewCommandEvent()

OrderRegionChanged, EVT_ORDER_REGION_CHANGED = ne.NewCommandEvent()

SmtOrderRegionChanged, EVT_SMT_ORDER_REGION_CHANGED = ne.NewCommandEvent()

boardCount, EVT_BOARD_COUNT = ne.NewCommandEvent()


PanelTabControl, EVT_PANEL_TAB_CONTROL = ne.NewCommandEvent()

ComboNumber, EVT_COMBO_NUMBER = ne.NewCommandEvent()


ShowTipFlnsihedCopperWeight, EVT_SHOW_TIP_FLNSIHED_COPPER_WEIGHT = ne.NewCommandEvent()

ShowSolderMaskColor, EVT_SHOW_SOLDER_MASK_COLOR = ne.NewCommandEvent()

ShowPcbPackageKind, EVT_SHOW_PCB_PACKAGE_KIND = ne.NewCommandEvent()

GetUniqueValueFpCount, EVT_GET_UNIQUE_VALUE_FP_COUNT = ne.NewCommandEvent()

DestorySmtDataGen, EVT_DESTORY_SMT_DATA_GEN = ne.NewCommandEvent()