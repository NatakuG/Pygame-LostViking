""" Player controllable object
Includes:
    -> PlayerPlane
"""
from enum import Flag
import pygame
from pygame.sprite import spritecollideany
from pygame.locals import *

from src.setting import SCREEN_WIDTH, SCREEN_HEIGHT

from src.util.collide_detect import collide_detect
from src.util.type import Pos
from src.util.inertial import accelerate, decelerate

from src.helper.sound import play_sound

from src.game.groups import G_Enemys, G_Enemy_Bullets
from src.game.animation import AnimeSprite
from src.game.animation.Effect import AttachEffect
from src.game.custom_events import EVENT_PLAYER_SHOOT, EVENT_PLAYER_BOMB
from .player_control import PLAYER1_CONTROL, PLAYER2_CONTROL
from .PlayerWeapon import PlayerWeapon
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class PlayerPlane(AnimeSprite):
    """ Basic Player Abstract class
    """
    BOMB_COUNT_MAX = 3
    BOMB_COUNT_DEFAULT = 1

    LIFE_MAX = 5
    LIFE_DEFAULT = 3

    LEVEL_MAX = 3

    MAX_SPEED_X = 8
    MAX_SPEED_UP = 10
    MAX_SPEED_DOWN = 5
    ACC_X = 0.8
    ACC_UP = 1
    ACC_DOWN = 0.6
    MAX_HEALTH = 100

    INVINCIBLE_DURATION = 100

    LIMIT_TOP = 50
    LIMIT_BOTTOM = 100

    def __init__(self, weapon: PlayerWeapon, pos, frames, frame_size, id=1):
        # Init
        super().__init__(frames=frames, frame_size=frame_size)

        self.id = id
        if id == 1:
            self.controller = PLAYER1_CONTROL
        else:
            self.controller = PLAYER2_CONTROL

        if pos:
            self.start_position = pos
        else:
            self.start_position = (int(pygame.display.get_surface().get_width() // 2),
                                   int(pygame.display.get_surface().get_height() - self.rect.height - self.LIMIT_BOTTOM))

        # Set bullet type
        ''' Init Weapon '''
        self._weapon = weapon

        self._score = 0
        self._life = self.LIFE_DEFAULT
        self._bomb_count = self.BOMB_COUNT_DEFAULT
        self._level = 1

        self._speed = pygame.Vector2(0, 0)
        self._health = self.MAX_HEALTH

        self._attack_speed = 20
        self._count_attack_interval = 0
        self._count_invincible = 0

        ''' States '''
        self.state = None
        self.is_invincible = False
        self.is_active = True
        self._is_moving_x = False
        self._is_moving_y = False

        # Set init position
        self.set_pos(pos)

    # --------------- Super Methods Override --------------- #
    def update(self) -> None:
        """ Update method from Sprite, is called per frame """
        super().update()
        self._reload()
        if self.is_active:
            if self.is_invincible:
                if self._count_invincible > 0:
                    self._count_invincible -= 1
                elif self._count_invincible == 0:
                    self.is_invincible = False
            self._move()
            self.collide_enemy(G_Enemys)
            self.collide_enemy_bullet(G_Enemy_Bullets)

    def anime_end_loop_hook(self):
        if not self.is_active:
            self.reset()

    # --------------------- Behaviors ---------------------

    def _move(self) -> None:
        if self._speed.y != 0 or self._speed.x != 0:
            # Move this object
            # (Note: this is the only place when the object is really moving)
            self.rect.move_ip(self._speed)

            # Speed down if there's no movement command on X or Y
            # (Note: Only values of _speed_x/_speed_y will be changed here)
            if not self._is_moving_x:
                self._speed.x = decelerate(self._speed.x, self.ACC_X)
            if not self._is_moving_y:
                self._speed.y = decelerate(self._speed.y, self.ACC_DOWN)

            # Restrict the plane inside the screen
            if self.rect.bottom > SCREEN_HEIGHT - self.LIMIT_BOTTOM:
                self.rect.bottom = SCREEN_HEIGHT - self.LIMIT_BOTTOM
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH
            if self.rect.top < 0 + self.LIMIT_TOP:
                self.rect.top = 0 + self.LIMIT_TOP

    def _reload(self):
        if self._count_attack_interval > 0:
            self._count_attack_interval -= 1

    def destroy(self) -> None:
        self._health = 0
        self.dec_life()
        self.is_active = False
        self._is_moving_y = False
        self._is_moving_x = False
        self.set_anime_state("DESTROY")
        play_sound("PLAYER_DESTROY")

    # ------------------ Battle
    def hit(self, damage=100, **kwargs) -> bool:
        """
        This function is called in collision detection
        """
        if not self.is_invincible and self.is_active:
            # Take damage
            self._health -= damage
            if self._health > 0:
                # Get Hit effect
                AttachEffect(
                    self,
                    frames={
                        "IDLE": self.frames["HIT"]
                    },
                    frame_size=self.frame_size
                )
            else:
                # HP below 0
                self.destroy()
            return True
        else:
            return False

    def invincible(self, duration: int = None, continuous: bool = False):
        if continuous:
            self._count_invincible = -1
        elif duration is not None:
            self._count_invincible = duration
        else:
            self._count_invincible = self.INVINCIBLE_DURATION
        self.is_invincible = True

    def remove_invincible(self):
        self._count_invincible = 0
        self.is_invincible = False

    def attack(self) -> None:
        """
        This method is called from a user attack event
        """
        if self.is_active:
            if self._count_attack_interval == 0:
                play_sound("PLAYER_SHOOT")
                self._weapon.shoot(pos=Pos(self.rect.center))
                self._count_attack_interval = self._attack_speed

    def collide_enemy(self, enemy_group):
        enemy = spritecollideany(self, enemy_group, collide_detect(0.5))
        if enemy and enemy.is_active and not self.is_invincible:
            self._score += enemy.score
            self.destroy()
            enemy.destroy()

    def collide_enemy_bullet(self, enemy_bullet_group):
        bullet = spritecollideany(
            self, enemy_bullet_group, collide_detect(0.6))
        if bullet:
            self.hit(bullet.damage)
            bullet.hit(target=self)

    # ------------------ Trigger-Movement-Commands ------------------
    # ------------------ (Instant trigger method called by events) --
    # Trigger Move Up

    def trigger_move_up(self) -> None:
        """ Trigger this object to move Up (with acceleration)
        Called by event (e.g. Button press)
        """
        if not self.is_active:
            return
        # If the plane starts to move, switch frame to "MOVE_UP"
        if not self._is_moving_y:
            self._is_moving_y = True
            self.set_anime_state("MOVE_UP")
        # If not outside the screen
        if self.rect.top > 0:
            self._speed.y = accelerate(
                self._speed.y, self.MAX_SPEED_UP, -1, self.ACC_UP)
        else:
            self._speed.y = 0
            self.rect.top = 0

    # Trigger Move Down
    def trigger_move_back(self) -> None:
        """ Trigger this object to move Down (with acceleration)
        Called by event (e.g. Button press)
        (Note: This method only change the value of _speed_x / _speed_y)
        """
        if not self.is_active:
            return
        # If it was not moving before, change image
        if not self._is_moving_y:
            self._is_moving_y = True
            self.set_anime_state("MOVE_DOWN")
        # If not outside the screen
        if self.rect.bottom < SCREEN_HEIGHT - self.LIMIT_BOTTOM:
            self._speed.y = accelerate(
                self._speed.y, self.MAX_SPEED_DOWN, 1, self.ACC_DOWN)
        else:
            self._speed.y = 0
            self.rect.bottom = SCREEN_HEIGHT - self.LIMIT_BOTTOM

    # Trigger Move Left
    def trigger_move_left(self) -> None:
        """ Trigger this object to move Left (with acceleration)
        Called by event (e.g. Button press)
        (Note: This method only change the value of _speed_x / _speed_y)
        """
        if not self.is_active:
            return
        # If not outside the screen
        if self.rect.left > 0:
            self._is_moving_x = True
            self._speed.x = accelerate(
                self._speed.x, self.MAX_SPEED_X, -1, self.ACC_X)
        else:
            self._speed.x = 0
            self.rect.left = 0

    # Trigger Move Right
    def trigger_move_right(self) -> None:
        """ Trigger this object to move Right (with acceleration)
        Called by event (e.g. Button press)
        (Note: This method only change the value of _speed_x / _speed_y)
        """
        if not self.is_active:
            return
        # If not outside the screen
        if self.rect.right < SCREEN_WIDTH:
            self._is_moving_x = True
            self._speed.x = accelerate(
                self._speed.x, self.MAX_SPEED_X, 1, self.ACC_X)
        else:
            self._speed.x = 0
            self.rect.right = SCREEN_WIDTH

    # Trigger Brake y, only triggered when lease the button
    def trigger_stop_y(self) -> None:
        """ Trigger this object to stop in y axis (with acceleration)
        Triggered by event (e.g. Button release)
        (Note: This only sets the flag, the deceleration will be done
        by _inertial_deceleration automatically in update)
        """
        self._is_moving_y = False
        if self.is_active:
            self.set_anime_state("IDLE")

    # Trigger Brake x
    def trigger_stop_x(self) -> None:
        """ Trigger this object to stop in x axis (with acceleration)
        Triggered by event (e.g. Button release)
        (Note: This only sets the flag, the deceleration will be done
        by _inertial_deceleration automatically in update)
        """
        self._is_moving_x = False

    # ------------------ Attributes -----------------

    # ----- Life
    @property
    def life(self) -> int:
        return self._life

    def add_life(self) -> bool:
        if self._life >= self.LIFE_MAX:
            logging.info("Add Life: Max lives reached")
            return False
        self._life += 1
        logging.info("Add Life")
        return True

    def dec_life(self) -> bool:
        if self._life <= 0:
            logging.warning("Error: Can't decrease life under 0.")
            return False
        self._life -= 1
        logging.info("Decrease Life")
        return True

    # ----- Weapon & Level

    @property
    def weapon(self) -> PlayerWeapon:
        return self._weapon

    @weapon.setter
    def weapon(self, weapon_type) -> None:
        self._weapon = weapon_type

    @property
    def level(self) -> int:
        return self.weapon.level

    def level_up(self) -> None:
        self.weapon.level_up()

    def level_down(self) -> None:
        self.weapon.level_down()

    def reset_level(self) -> None:
        self.weapon.reset_level()

    # ----- Score
    @property
    def score(self) -> int:
        return self._score

    def add_score(self, score) -> int:
        self._score += score

    # ----- Attack Speed
    @property
    def attack_speed(self) -> int:
        return self._attack_speed

    def set_attack_speed(self, attack_speed) -> None:
        self._attack_speed = attack_speed

    # ----- Position
    @property
    def pos(self) -> tuple[int, int]:
        return self.rect.center

    def set_pos(self, point=None) -> None:
        if point is None:
            self.rect.center = self.start_position
        else:
            # Move its rect to a point, or a default position
            self.rect.center = point

    # ----- Speed
    @property
    def speed(self) -> pygame.Vector2:
        return self._speed

    # ----- Health
    @property
    def health(self) -> int:
        return self._health

    def add_health(self) -> bool:
        if self.health < self.MAX_HEALTH:
            self._health = self.MAX_HEALTH
            logging.info("Add Health")
            return True
        logging.info("Add Health: Full health reached")
        return False

    # ----- Bomb
    @property
    def bomb_count(self) -> int:
        return self._bomb_count

    def add_bomb(self) -> bool:
        if self._bomb_count >= self.BOMB_COUNT_MAX:
            logging.info("Add Bomb: Max Bomb number reached")
            return False
        self._bomb_count += 1
        logging.info("Add Bomb")
        return True

    def dec_bomb(self) -> bool:
        if self._bomb_count <= 0:
            logging.warning("Error: Can't decrease bomb under 0.")
            return False
        self._bomb_count -= 1
        logging.info("Decrese Bomb")
        return True

    # ----------------- Reset method -----------------
    # Reset
    def reset(self, point=None) -> None:
        self.is_active = True
        self.is_invincible = True
        self._count_invincible = self.INVINCIBLE_DURATION
        self.set_anime_state("IDLE")
        self.set_pos(point)

        def break_cb_func():
            return not self.is_invincible
        AttachEffect(
            self,
            frames={
                "IDLE": self.frames["INVINCIBLE"]
            },
            frame_size=self.frame_size,
            break_cb_func=break_cb_func,
            loop=True
        )
        # self.is_invincible = True
        self._weapon.reset_level()
        self._health = self.MAX_HEALTH

    # ----------------- Event -----------------

    def detect_key_pressed(self):
        # If Key Pressed
        key_pressed = pygame.key.get_pressed()
        if key_pressed[self.controller.MOVE_UP.value]:
            self.trigger_move_up()
        elif key_pressed[self.controller.MOVE_DOWN.value]:
            self.trigger_move_back()
        elif key_pressed[self.controller.MOVE_LEFT.value]:
            self.trigger_move_left()
        elif key_pressed[self.controller.MOVE_RIGHT.value]:
            self.trigger_move_right()

    def handle_event(self, e):
        if e.type == KEYDOWN:
            # Space Button
            if e.key == self.controller.SHOOT.value:
                pygame.event.post(pygame.event.Event(
                    EVENT_PLAYER_SHOOT, {"player": self, "id": self.id}))
                pygame.time.set_timer(pygame.event.Event(
                    EVENT_PLAYER_SHOOT, {"player": self, "id": self.id}), self.attack_speed)
            else:
                return False

            return True
        # --------------- Key Up Events ---------------
        elif e.type == KEYUP:
            if e.key in [self.controller.MOVE_UP.value, self.controller.MOVE_DOWN.value]:
                self.trigger_stop_y()
            elif e.key in [self.controller.MOVE_LEFT.value, self.controller.MOVE_RIGHT.value]:
                self.trigger_stop_x()
            elif e.key == self.controller.BOMB.value:
                pygame.event.post(pygame.event.Event(
                    EVENT_PLAYER_BOMB, {"player": self, "id": self.id}))
            elif e.key == self.controller.SHOOT.value:
                pygame.time.set_timer(pygame.event.Event(
                    EVENT_PLAYER_SHOOT, {"player": self, "id": self.id}), 0)
            else:
                return False
            return True
        return False
