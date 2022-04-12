from src.util.type import Size, Pos
from src.helper.image import get_image
from src.game.player import PlayerPlane
from src.helper.sound import play_sound
from .SUPPLY_TYPE import SUPPLY_TYPE
from .Supply import Supply


class SupplyBomb(Supply):
    def __init__(self, pos: Pos = None):
        super().__init__(pos,
                         frames={
                             "BASE": get_image("Supply/SupplyBase.png"),
                             "IDLE": get_image("Supply/SupplyBomb.png")
                         },
                         frame_size=None
                         )
        self.type = SUPPLY_TYPE.Life

    def get_by_player(self, player: PlayerPlane):
        player.add_bomb()
        play_sound("SUPPLY_BOMB")
        return super().get_by_player(player)
