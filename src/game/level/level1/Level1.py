import random
import pygame
import logging
import sys
from src.setting import MAIN_VOLUME
from src.helper.sound.sound_loader import load_sound, play_music
from src.helper.image import load_image, del_image
from src.helper.sound import load_music
from .Scout import EnemyScout
from .Phoenix import EnemyPhoenix
from .Carrier import EnemyCarrier

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class Level1:
    SPAWN_SPEED_SCOUT = 100
    SPAWN_SPEED_SCOUT_MAX = 30
    SPAWN_SPEED_SCOUT_INCREASE = 0.01
    SPAWN_SPEED_PHOENIX = 2000
    SPAWN_SPEED_CARRIER = 8200

    def __init__(self, enable_event=True) -> None:
        self.start_time = 0
        load_image("Enemy/Laser.png")
        load_image("Enemy/Laser2.png")
        load_image("Enemy/LaserHit.png")
        load_image("Enemy/Scout/ScoutBase.png")
        load_image("Enemy/Scout/ScoutNormal.png")
        load_image("Enemy/Scout/ScoutDestroy.png")
        load_image("Enemy/Scout/ScoutHit.png")
        load_image("Enemy/Scout/ScoutAttack.png")
        load_image("Enemy/Phoenix/PhoenixBase.png")
        load_image("Enemy/Phoenix/PhoenixNormal.png")
        load_image("Enemy/Phoenix/PhoenixFast.png")
        load_image("Enemy/Phoenix/PhoenixDestroy.png")
        load_image("Enemy/Phoenix/PhoenixHit.png")
        load_image("Enemy/Phoenix/PhoenixAttack.png")
        load_image("Enemy/Phoenix/PhoenixShield.png")
        load_image("Enemy/Carrier/CarrierBase.png"),
        load_image("Enemy/Carrier/CarrierNormal.png"),
        load_image("Enemy/Carrier/CarrierDestroy.png"),
        load_image("Enemy/Carrier/CarrierHit.png"),
        load_image("Enemy/Carrier/CarrierAttack.png")
        load_image("Enemy/Carrier/LaserCarrierStart.png")
        load_image("Enemy/Carrier/LaserCarrierIdle.png")
        load_image("Enemy/Carrier/LaserCarrierEnd.png")
        load_image("Enemy/Interceptor/InterceptorBase.png"),
        load_image("Enemy/Interceptor/InterceptorIdle.png"),
        load_image("Enemy/Interceptor/InterceptorMove.png"),
        load_image("Enemy/Interceptor/InterceptorDestroy.png"),
        load_image("Enemy/Interceptor/InterceptorHit.png"),
        load_image("Enemy/Interceptor/InterceptorAttack.png")

        load_sound("Enemy/Shield.wav", MAIN_VOLUME - 0.4, "SHIELD")
        load_sound("Enemy/Destroy.wav", MAIN_VOLUME - 0.4, "ENEMY_DESTROY")
        load_sound("Enemy/PhoenixArrive.wav",
                   MAIN_VOLUME - 0.4, "PHOENIX_ARRIVE")
        load_sound("Enemy/PhoenixLaser.wav",
                   MAIN_VOLUME - 0.3, "PHOENIX_LASER")
        load_sound("Enemy/PhoenixDestroy.wav",
                   MAIN_VOLUME - 0.3, "PHOENIX_DESTROY")
        load_sound("Enemy/ScoutDestroy.wav",
                   MAIN_VOLUME - 0.4, "SCOUT_DESTROY")
        load_sound("Enemy/CarrierDestroy.wav",
                   MAIN_VOLUME - 0.1, "CARRIER_DESTROY")
        load_sound("Enemy/CarrierLaserStart.wav",
                   MAIN_VOLUME - 0.4, "CARRIER_LASER_START")
        load_sound("Enemy/CarrierLaser.wav",
                   MAIN_VOLUME - 0.3, "CARRIER_LASER")
        load_sound("Enemy/CarrierArrive.wav",
                   MAIN_VOLUME - 0.2, "CARRIER_ARRIVE")
        load_sound("Enemy/InterceptorLaser.wav",
                   MAIN_VOLUME - 0.4, "INTERCEPTOR_LASER")
        load_sound("Enemy/InterceptorCreate.wav",
                   MAIN_VOLUME - 0.4, "INTERCEPTOR_CREATE")
        load_sound("Enemy/Hit.wav",
                   MAIN_VOLUME - 0.4, "ENEMY_HIT")

        self.spwan_speed_scout = self.SPAWN_SPEED_SCOUT
        self.spwan_speed_phoenix = self.SPAWN_SPEED_PHOENIX
        self._count_create_scout = 0
        self._count_create_phoenix = 0
        self._phoenix_created_times = 0
        self._count_create_carrier = 0
        self.carrier_created = False

    def start(self):
        self.start_time = pygame.time.get_ticks()

        self.spwan_speed_scout = self.SPAWN_SPEED_SCOUT
        self._count_create_scout = 0
        self._count_create_phoenix = 0
        self._phoenix_created_times = 0
        self._count_create_carrier = 0
        self._carrier_created = False

        load_music("music/bgm1.ogg", MAIN_VOLUME - 0.4)
        play_music()

    def update(self):
        self._count_create_phoenix += 1

        if self.spwan_speed_scout > self.SPAWN_SPEED_SCOUT_MAX:
            self.spwan_speed_scout -= self.SPAWN_SPEED_SCOUT_INCREASE

        if not self._carrier_created:
            self._count_create_scout += 1
            self._count_create_carrier += 1

            if self._count_create_scout > self.spwan_speed_scout:
                self._count_create_scout = 0
                if EnemyScout.add_enemy_scout(1):
                    logging.info('Create Scout')
            if self._count_create_phoenix > self.spwan_speed_phoenix:
                self._phoenix_created_times += 1
                self._count_create_phoenix = 0
                if self._phoenix_created_times >= 3:
                    EnemyPhoenix.add_enemy_phoenix()
                else:
                    EnemyPhoenix.add_enemy_phoenix(
                        side=random.choice(["left", "right"]))
                logging.info('Create Phoenix')
            if self._count_create_carrier > self.SPAWN_SPEED_CARRIER:
                self._count_create_carrier = 0
                self._carrier_created = True
                EnemyCarrier()
                logging.info('Create Carrier')
        else:
            if self._count_create_phoenix > self.spwan_speed_phoenix * 1.5:
                self._count_create_phoenix = 0
                EnemyPhoenix.add_enemy_phoenix(
                    side=random.choice(["left", "right"]))
                logging.info('Create Phoenix')

    def event_handler(self, event):
        if event.type == self.EVENT_CREATE_SCOUT:
            if EnemyScout.add_enemy_scout(1):
                logging.info('Create Scout')
            return True
        elif event.type == self.EVENT_CREATE_PHOENIX:
            if pygame.time.get_ticks() - self.start_time > 60000:
                EnemyPhoenix.add_enemy_phoenix()
            else:
                EnemyPhoenix.add_enemy_phoenix(
                    side=random.choice(["left", "right"]))
            logging.info('Create Phoenix')
            return True
        elif event.type == self.EVENT_CREATE_CARRIER:
            EnemyCarrier()
            logging.info('Create Carrier')
            pygame.time.set_timer(self.EVENT_CREATE_CARRIER, 0)
            pygame.time.set_timer(self.EVENT_CREATE_PHOENIX, 0)
            pygame.time.set_timer(self.EVENT_CREATE_PHOENIX,
                                  self.SPAWN_SPEED_PHOENIX * 2)
            pygame.time.set_timer(self.EVENT_CREATE_SCOUT, 0)
            return True
        return False

    def __del__(self) -> None:
        del_image("Enemy/ScoutBase.png")
        del_image("Enemy/ScoutNormal.png")
        del_image("Enemy/ScoutDestroy.png")
        del_image("Enemy/ScoutHit.png")
        del_image("Enemy/Scout/ScoutAttack.png")
        del_image("Enemy/Phoenix/PhoenixBase.png")
        del_image("Enemy/Phoenix/PhoenixNormal.png")
        del_image("Enemy/Phoenix/PhoenixFast.png")
        del_image("Enemy/Phoenix/PhoenixDestroy.png")
        del_image("Enemy/Phoenix/PhoenixHit.png")
        del_image("Enemy/Phoenix/PhoenixAttack.png")
        del_image("Enemy/Phoenix/PhoenixShield.png")
        del_image("Enemy/Carrier/CarrierBase.png"),
        del_image("Enemy/Carrier/CarrierNormal.png"),
        del_image("Enemy/Carrier/CarrierDestroy.png"),
        del_image("Enemy/Carrier/CarrierHit.png"),
        del_image("Enemy/Carrier/CarrierAttack.png")
        del_image("Enemy/Interceptor/InterceptorBase.png"),
        del_image("Enemy/Interceptor/InterceptorIdle.png"),
        del_image("Enemy/Interceptor/InterceptorMove.png"),
        del_image("Enemy/Interceptor/InterceptorDestroy.png"),
        del_image("Enemy/Interceptor/InterceptorHit.png"),
        del_image("Enemy/Interceptor/InterceptorAttack.png")
