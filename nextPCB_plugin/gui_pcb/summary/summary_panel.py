from nextPCB_plugin.order_nextpcb.supported_region import SupportedRegion
from nextPCB_plugin.utils_nextpcb.roles import EditDisplayRole
from .ui_summary_panel import UiSummaryPanelNextpcb

import wx
from .order_summary_model import OrderSummaryModel
from .price_summary_model import PriceSummaryModel


import wx.dataview as dv
from nextPCB_plugin.settings_nextpcb.setting_manager import SETTING_MANAGER
from nextPCB_plugin.gui_pcb.event.pcb_fabrication_evt_list import (
    UpdatePrice,
    PlaceOrder,
    OrderRegionChanged,
    SmtOrderRegionChanged,
    EVT_PANEL_TAB_CONTROL,
    GetUniqueValueFpCount,
    
)

from nextPCB_plugin.kicad_pcb.board_manager import BoardManager

from nextPCB_plugin.kicad_nextpcb_new.mainwindow import NextPCBTools
from nextPCB_plugin.kicad_nextpcb_new.store import Store
import os

from pathlib import Path
import tempfile
from enum import Enum
from .price_model_base import PriceModelBase
from .pcb_price_model import PCBPriceModel
from .smt_price_model import SmtPriceModel
import threading

from nextPCB_plugin.kicad_pcb.helpers import get_valid_footprints

OrderRegionSettings = (
    EditDisplayRole(SupportedRegion.EUROPE_USA, _("Worldwide (English)")),
    EditDisplayRole(SupportedRegion.JAPAN, _("Worldwide (Japanese)")),
)

class PriceCategoryNextpcb(Enum):
    PCB = "pcb"
    SMT = "smt"




        
