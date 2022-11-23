from evilemu.emulator import Emulator
import os
import random
from game import Game, action


class LADXR(Game):
    @staticmethod
    def is_running(emulator: Emulator):
        header = emulator.read_rom(0x134, 0x10)
        return header == b'LADXR\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x80'

    def __init__(self, emulator: Emulator):
        super().__init__()
        assert self.is_running(emulator)
        self.__emulator = emulator

    @action(id="zol", name="Zol storm!", cost=100)
    def do_slime_rain(self):
        self.__emulator.write_ram8(0xDDF8 - 0xC000, 0xF0)
        self.__emulator.write_ram8(0xDDF7 - 0xC000, self.__emulator.read_ram8(0xDDF7 - 0xC000) | 0x01)

    @action(id="cucco", name="Cucco party!", cost=100)
    def do_cucco_party(self):
        self.__emulator.write_ram8(0xDDF8 - 0xC000, 0xF1)
        self.__emulator.write_ram8(0xDDF7 - 0xC000, self.__emulator.read_ram8(0xDDF7 - 0xC000) | 0x01)

    @action(id="power", name="Piece of power", cost=10)
    def do_pop(self):
        self.__emulator.write_ram8(0xDDF8 - 0xC000, 0xF2)
        self.__emulator.write_ram8(0xDDF7 - 0xC000, self.__emulator.read_ram8(0xDDF7 - 0xC000) | 0x01)

    @action(id="regen", name="Regenerate health", cost=100)
    def do_regen(self):
        self.__emulator.write_ram8(0xDB93 - 0xC000, 0xFF)

    @action(id="damage", name="Do 1 heart of damage", cost=20)
    def do_damage(self):
        self.__emulator.write_ram8(0xDB94 - 0xC000, 0x08)

    @action(id="gfxages", name="Ages girl graphics", cost=1000)
    def do_gfx_ages(self):
        self.do_gfx("AgesGirl")

    @action(id="gfxbowwow", name="Bowwow graphics", cost=1000)
    def do_gfx_bowwow(self):
        self.do_gfx("Bowwow")

    @action(id="gfxbunny", name="Bunny graphics", cost=1000)
    def do_gfx_bunny(self):
        self.do_gfx("Bunny")

    @action(id="gfxrandom", name="Random graphics", cost=1000)
    def do_gfx_random(self):
        gfx_list = [os.path.splitext(name)[0] for name in os.listdir("data/ladx") if os.path.splitext(name)[1] == ".bin"]
        self.do_gfx(random.choice(gfx_list))

    def do_gfx(self, name):
        gfx = open(f"data/ladx/{name}.bin", "rb").read()
        self.__emulator.write_rom(0x2C * 0x4000, gfx)

    @action(id="disablesword", name="Disable sword (60 seconds)", cost=500)
    def do_disable_sword(self):
        self.__emulator.write_rom16(0x129E + 2, 0x12ED)
        self.__emulator.write_rom8(0x1322, 0xFF)
    @do_disable_sword.timeout(60)
    def do_enable_sword(self):
        self.__emulator.write_rom16(0x129E + 2, 0x1528)
        self.__emulator.write_rom8(0x1322, 0x01)

    @action(id="disablebombs", name="Disable bombs (60 seconds)", cost=500)
    def do_disable_bombs(self):
        self.__emulator.write_rom16(0x129E + 4, 0x12ED)
    @do_disable_bombs.timeout(60)
    def do_enable_bombs(self):
        self.__emulator.write_rom16(0x129E + 4, 0x135A)

    @action(id="disablebow", name="Disable bow (60 seconds)", cost=500)
    def do_disable_bow(self):
        self.__emulator.write_rom16(0x129E + 10, 0x12ED)
    @do_disable_bow.timeout(60)
    def do_enable_bow(self):
        self.__emulator.write_rom16(0x129E + 10, 0x13BD)

    @action(id="disablehook", name="Disable hookshot (60 seconds)", cost=500)
    def do_disable_hook(self):
        self.__emulator.write_rom16(0x129E + 12, 0x12ED)
    @do_disable_hook.timeout(60)
    def do_enable_hook(self):
        self.__emulator.write_rom16(0x129E + 12, 0x1319)

    @action(id="disablerod", name="Disable magic rod (60 seconds)", cost=500)
    def do_disable_rod(self):
        self.__emulator.write_rom16(0x129E + 14, 0x12ED)
    @do_disable_rod.timeout(60)
    def do_enable_rod(self):
        self.__emulator.write_rom16(0x129E + 14, 0x12D8)

    @action(id="disableocarina", name="Disable ocarina (60 seconds)", cost=500)
    def do_disable_ocarina(self):
        self.__emulator.write_rom16(0x129E + 18, 0x12ED)
    @do_disable_ocarina.timeout(60)
    def do_enable_ocarina(self):
        self.__emulator.write_rom16(0x129E + 18, 0x41FC)

    @action(id="disablefeather", name="Disable feather (60 seconds)", cost=500)
    def do_disable_feather(self):
        self.__emulator.write_rom16(0x129E + 20, 0x12ED)
    @do_disable_feather.timeout(60)
    def do_enable_feather(self):
        self.__emulator.write_rom16(0x129E + 20, 0x14CB)

    @action(id="disableshovel", name="Disable shovel (60 seconds)", cost=500)
    def do_disable_shovel(self):
        self.__emulator.write_rom16(0x129E + 22, 0x12ED)
    @do_disable_shovel.timeout(60)
    def do_enable_shovel(self):
        self.__emulator.write_rom16(0x129E + 22, 0x12F8)

    @action(id="disablepowder", name="Disable magic powder (60 seconds)", cost=500)
    def do_disable_powder(self):
        self.__emulator.write_rom16(0x129E + 24, 0x12ED)
    @do_disable_powder.timeout(60)
    def do_enable_powder(self):
        self.__emulator.write_rom16(0x129E + 24, 0x148D)

    @action(id="disablerang", name="Disable boomerang (60 seconds)", cost=500)
    def do_disable_rang(self):
        self.__emulator.write_rom16(0x129E + 26, 0x12ED)
    @do_disable_rang.timeout(60)
    def do_enable_rang(self):
        self.__emulator.write_rom16(0x129E + 26, 0x1383)
