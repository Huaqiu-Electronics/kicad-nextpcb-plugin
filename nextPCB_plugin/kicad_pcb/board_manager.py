from pcbnew import GetBoard, LoadBoard, PCB_TRACK
import wx
import os
import threading
import queue

class EmptyBoardException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class BoardManagerNextpcb:
    def __init__(self, board) -> None:
        if board is None:
            raise EmptyBoardException("Empty kicad board")
        self._board = board

    @property
    def board(self):
        return self._board


def load_board_manager():
    try:
        GetBoard().GetFileName()
        board = GetBoard()
        if board:
            return BoardManagerNextpcb(board)
    except Exception as e:
        for fp in   "C:\\Program Files\\demos\\video\\video.kicad_pcb",'C:\\Program Files\\demos\\flat_hierarchy\\flat_hierarchy.kicad_pcb',:
            if os.path.exists(fp):
                return BoardManagerNextpcb(LoadBoard(fp))


class BoardVarManager:
    def __init__(self) -> None:
        self.board_manager = load_board_manager()
        self._board_width = None
        self._board_height = None
        self._layer_count = None
        self._design_settings = None
        self._tracks = []
        self._fp_parts = []

        self._init_event  = threading.Event()  # 用于指示初始化是否完成
        self._init_thread = threading.Thread(target=self._async_init)
        self._init_thread.start()


    def _async_init(self):
        from nextPCB_plugin.kicad_pcb.helpers import get_valid_footprints
        try:
            self._board_width = self.board_manager.board.GetBoardEdgesBoundingBox().GetWidth()
            self._board_height = self.board_manager.board.GetBoardEdgesBoundingBox().GetHeight()
            self._layer_count = self.board_manager.board.GetCopperLayerCount()
            self._design_settings = self.board_manager.board.GetDesignSettings()
            self._tracks: "list[PCB_TRACK]" = self.board_manager.board.Tracks()
            
            
            for fp in get_valid_footprints(self.board_manager.board):
                part = [
                    fp.GetReference(),
                    fp.GetValue(),
                    str(fp.GetFPID().GetLibItemName()),
                ]
                self._fp_parts.append(part)
        except Exception as e:
            print(f"Initialization failed: {e}")
        finally:
            self._init_event.set()  # 无论成功或失败，都通知初始化完成


