import wx
import wx.dataview
from .foot_print_list_model import FootprintListModel
from nextPCB_plugin.kicad_nextpcb_new.helpers import (
    PLUGIN_PATH,
    HighResWxSize,
)
import wx.dataview as dv


class FootPrintList(wx.dataview.DataViewListCtrl):
    def __init__(
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.dataview.DV_SINGLE,
    ):
        wx.dataview.DataViewListCtrl.__init__(self, parent, id, pos, size, style)

        self.SetMinSize(HighResWxSize(self, wx.Size(900, 400)))
        self.idx = self.AppendTextColumn(
            _("index"),

            width=70, 
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.reference = self.AppendTextColumn(
            _("Reference"),

            width=80,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.value = self.AppendTextColumn(
            _("Value"),

            width= 100,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.footprint = self.AppendTextColumn(
            _("Footprint"),

            width= 300,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.colu_mpn = self.AppendTextColumn(
            _("MPN"),

            width= 200,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.colu_manufact = self.AppendTextColumn(
            _("Manufacturer"),

            width= 200,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.colu_category = self.AppendTextColumn(
            _("Category"),

            width= 200,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.colu_sku = self.AppendTextColumn(
            _("SKU"),

            width= 150,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        
        self.colu_quantity = self.AppendTextColumn(
            _("Quantity"),

            width= 80,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.bom = self.AppendToggleColumn(
            _("BOM"),

            width= 60,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.pos = self.AppendToggleColumn(
            _("POS"),

            width= 60,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.side = self.AppendTextColumn(
            _("Side"),

            width= 50,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )

        self.AppendTextColumn(
            " ",

            width=1,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )

    def init_data_view(self, foot_print_list_data):
        return

        self.FootprintListModel = FootprintListModel( foot_print_list_data )
        self.AssociateModel( self.FootprintListModel )

        # wx.CallAfter(self.part_list_data_panel.Layout)
        