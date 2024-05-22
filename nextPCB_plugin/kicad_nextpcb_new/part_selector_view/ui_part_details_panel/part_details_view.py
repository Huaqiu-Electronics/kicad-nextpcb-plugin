import wx
import wx.xrc
import wx.dataview
import requests
import webbrowser
import io
import logging
from .ui_part_details_panel import UiPartDetailsPanel
import wx.dataview as dv
import threading
from PIL import Image

parameters = {
    "mpn": _("MPN"),
    "manufacturer": _("Manufacturer"),
    "pkg": _("Package / Footprint"),
    "category": _("Category"),
    "part_desc": _("Description"),
    "sku": _("SKU"),
}

class PartDetailsView(UiPartDetailsPanel):
    def __init__(
        
        self,
        parent,
        id=wx.ID_ANY,
        pos=wx.DefaultPosition,
        size=wx.DefaultSize,
        style=wx.TAB_TRAVERSAL,
        name=wx.EmptyString,
    ):
        super().__init__(parent, id=id, pos=pos, size=size, style=style, name=name)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        # ---------------------------------------------------------------------
        # ----------------------- Properties List -----------------------------
        # ---------------------------------------------------------------------
        self.property = self.data_list.AppendTextColumn(
            _("Property"),
            width=180,
            mode=dv.DATAVIEW_CELL_ACTIVATABLE,
            align=wx.ALIGN_LEFT,
        )
        self.value = self.data_list.AppendTextColumn(
            _("Value"), width=-1, mode=dv.DATAVIEW_CELL_ACTIVATABLE, align=wx.ALIGN_LEFT
        )
        self.data_list.Bind(wx.dataview.EVT_DATAVIEW_SELECTION_CHANGED, self.on_open_pdf)
        self.initialize_data()

    def initialize_data(self):
        # Initialize data and populate the data list
        self.data_list.DeleteAllItems()
        self.part_image.SetBitmap(wx.NullBitmap)

        for k, v in parameters.items():
            self.data_list.AppendItem([v, " "])
        # self.data_list.AppendItem([_("Price"), " "])
        self.data_list.AppendItem([_("Datasheet"), " "])
        self.data_list.AppendItem(["1", " "])
        # update layout
        self.Layout()

    def on_open_pdf(self, e):
        """Open the linked datasheet PDF on button click."""
        item = self.data_list.GetSelection()
        row = self.data_list.ItemToRow(item)
        if item is None or row == -1:
            self.logger.debug("No item selected or clicked on empty space.")
            return 
        Datasheet = self.data_list.GetTextValue(row, 0)
        if Datasheet == _("Datasheet"): 
            self.logger.debug(f"pdf trigger link")
            if self.pdfurl != "-" :
                self.logger.info("opening %s", str(self.pdfurl))
                webbrowser.open("https:" + self.pdfurl)
        else:
            self.logger.debug(f"pdf trigger link error")
            return

    def show_image(self, picture):
        if picture:
            self.logger.debug(f"image: {self.get_scaled_bitmap(picture)}")
            if self.get_scaled_bitmap(picture) is None:
                self.part_image.SetBitmap(wx.NullBitmap)
            else:
                self.part_image.SetBitmap(self.get_scaled_bitmap(picture))
        else:
            self.part_image.SetBitmap(wx.NullBitmap)
            self.Layout()

    def get_scaled_bitmap(self, url):
        """Download a picture from a URL and convert it into a wx Bitmap"""
        # 确保 URL 是一个完整的网址，添加 https:// 如果缺失
        if not url.startswith("http:") and not url.startswith("https:"):
            url = "https:" + url
        self.logger.debug(f"image_count: {url}")
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36"
        }
        
        try:
            response = requests.get(url, headers=header)
            response.raise_for_status()  # Raises an HTTPError for bad responses
            content = response.content
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading image: {e}")
            return None
        if not content:
            return None
        bitmap = self.display_bitmap(content)
        return bitmap
        
    def display_bitmap(self, content):
        io_bytes = io.BytesIO(content)
        try:
            image = Image.open(io_bytes)
        except (IOError, SyntaxError) as e:
            # Handle the error if the image file is not valid
            print(f"Error opening image: {e}")
            return
        
        sb_size = self.part_image.GetSize()
        min_dimension = min(sb_size.GetWidth(), sb_size.GetHeight())
        if min_dimension <= 0:
            self.report_part_data_fetch_error(
                _("The width and height of new size must be greater than 0")
            )
            return
        # Scale the image
        factor = min_dimension / max(image.width, image.height) 
        new_width = int(image.width * factor)
        new_height = int(image.height * factor)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        # 将PIL图像转换为wxPython图像
        wx_image = wx.Image(new_width, new_height)
        wx_image.SetData(resized_image.convert('RGB').tobytes())
        
        if not wx_image.IsOk():
            self.logger.error("The wx.Image is not valid.")
            return None
        result = wx.Bitmap(wx_image)
        return result

    def get_part_data(self, _clicked_part):
        """fetch part data from NextPCB API and parse it into the table, set picture and PDF link"""
        if _clicked_part == "":
            self.report_part_data_fetch_error(
                _("returned data does not have expected clicked part")
            )
        self.clicked_part = _clicked_part
        
        for i in range(self.data_list.GetItemCount()):
            self.data_list.DeleteItem(0)
        for k, v in parameters.items():
            val = self.clicked_part.get(k, "-")
            if val != "null" and val:
                self.data_list.AppendItem([v, str(val)])
            else:
                self.data_list.AppendItem([v, "-"])

        self.pdfurl = self.clicked_part.get("datasheet", {})
        self.pdfurl = "-" if self.pdfurl == "" else self.pdfurl
        self.data_list.AppendItem(
            [
                _("Datasheet"),
                self.pdfurl,
            ]
        )

        picture = self.clicked_part.get("image", [])
        threading.Thread(target= self.show_image,args=(picture, ) ).start()


    def report_part_data_fetch_error(self, reason):
        mpn = self.clicked_part.get('mpn', "-")
        wx.MessageBox(
            _(f"Failed to download part detail: {reason}\r\nWe looked for a part named:\r\n{ mpn }\r\n"),
            _("Error"),
            style=wx.ICON_ERROR,
        )
        # self.Destroy()