class SummaryPanelNextpcb(UiSummaryPanelNextpcb):
    def __init__(self, parent, board_manager: BoardManager):
        super().__init__(parent)
        
        self._board_manager = board_manager
        self.project_path = os.path.split(self._board_manager.board.GetFileName())[0]
        nextpcb_path = os.path.join(self.project_path, "nextpcb")
        try:
            Path(nextpcb_path).mkdir(parents=True, exist_ok=True)
        except (PermissionError, OSError) as e:
            self.project_path = os.path.join(tempfile.gettempdir() )
        
        self.db_file_path = os.path.join(self.project_path, "database","project.db")
        self.get_files_dir = os.path.join(self.project_path, "nextpcb", "production_files")
        self.store = Store(self, self.project_path, self._board_manager.board )
        self.price_category: "dict[int,PriceModelBase]" = {
            PriceCategoryNextpcb.PCB: PCBPriceModel(),
            PriceCategoryNextpcb.SMT: SmtPriceModel(),
        }
        
        self.pcb_price_model = { PriceCategoryNextpcb.PCB : PCBPriceModel() }
        self.smt_price_model = { PriceCategoryNextpcb.PCB : self.pcb_price_model[PriceCategoryNextpcb.PCB],
                        PriceCategoryNextpcb.SMT : SmtPriceModel(),
                        }
        
        
        self.btn_update_price.Bind(wx.EVT_BUTTON, self.on_update_price_clicked)
        self.btn_place_order.Bind(wx.EVT_BUTTON, self.on_place_order_clicked)
        self.choice_order_region.Bind(wx.EVT_CHOICE, self.on_region_changed)
        self.Bind(
            wx.EVT_SPLITTER_SASH_POS_CHANGED,
            self.on_sash_changed,
            self.splitter_detail_summary,
        )
        self.btn_bom_match.Bind(wx.EVT_BUTTON, self.on_bom_match)

        self.init_ui()
        thread = threading.Thread(target=self.load_Designator)
        thread.start() 

    def init_ui(self ):
        self.list_bom_view.AppendTextColumn(
            _("Designator"),
            0,
            width=70,
            align=wx.ALIGN_CENTER,
            flags=dv.DATAVIEW_COL_RESIZABLE,
        )
        self.list_bom_view.AppendTextColumn(
            _("Value"),
            1,
            width=140,
            align=wx.ALIGN_CENTER,
            flags=dv.DATAVIEW_COL_RESIZABLE,
        )
        self.list_bom_view.AppendTextColumn(
            _("Footprint"),
            2,
            width=-1,
            align=wx.ALIGN_CENTER,
            flags=dv.DATAVIEW_COL_RESIZABLE,
        )


        self.list_order_summary.AppendTextColumn(
            _("Build Time"),
            0,
            width=-1,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_LEFT,
        )
        self.list_order_summary.AppendTextColumn(
            _("Qty"),
            1,
            width=-1,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_CENTER,
        )
        self.list_order_summary.AppendTextColumn(
            _("Price"),
            2,
            width=-1,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_LEFT,
        )

        self.list_order_summary.SetMinSize(
            wx.Size(-1, SummaryPanelNextpcb.GetLineHeight(self) * 3 + 30)
        )
        self.model_order_summary = OrderSummaryModel()
        self.list_order_summary.AssociateModel(self.model_order_summary)

        self.list_price_detail.AppendTextColumn(
            _("Item"),
            0,
            width=120,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_LEFT,
        )
        self.list_price_detail.AppendTextColumn(
            _("Price"),
            1,
            width=-1,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_RIGHT,
        )


        self.model_price_summary = PriceSummaryModel( self.pcb_price_model )
        self.list_price_detail.AssociateModel(self.model_price_summary)
        self.choice_order_region.AppendItems(
            [i.DisplayRole for i in OrderRegionSettings]
        )
        self.choice_order_region.SetSelection(SETTING_MANAGER.order_region)

        max_width = 300
        for view in self.list_order_summary, self.list_price_detail:
            sum = 0
            for i in range(0, view.GetColumnCount()):
                sum = sum + view.GetColumn(i).GetWidth()
            max_width = max(max_width, sum)
            sum = 0

        self.SetMinSize(wx.Size(max_width + 30, -1))
        self.switch_smt_splitter.Unsplit(self.switch_smt_panel)
        wx.CallAfter(self.switch_smt_splitter.UpdateSize)

    def OnShowTipFinishedCopperWeight(self ):
        try:
            print("Event triggered with weight:")
            wx.MessageBox(f"Event triggered with weight:")
        except Exception as e:
            print("Exception in event handler:", e)


    def ShowTipFinishedCopperWeight(self, copper_wight_selection ):
        if copper_wight_selection == 0:
            self.flnsihed_copper_text.Show(False)
        else:
            self.flnsihed_copper_text.Show(True)
        wx.CallAfter(self.switch_amf_panel.Layout)

    def ShowTipSolderMaskColor(self, mask_color_selection ):
        if mask_color_selection == _("Green"):
            self.solder_mask_text.Show(False)
        else:
            self.solder_mask_text.Show(True)
        wx.CallAfter(self.switch_amf_panel.Layout)

    def ShowTipPcbPackageKind(self, pcb_package_kind_selection):
        if pcb_package_kind_selection == 1:
            self.board_type_text.Show(False)
        else:
            self.board_type_text.Show(True)
        wx.CallAfter(self.switch_amf_panel.Layout)


    def is_database_exists(self):
        result = os.path.exists(self.db_file_path)
        
        evt = GetUniqueValueFpCount(-1, unique_value_fp_count = self.store.get_unique_value_fp_count() )
        wx.PostEvent(self.Parent, evt)
        
        parts = self.store.get_reference_mpn_footprint()
        mpn_values = [part[1] for part in parts]
        all_empty = all(value == '' for value in mpn_values)
        return result and all_empty

    def get_data(self):
        parts = []
        self.list_bom_view.DeleteAllItems()
        parts = self.store.get_reference_mpn_footprint()
        for part in parts:
            self.list_bom_view.AppendItem(part)

    def _get_file_list(self):
        file_list = []
        if os.path.exists(self.get_files_dir) and os.path.isdir(self.get_files_dir):
            # Iterate over files in the directory
            for filename in os.listdir(self.get_files_dir):
                file_path = os.path.join(self.get_files_dir, filename)
                if os.path.isfile(file_path):
                    # Add only files to the file_list
                    file_list.append(file_path)
        return file_list

    def judge_files_exist(self):
        file_list = self._get_file_list()
        self.patch_file = next((file for file in file_list if "CPL" in file and "zip" in file), "")
        self.pcb_file = next((file for file in file_list if "GERBER" in file and "zip" in file), "")
        self.bom_file = next((file for file in file_list if "BOM" in file and "csv" in file), "")
        return os.path.exists(self.patch_file) and os.path.exists(self.pcb_file) and os.path.exists(self.bom_file)

    def get_files(self):
        file_list = self._get_file_list()
        self.patch_file = next((file for file in file_list if "CPL" in file and "zip" in file), "")
        self.pcb_file = next((file for file in file_list if "GERBER" in file and "zip" in file), "")
        self.bom_file = next((file for file in file_list if "BOM" in file and "csv" in file), "")
        smt_files = {
            "patch_file": open(self.patch_file, 'rb'),
            "bom_file": open(self.bom_file, 'rb'),
            "pcb_file": open(self.pcb_file, 'rb'),
        }
        return smt_files

    def get_file_name(self):
        from nextPCB_plugin.api_pcb.base_request import  SmtRequest 
        
        file_list = self._get_file_list()
        patch_file = next((file for file in file_list if "CPL" in file and "zip" in file), "")
        pcb_file = next((file for file in file_list if "GERBER" in file and "zip" in file), "")
        bom_file = next((file for file in file_list if "BOM" in file and "csv" in file), "")
        return SmtRequest(
            patch_file_name=os.path.basename(patch_file),
            bom_file_name=os.path.basename(bom_file),
            pcb_file_name=os.path.basename(pcb_file),
        )


    def switch_to_amf(self):
        self.switch_smt_splitter.Unsplit(self.switch_smt_panel)
        self.splitter_detail_summary.SplitHorizontally(self.m_panel7, self.switch_amf_panel, 0 )

        total_height = self.splitter_detail_summary.GetClientSize().GetHeight()
        sash_position = int(total_height * 3 / 8)
        self.splitter_detail_summary.SetSashPosition(sash_position)
        
        wx.CallAfter(self.switch_smt_splitter.UpdateSize)
        wx.CallAfter(self.splitter_detail_summary.UpdateSize)
        self.model_price_summary = PriceSummaryModel( self.pcb_price_model )
        self.list_price_detail.AssociateModel(self.model_price_summary)
        
        

    def switch_to_smt(self):
        self.splitter_detail_summary.Unsplit(self.switch_amf_panel)
        self.switch_smt_splitter.SplitHorizontally(self.switch_smt_panel, self.m_panel9, 0)
        total_height = self.switch_smt_splitter.GetClientSize().GetHeight()
        sash_position = int(total_height * 3 / 4)
        self.switch_smt_splitter.SetSashPosition(sash_position)
        wx.CallAfter(self.switch_smt_splitter.UpdateSize)
        wx.CallAfter(self.splitter_detail_summary.UpdateSize) 
        self.model_price_summary = PriceSummaryModel( self.smt_price_model )
        self.list_price_detail.AssociateModel(self.model_price_summary)

    def splitter_detail_summaryOnIdle(self, event):
        self.splitter_detail_summary.SetSashPosition(
            SETTING_MANAGER.get_summary_detail_sash_pos()
        )
        self.splitter_detail_summary.Unbind(wx.EVT_IDLE)

    def update_price_detail(self, price: "dict"):
        self.model_price_summary.update_price(price)

    def get_total_price(self):
        return self.model_price_summary.get_sum()

    def update_order_summary(self, price_summary: "list"):
        self.model_order_summary.update_order_info(price_summary)

    def on_bom_match(self, e):
        dlg = NextPCBTools(self, self._board_manager)
        result = dlg.ShowModal()
        # if result in (wx.ID_OK, wx.ID_CANCEL):
        #     dlg.Destroy()
        self.load_Designator()


    def on_update_price_clicked(self, ev):
        self.clear_content()
        evt = UpdatePrice(id=-1)
        wx.PostEvent(self.Parent, evt)

    def on_place_order_clicked(self, ev):
        evt = PlaceOrder(id=-1)
        wx.PostEvent(self.Parent, evt)
        
    def on_generate_fabrication_file(self ):
        dlg = NextPCBTools(self, self._board_manager)
        dlg.generate_fabrication_data()
        self.get_data()
        self.get_files()
        dlg.Destroy()


    def on_sash_changed(self, evt):
        sash_pos = evt.GetSashPosition()
        SETTING_MANAGER.set_summary_detail_sash_pos(sash_pos)

    def GetImagePath(self, bitmap_path):
        from nextPCB_plugin.icon_pcb import GetImagePath
        return GetImagePath(bitmap_path)

    @staticmethod
    def GetLineHeight(parent):
        line = wx.TextCtrl(parent)
        _, height = line.GetSize()
        line.Destroy()
        return height

    def clear_content(self):
        for i in self.model_order_summary, self.model_price_summary:
            i.clear_content()

    def on_region_changed(self, evt):
        SETTING_MANAGER.set_order_region(self.choice_order_region.GetCurrentSelection())
        self.clear_content()
        ev = OrderRegionChanged(-1)
        wx.PostEvent(self.Parent, ev)
        self.smt_on_region_changed(evt)

    def smt_on_region_changed(self, event):
        SETTING_MANAGER.set_order_region(self.choice_order_region.GetCurrentSelection())
        self.clear_content()
        evt = SmtOrderRegionChanged(-1)
        wx.PostEvent(self.Parent, evt)   

    def load_Designator(self):
        if self.is_database_exists():
            self.list_bom_view.DeleteAllItems()
            for fp in get_valid_footprints(self._board_manager.board):
                part = [
                    fp.GetReference(),
                    fp.GetValue(),
                    str(fp.GetFPID().GetLibItemName()),
                ]
                self.list_bom_view.AppendItem(part)
                
        else:
            column_to_replace = self.list_bom_view.GetColumn(1)
            column_to_replace.SetTitle( _("MPN") )
            self.Layout()
            self.get_data()


