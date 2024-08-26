from nextPCB_plugin.gui_pcb.summary.price_summary_model import PriceCategoryNextpcb
from nextPCB_plugin.kicad_pcb.board_manager import BoardManager
from nextPCB_plugin.kicad_pcb.fabrication_data_generator_evt import (
    EVT_BUTTON_FABRICATION_DATA_GEN_RES,
    FabricationDataGenEvent,
    GenerateStatus,
)

from nextPCB_plugin.pcb_fabrication_pcb.base_pcb.base_info_view import BaseInfoViewNextpcb
from nextPCB_plugin.pcb_fabrication_pcb.process_pcb.process_info_view import ProcessInfoViewNextpcb
from nextPCB_plugin.pcb_fabrication_pcb.special_process_pcb.special_process_view import (
    SpecialProcessViewNextpcb,
)
from nextPCB_plugin.pcb_fabrication_pcb.personalized_pcb.personalized_info_view import (
    PersonalizedInfoViewNextpcb,
)
from nextPCB_plugin.gui_pcb.summary.summary_panel import SummaryPanelNextpcb
from nextPCB_plugin.settings_nextpcb.default_express import DEFAULT_EXPRESS ,ALLOWED_KEYS , ADDED_DATA
from nextPCB_plugin.settings_nextpcb.single_plugin import SINGLE_PLUGIN
from nextPCB_plugin.utils_nextpcb.form_panel_base import FormKind, FormPanelBase
from nextPCB_plugin.gui_pcb.event.pcb_fabrication_evt_list import (
    EVT_UPDATE_PRICE,
    EVT_PLACE_ORDER,
    EVT_ORDER_REGION_CHANGED,
    EVT_SMT_ORDER_REGION_CHANGED,
    PanelTabControl,
    EVT_COMBO_NUMBER,
    EVT_SHOW_TIP_FLNSIHED_COPPER_WEIGHT,
    EVT_SHOW_SOLDER_MASK_COLOR,
    EVT_SHOW_PCB_PACKAGE_KIND,
    EVT_GET_UNIQUE_VALUE_FP_COUNT,
    EVT_DESTORY_SMT_DATA_GEN,
)
from nextPCB_plugin.settings_nextpcb.setting_manager import SETTING_MANAGER
from nextPCB_plugin.kicad_pcb.fabrication_data_generator import FabricationDataGenerator
from nextPCB_plugin.api_pcb.base_request import ( BaseRequest )

from nextPCB_plugin.gui_pcb.summary.order_summary_model import (
    AVAILABLE_TIME_UNIT,
    OrderSummary,
    BuildTime,
    TimeUnit,
)
import wx
import wx.xrc
import wx.dataview
import urllib

import json
from nextPCB_plugin.order_nextpcb.order_region import OrderRegion, URL_KIND
from nextPCB_plugin.kicad_pcb.fabrication_data_generator_thread import DataGenThread
from enum import Enum

from nextPCB_plugin.smt_pcb_fabrication_pcb.smt_base_nextpcb.base_info_view import SmtBaseInfoViewNextpcb
from nextPCB_plugin.smt_pcb_fabrication_pcb.process_nextpcb.process_info_view import SmtProcessInfoViewNextpcb
from nextPCB_plugin.smt_pcb_fabrication_pcb.personalized_nextpcb.personalized_info_view import (
    SmtPersonalizedInfoViewNextpcb,
)
from urllib.parse import urlencode
import threading
from wx.lib.pubsub import pub
import webbrowser
from nextPCB_plugin.gui_pcb.summary.upload_file import UploadFile
from nextPCB_plugin.order_nextpcb.supported_region import SupportedRegion
from nextPCB_plugin.utils_nextpcb.request_helper import RequestHelper
        

class SMTPCBFormPartNextpcb(Enum):
    SMT_BASE_INFO = 0
    SMT_PROCESS_INFO = 1
    SMT_PERSONALIZED = 2


