import pygame
import random
from src.game.animation.Effect import Effect
from src.helper.image.image_loader import get_image
from src.util.type import Pos, Size
from .util import get_supply_type
from src.setting import SCREEN_WIDTH
from src.util.type import Pos
from src.game.groups import G_Supplies
from .SUPPLY_TYPE import SUPPLY_TYPE


EVENT_ADD_SUPPLY = pygame.event.custom_type()
EVENT_DROP_SUPPLY = pygame.event.custom_type()


supply_cooldown_timer = pygame.time.Clock()

supply_cooldown_count = supply_cooldown_timer.tick()

SUPPLY_COOLDOWN = 10000


class SupplyEvent:

    def __init__(self) -> None:
        pass


def supply_event_config():
    pygame.time.set_timer(EVENT_ADD_SUPPLY, 35000)


def supply_events_handler(event):
    if event.type == EVENT_ADD_SUPPLY:
        pos = Pos(
            [random.randint(int(SCREEN_WIDTH/3), int(2 * SCREEN_WIDTH/3)), -50])
        sup = get_supply_type()
        sup(pos)

    elif event.type == EVENT_DROP_SUPPLY:

        global supply_cooldown_count
        supply_cooldown_count += supply_cooldown_timer.tick()
        if supply_cooldown_count < SUPPLY_COOLDOWN:
            return
        elif len(G_Supplies.sprites()) < 2:
            Effect(
                pos=event.pos,
                frames={
                    "IDLE": get_image("Supply/SupplyDrop.png")
                },
                frame_size=Size([50, 50]))
            supply_cooldown_count = 0
            sup = get_supply_type(event.supply_type)
            sup(event.pos)


def drop_supply_event(pos: Pos, supply_type: SUPPLY_TYPE = None):

    pygame.event.post(pygame.event.Event(
        EVENT_DROP_SUPPLY, {"pos": pos, "supply_type": supply_type}))
