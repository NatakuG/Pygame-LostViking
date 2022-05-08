import pygame.event
from pygame.locals import *
from src.game.groups import G_Enemys

from src.helper.sound.sound_loader import play_sound
from src.game.custom_events import *
from .PlayerPlane import PlayerPlane
from .PlayerBomb import PlayerNucBomb


def _handle_player_shoot_event(player: PlayerPlane):
    player.attack()


def _handle_player_bomb_launch_event(player: PlayerPlane):
    if player.bomb_count > 0:
        player.dec_bomb()
        PlayerNucBomb.launch(player.pos, player)
        pygame.event.set_blocked(EVENT_PLAYER_BOMB)
    else:
        play_sound("BOMB_ERROR")


def _handle_player_bomb_explode_event(player: PlayerPlane):
    from src.game.groups import G_Enemys, G_Enemy_Bullets
    for each in G_Enemys:
        if each.is_active:
            each.hit(1000)
            if not each.is_active:
                player.add_score(each.score)

    for each in G_Enemy_Bullets:
        each.hit()

    pygame.event.set_allowed(EVENT_PLAYER_BOMB)


def detect_custom_event(e: pygame.event.Event):
    # --------------- Customized Events ---------------
    if e.type == EVENT_PLAYER_SHOOT:
        if hasattr(e, "player"):
            _handle_player_shoot_event(e.player)

    elif e.type == EVENT_PLAYER_BOMB:
        if hasattr(e, "player"):
            _handle_player_bomb_launch_event(e.player)
    elif e.type == EVENT_BOMB_EXPLODE:
        if hasattr(e, "player"):
            _handle_player_bomb_explode_event(e.player)
            print("Bomb explode")
    else:
        return False
    return True