SMT_PCB_PANEL_CTORS_NEXTPCB = {
    SMTPCBFormPartNextpcb.SMT_BASE_INFO: SmtBaseInfoViewNextpcb,
    SMTPCBFormPartNextpcb.SMT_PROCESS_INFO: SmtProcessInfoViewNextpcb,
    SMTPCBFormPartNextpcb.SMT_PERSONALIZED: SmtPersonalizedInfoViewNextpcb,
}


class PCBFormPartNextpcb(Enum):
    BASE_INFO = 0
    PROCESS_INFO = 1
    SPECIAL_PROCESS = 2
    PERSONALIZED = 3


PCB_PANEL_CTORS_NEXTPCB = {
    PCBFormPartNextpcb.BASE_INFO: BaseInfoViewNextpcb,
    PCBFormPartNextpcb.PROCESS_INFO: ProcessInfoViewNextpcb,
    PCBFormPartNextpcb.SPECIAL_PROCESS: SpecialProcessViewNextpcb,
    PCBFormPartNextpcb.PERSONALIZED: PersonalizedInfoViewNextpcb,
}

DATA = "data"
LIST = "list"
SUGGEST = "suggest"
DEL_TIME = "deltime"
NAME = "name"
PCS_COUNT = "pcs_count"
TOTAL = "total"
PCB = "pcb"
FEE = "fee"
BCOUNT = "bcount"


