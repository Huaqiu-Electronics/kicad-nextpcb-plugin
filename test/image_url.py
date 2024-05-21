import wx
import requests
from io import BytesIO
import logging

class ImageFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG)
        
        self.panel = wx.Panel(self)
        self.part_image = wx.StaticBitmap(self.panel)
        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.part_image, 1, wx.EXPAND | wx.ALL, 5)
        self.panel.SetSizerAndFit(self.sizer)
        
        self.SetSize((800, 600))
        self.Centre()


    def download_and_set_image(self, url):
        # Ensure URL is complete
        if not url.startswith("http:") and not url.startswith("https:"):
            url = "https:" + url
        
        self.logger.debug(f"image_count: {url}")
        
        try:
            response = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.9999.999 Safari/537.36"
            })
            response.raise_for_status()
            image_data = response.content
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error downloading image: {e}")
            self.part_image.SetBitmap(wx.NullBitmap)
            self.Layout()
            return
        
        self.set_image(image_data)

    def set_image(self, image_data):
        stream = BytesIO(image_data)
        image = wx.Image(stream)
        
        if not image.IsOk():
            self.logger.debug("Image is not valid")
            self.part_image.SetBitmap(wx.NullBitmap)
        else:
            self.logger.debug("Setting image")
            bitmap = wx.Bitmap(image)
            self.part_image.SetBitmap(bitmap)
        
        self.Layout()

class MyApp(wx.App):
    def OnInit(self):
        frame = ImageFrame(None, title="Image Viewer")
        frame.Show()
        frame.download_and_set_image("https://media.futureelectronics.com/semiconductors/discretes/diodes/schottky-diodes/DO-35-PROTECTION-THYRISTORS-STM-FNT-SML.JPG?m=cgQKyY")
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()