class MainFrameNextpcb(wx.Frame):
    def __init__(self, board_manager: BoardManager, size, parent=None):
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=_("   NextPCB   "),
            pos=wx.DefaultPosition,
            size=size,
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
        )
        self._board_manager = board_manager
        self._fabrication_data_gen = None
        self._fabrication_data_gen_thread = None
        self._pcb_form_parts: "dict[PCBFormPartNextpcb, FormPanelBase]" = {}       
        self.smt_pcb_form_parts: "dict[PCBFormPartNextpcb, FormPanelBase]" = {}    
        self._data_gen_progress: wx.ProgressDialog = None
        self._dataGenThread: DataGenThread = None
        self._number = 5
        SINGLE_PLUGIN.register_main_wind(self)
        self.init_ui()


    def show_data_gen_progress_dialog(self):
        if self._data_gen_progress is not None:
            self._data_gen_progress.Destroy()
            self._data_gen_progress = None
        self._data_gen_progress = wx.ProgressDialog(
            _("Preparing for your order"),
            _("The browser will be launched automatically while ready"),
            maximum=GenerateStatus.MAX_PROGRESS,
            parent=self,
            style=0 | wx.PD_APP_MODAL,
        )



    def init_ui(self):
        self.SetSizeHints(wx.DefaultSize, wx.DefaultSize)
        left_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.book_ctrl = wx.Panel(self.main_splitter)
        left_sizer = wx.BoxSizer( wx.VERTICAL )

        #------------amf---------------
        self.main_notebook = wx.Notebook( self.book_ctrl, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.active_manufacturing = wx.Panel( self.main_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.main_notebook.AddPage( self.active_manufacturing, u"                PCB                ", True )
        amf_sizer = wx.BoxSizer( wx.VERTICAL )

        
        pcb_fab_scroll_wind = wx.ScrolledWindow(
            self.active_manufacturing,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(-1, -1),
            wx.HSCROLL | wx.VSCROLL,
        )
        pcb_fab_scroll_wind.SetScrollRate(10, 10)

        lay_pcb_fab_panel = wx.BoxSizer(wx.VERTICAL)
        for i in PCB_PANEL_CTORS_NEXTPCB:
            view = PCB_PANEL_CTORS_NEXTPCB[i](pcb_fab_scroll_wind, self._board_manager)
            self._pcb_form_parts[i] = view
            lay_pcb_fab_panel.Add(view, 0, wx.ALL | wx.EXPAND, 5)
            
        pcb_fab_scroll_wind.SetSizer(lay_pcb_fab_panel)
        pcb_fab_scroll_wind.Layout()

        self.summary_view = SummaryPanelNextpcb( self.main_splitter, self._board_manager )
        amf_sizer.Add(pcb_fab_scroll_wind, 1, wx.EXPAND, 8)
        self.active_manufacturing.SetSizer(amf_sizer)
        self.active_manufacturing.Layout()
        amf_sizer.Fit(self.active_manufacturing)
        for i in self._pcb_form_parts.values():
            i.init()
            i.on_region_changed()

        # self._pcb_form_parts[ PCBFormPartNextpcb.PROCESS_INFO].register_xx_handle(lambda :  self.summary_view.OnShowTipFinishedCopperWeight())
        #------------smt-------------
        self.surface_mount_technology = wx.Panel( self.main_notebook, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        self.main_notebook.AddPage( self.surface_mount_technology, u"         BOM && SMT         ", False )
        smt_sizer = wx.BoxSizer( wx.VERTICAL )
        
        smt_fab_scroll_wind = wx.ScrolledWindow(
            self.surface_mount_technology,
            wx.ID_ANY,
            wx.DefaultPosition,
            wx.Size(-1, -1),
            wx.HSCROLL | wx.VSCROLL,
        )
        smt_fab_scroll_wind.SetScrollRate(10, 10)

        lay_pcb_fab_panel1 = wx.BoxSizer(wx.VERTICAL)
        for i in SMT_PCB_PANEL_CTORS_NEXTPCB:
            view = SMT_PCB_PANEL_CTORS_NEXTPCB[i](smt_fab_scroll_wind, self._board_manager)
            self.smt_pcb_form_parts[i] = view
            lay_pcb_fab_panel1.Add(view, 0, wx.ALL | wx.EXPAND, 5)

        smt_fab_scroll_wind.SetSizer(lay_pcb_fab_panel1)
        smt_fab_scroll_wind.Layout()

        smt_sizer.Add(smt_fab_scroll_wind, 1, wx.EXPAND, 8)
        self.surface_mount_technology.SetSizer(smt_sizer)
        self.surface_mount_technology.Layout()
        smt_sizer.Fit(self.surface_mount_technology)
        
        self.surface_mount_technology.SetSizer( smt_sizer )
        self.surface_mount_technology.Layout()
        smt_sizer.Fit( self.surface_mount_technology )

        for j in self.smt_pcb_form_parts.values():
            j.init()
            j.on_region_changed()
            
        #---- book ctrl ----
        self.main_splitter.SplitVertically(
            self.book_ctrl, self.summary_view, 0
        )
        left_sizer.Add( self.main_notebook, 1, wx.EXPAND |wx.ALL, 0 )
        self.book_ctrl.SetSizer( left_sizer )
        self.book_ctrl.Layout()
        left_sizer.Fit( self.book_ctrl )
        
        
        self.main_notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.change_ui)


        self.Bind(EVT_UPDATE_PRICE, self.on_update_price)
        self.Bind(EVT_PLACE_ORDER, self.on_place_order)
        self.Bind(EVT_COMBO_NUMBER, self.on_place_order)
        self.Bind(EVT_ORDER_REGION_CHANGED, self.on_order_region_changed)
        self.Bind(EVT_SMT_ORDER_REGION_CHANGED, self.smt_on_order_region_changed)

        self.Bind(wx.EVT_SIZE, self.OnSize, self)
        self.Bind(wx.EVT_CLOSE, self.OnClose, self)
        self.Bind(
            wx.EVT_SPLITTER_SASH_POS_CHANGED,
            self.on_sash_pos_changed,
            self.main_splitter,
        )
        self.main_splitter.Bind(wx.EVT_IDLE, self.main_splitter_on_idle)

        
        self.Bind( EVT_SHOW_TIP_FLNSIHED_COPPER_WEIGHT, self.OnShowTipFinishedCopperWeight )
        self.Bind( EVT_SHOW_SOLDER_MASK_COLOR, self.OnShowTipSolderMaskColor  )
        self.Bind(EVT_SHOW_PCB_PACKAGE_KIND, self.OnShowTipPcbPackageKind )
        self.Bind(EVT_GET_UNIQUE_VALUE_FP_COUNT, self.OnGetValueFpGuoupCount )
        

        self.Bind(
            EVT_BUTTON_FABRICATION_DATA_GEN_RES, self.on_fabrication_data_gen_progress
        )
        self.Bind( EVT_DESTORY_SMT_DATA_GEN, self.destory_data_gen_dialog )
        
        pub.subscribe(self.receive_number_data, "combo_number")
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(self.main_splitter, 1, wx.EXPAND, 5)
        self.SetSizer(main_sizer)
        self.Layout()
        self.Centre(wx.BOTH)



    def OnShowTipFinishedCopperWeight(self, evt ):
        self.summary_view.ShowTipFinishedCopperWeight(evt.copper_wight_selection)

    def OnShowTipSolderMaskColor(self, evt ):
        self.summary_view.ShowTipSolderMaskColor(evt.solder_color_selection)
        
    def OnShowTipPcbPackageKind(self , evt):
        self.summary_view.ShowTipPcbPackageKind(evt.pcb_package_kind_selection)
        
    def OnGetValueFpGuoupCount(self , evt):
        self.smt_pcb_form_parts[SMTPCBFormPartNextpcb.SMT_PROCESS_INFO].SetValueFpGuoupCount(evt.unique_value_fp_count)
        
    def change_ui(self, evt):
        self.selected_page_index = self.main_notebook.GetSelection()
        if self.selected_page_index == 0:
            self.summary_view.switch_to_amf()
        elif self.selected_page_index == 1:
            self.summary_view.switch_to_smt()


    def on_fabrication_data_gen_progress(self, evt: FabricationDataGenEvent):
        if self._data_gen_progress is not None:
            res = evt.get_status()
            if GenerateStatus.RUNNING == res.get_status():
                self._data_gen_progress.Update(res.get_progress(), res.get_message())
            else:
                self._data_gen_progress.Destroy()
                self._data_gen_progress = None
                if GenerateStatus.FAILED == res.get_status():
                    wx.MessageBox(f"{res.get_message()}")

    def destory_data_gen_dialog(self, evt):
        self._data_gen_progress.Update(GenerateStatus.MAX_PROGRESS - 1, _("Sending order request"))
        self._data_gen_progress.Destroy()
        self._data_gen_progress = None

    def on_sash_pos_changed(self, evt):
        sash_pos = evt.GetSashPosition()
        SETTING_MANAGER.set_mainwindow_sash_pos(sash_pos)

    def main_splitter_on_idle(self, evt):
        self.main_splitter.SetSashPosition(
            SETTING_MANAGER.get_mainwindow_sash_position()
        )
        self.main_splitter.Unbind(wx.EVT_IDLE)

    @property
    def fabrication_data_generator(self):
        if self._fabrication_data_gen is None:
            self._fabrication_data_gen = FabricationDataGenerator(
                self._board_manager.board
            )
        return self._fabrication_data_gen

    def smt_build_form(self, kind: FormKind):
        base = self.summary_view.get_file_name().__dict__
        for i in self.smt_pcb_form_parts.values():
            base = base | i.get_from(kind)
        return base
    
    def smt_build_file(self):
        smt_files = self.summary_view.get_files()
        return smt_files
        
    def judge_files_exist(self):
        return self.summary_view.judge_files_exist()
        
    def build_form(self, kind: FormKind):
        base = BaseRequest().__dict__
        for i in self._pcb_form_parts.values():
            base = base | i.get_from(kind)
        return base

    def get_query_price_form(self):

        self.selected_page_index = self.main_notebook.GetSelection()
        if self.selected_page_index == 0:
            form = self.build_form(FormKind.QUERY_PRICE)
            if SETTING_MANAGER.order_region == SupportedRegion.CHINA_MAINLAND:
                form = form | DEFAULT_EXPRESS
            
        elif self.selected_page_index == 1:
            form = self.smt_build_form(FormKind.QUERY_PRICE)
            if SETTING_MANAGER.order_region != SupportedRegion.CHINA_MAINLAND:
                form =self.remove_extra_params(form, ALLOWED_KEYS) 
                form = self.convert_keys(form)
                form = form
        return form

    def remove_extra_params(self, form, allowed_keys):
        return {key: value for key, value in form.items() if key in allowed_keys}

    def convert_keys( self, form ):
        key_mapping = {
            'pcb_ban_width': 'pcb_width',
            'pcb_ban_height': 'pcb_height',
            'bom_material_type_number': 'patch_material_type',
        }
        converted_form = {key_mapping.get(key, key): value for key, value in form.items()}
        return converted_form

    def get_place_order_form(self):
        if self.selected_page_index == 0:
            return {**self.build_form(FormKind.PLACE_ORDER), "type": "pcbfile"}
        return {**self.build_form(FormKind.PLACE_ORDER) }

    def form_is_valid(self):
        for i in self._pcb_form_parts.values():
            if not i.is_valid():
                return False
        return True
    
    def smt_form_is_valid(self):
        for i in self.smt_pcb_form_parts.values():
            if not i.is_valid():
                return False
        return True

    def parse_zh_data_time(self, dt: str):
        t = ""
        unit = None
        for i in dt:
            if i.isnumeric():
                t = t + i
            elif "天" == i:
                unit = TimeUnit.DAY.value
        if unit is None:
            unit = TimeUnit.HOUR.value
        return BuildTime(int(t), unit)

    def parse_price(self, summary: json):
        self.summary_view.update_price_detail({PriceCategoryNextpcb.PCB.value: summary})
        normal_total_price = self.summary_view.get_total_price()
        suggests = []
        if SUGGEST in summary and DEL_TIME in summary[SUGGEST]:
            for suggest in summary[SUGGEST][DEL_TIME]:
                if NAME in suggest and FEE in suggest and BCOUNT in suggest:
                    qty = int(suggest[BCOUNT])
                    price = float(suggest[FEE]) + normal_total_price
                    self.selected_page_index = self.main_notebook.GetSelection()
                    if self.selected_page_index == 0:
                        suggests.append(
                            OrderSummary(
                                pcb_quantity=qty,
                                price=price,
                                build_time=self.parse_zh_data_time(suggest[NAME]),
                            )
                        )
        self.summary_view.update_order_summary(suggests)

    def parse_smt_price(self, summary: json):
        self.summary_view.update_price_detail({PriceCategoryNextpcb.SMT.value: summary})

    def parse_price_list(self, summary: json):
        self.summary_view.update_price_detail(summary)
        suggests = []
        for item in summary:
            if SUGGEST in summary[item] and DEL_TIME in summary[item][SUGGEST]:
                for suggest in summary[item][SUGGEST][DEL_TIME]:
                    if NAME in suggest and TOTAL in suggest and PCS_COUNT in suggest:
                        full_time_cost = str(suggest[NAME]).split(" ")
                        if len(full_time_cost) > 1:
                            qty = int(suggest[PCS_COUNT])
                            price = float(suggest[TOTAL])
                            self.selected_page_index = self.main_notebook.GetSelection()
                            if self.selected_page_index == 0:
                                suggests.append(
                                    OrderSummary(
                                        pcb_quantity=qty,
                                        price=price,
                                        build_time=BuildTime(
                                            int(full_time_cost[0]), full_time_cost[1]
                                        ),
                                    )
                            )
        self.summary_view.update_order_summary(suggests)

    def on_update_price(self, evt):

        self.selected_page_index = self.main_notebook.GetSelection()
        if self.selected_page_index == 0:
            if not self.form_is_valid():
                return
            url = OrderRegion.get_url(SETTING_MANAGER.order_region, URL_KIND.QUERY_PRICE)
            if url is None:
                wx.MessageBox(_("No available url for querying price in current region"))
                return
            try:
                form = self.get_query_price_form()
                rep = urllib.request.Request(
                    url, data=RequestHelper.convert_dict_to_request_data(form)
                )
                fp = urllib.request.urlopen(rep)
                data = fp.read()
                encoding = fp.info().get_content_charset("utf-8")
                content = data.decode(encoding)
                quote = json.loads(content)
                if DATA in quote and LIST in quote[DATA]:
                    return self.parse_price_list(quote[DATA][LIST])
                elif SUGGEST in quote:
                    return self.parse_price(quote)
                else:
                    err_msg = quote
                    if "msg" in quote:
                        err_msg = quote["msg"]
                    wx.MessageBox(_("Incorrect form parameter: ") + err_msg)
            except Exception as e:
                wx.MessageBox(str(e))
                raise e  # TODO remove me

        elif self.selected_page_index == 1:
            if not self.form_is_valid():
                return
            url = OrderRegion.get_url(SETTING_MANAGER.order_region, URL_KIND.SMT_QUERY_PRICE)
            if url is None:
                wx.MessageBox(_("No available url for querying price in current region"))
                return
            try:
                form = self.get_query_price_form()
                encoded_data = urlencode(form).encode('utf-8')
                headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                rep = urllib.request.Request(
                    url, data = encoded_data, headers=headers   
                )
                fp = urllib.request.urlopen(rep)
                data = fp.read()                    
                encoding = fp.info().get_content_charset("utf-8")
                content = data.decode(encoding)
                quotes = json.loads(content)
                if quotes.get("response_code", {}) != '2000' :
                    wx.MessageBox(_("Return false"))
                    return                    
                quote = quotes.get("response_data", {}).get("list", {}).get("assembly", {})
                return self.parse_smt_price(quote)
            except Exception as e:
                wx.MessageBox(str(e))
                raise e  # TODO remove me

    def on_place_order(self, evt):
        import time
        self.selected_page_index = self.main_notebook.GetSelection()
        
        if self.selected_page_index == 0:
            if not self.form_is_valid():
                return
            url = OrderRegion.get_url(SETTING_MANAGER.order_region, URL_KIND.PLACE_ORDER)
            if url is None:
                wx.MessageBox(_("No available url for placing order in current region"))
                return
            self.show_data_gen_progress_dialog()
            if self._dataGenThread is not None:
                self._dataGenThread.join()
                self._dataGenThread = None
            data = self.get_place_order_form()
            self._dataGenThread = DataGenThread(
                self, 
                self.fabrication_data_generator, 
                self.get_place_order_form(), 
                url
            )
            
        elif self.selected_page_index == 1:
            
            if not self.form_is_valid():
                return
            url = OrderRegion.get_url(SETTING_MANAGER.order_region, URL_KIND.SMT_PLACE_ORDER)
            if url is None:
                wx.MessageBox(_("No available url for querying price in current region"))
                return
            self.show_data_gen_progress_dialog()
            self.summary_view.on_generate_fabrication_file()
            try:
                form = self.get_place_order_form() | self.get_query_price_form()
                # form = self.get_query_price_form()
                smt_order_region = SETTING_MANAGER.order_region
                self._data_gen_progress.Update( 200, _("Upload fabrication file") )
                uploadfile =  UploadFile( self._board_manager, url, form, smt_order_region, self._number )

                self._data_gen_progress.Update( 400 )
                uploadfile.upload_smtfile()
                if uploadfile.verify_pcb_smt_upload_success():
                    self._data_gen_progress.Update( 600, _("Sending order request") )
                    upload_file = uploadfile.upload_bomfile()
                    webbrowser.open(upload_file)

            except Exception as e:
                wx.MessageBox(str(e))
                raise e  # TODO remove me
            finally:
                self.destory_data_gen_dialog(evt)

    def receive_number_data(self, param1):
        self._number =  param1

    def adjust_size(self):
        for i in self._pcb_form_parts.values():
            i.Layout()
        self.active_manufacturing.Layout()
        self.book_ctrl.Layout()
        self.Layout()

    def smt_adjust_size(self):
        for j in self.smt_pcb_form_parts.values():
            j.Layout()
        self.surface_mount_technology.Layout()
        self.book_ctrl.Layout()
        self.Layout()

    def on_order_region_changed(self, ev):
        for i in self._pcb_form_parts.values():
            i.on_region_changed()
        self.adjust_size()
        
    def smt_on_order_region_changed(self, ev):    
        for j in self.smt_pcb_form_parts.values():
            j.on_region_changed()
        self.smt_adjust_size()

    def OnSize(self, evt):
        evt.Skip()
        SETTING_MANAGER.set_window_size(self.Size)

    def OnClose(self, evt):
        SINGLE_PLUGIN.register_main_wind(None)
        self.summary_view.Destroy()
        self.Destroy()
