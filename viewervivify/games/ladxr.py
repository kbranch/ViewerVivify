from evilemu.emulator import Emulator
import os
import random
import binascii
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

    @action(id="gfxages", name="AgesGirl graphics", cost=1000)
    def do_gfx_agesgirl(self):
        self.do_gfx("AgesGirl")

    @action(id="gfxbowwow", name="Bowwow graphics", cost=1000)
    def do_gfx_bowwow(self):
        self.do_gfx("Bowwow")

    @action(id="gfxbunny", name="Bunny graphics", cost=1000)
    def do_gfx_bunny(self):
        self.do_gfx("Bunny")

    @action(id="gfxgrandma", name="GrandmaUlrira graphics", cost=1000)
    def do_gfx_grandmaulrira(self):
        self.do_gfx("GrandmaUlrira")

    @action(id="gfxkirby", name="Kirby graphics", cost=1000)
    def do_gfx_kirby(self):
        self.do_gfx("Kirby")

    @action(id="gfxluigi", name="Luigi graphics", cost=1000)
    def do_gfx_luigi(self):
        self.do_gfx("Luigi")

    @action(id="gfxmarin", name="Marin graphics", cost=1000)
    def do_gfx_marin(self):
        self.do_gfx("Marin")

    @action(id="gfxalpha", name="MarinAlpha graphics", cost=1000)
    def do_gfx_alpha(self):
        self.do_gfx("MarinAlpha")

    @action(id="gfxmario", name="Mario graphics", cost=1000)
    def do_gfx_mario(self):
        self.do_gfx("Mario")

    @action(id="gfxmartha", name="Martha graphics", cost=1000)
    def do_gfx_martha(self):
        self.do_gfx("Martha")

    @action(id="gfxmatty", name="Matty_LA graphics", cost=1000)
    def do_gfx_matty(self):
        self.do_gfx("Matty_LA")

    @action(id="gfxmeme", name="Meme graphics", cost=1000)
    def do_gfx_meme(self):
        self.do_gfx("Meme")

    @action(id="gfxnes", name="NESLink graphics", cost=1000)
    def do_gfx_nes(self):
        self.do_gfx("NESLink")

    @action(id="gfxrichard", name="Richard graphics", cost=1000)
    def do_gfx_richard(self):
        self.do_gfx("Richard")

    @action(id="gfxrooster", name="Rooster graphics", cost=1000)
    def do_gfx_rooster(self):
        self.do_gfx("Rooster")

    @action(id="gfxrosa", name="Rosa graphics", cost=1000)
    def do_gfx_rosa(self):
        self.do_gfx("Rosa")

    @action(id="gfxsubrosian", name="Subrosian graphics", cost=1000)
    def do_gfx_subrosian(self):
        self.do_gfx("Subrosian")

    @action(id="gfxtarin", name="Tarin graphics", cost=1000)
    def do_gfx_tarin(self):
        self.do_gfx("Tarin")

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

    @action(id="invert", name="Invert buttons (60 seconds)", cost=500)
    def do_invert_dpad(self):
        self.__emulator.write_rom(0x2864, b'\xcb\x37\x2f\xe6\xf0\xb0\x47\x87\xe6\xaa\x4f\x78\x1f\xe6\x55\xb1\x00\x00\x00\x00')
    @do_invert_dpad.timeout(60)
    def do_normal_dpad(self):
        self.__emulator.write_rom(0x2864, b'\xf0\x00\xf0\x00\xf0\x00\xf0\x00\xf0\x00\xf0\x00\xf0\x00\xcb\x37\x2f\xe6\xf0\xb0')

    @action(id="green", name="Green link (color only)", cost=500)
    def do_color_green(self):
        self.__emulator.write_rom(0x1D8C, b'\x3E\x00\x00\x00\x00\x00\x00')
        self.__emulator.write_rom(0x1DD2, b'\x3E\x00\x00\x00\x00\x00\x00')

    @action(id="yellow", name="Yellow link (color only)", cost=500)
    def do_color_yellow(self):
        self.__emulator.write_rom(0x1D8C, b'\x3E\x01\x00\x00\x00\x00\x00')
        self.__emulator.write_rom(0x1DD2, b'\x3E\x01\x00\x00\x00\x00\x00')

    @action(id="red", name="Red link (color only)", cost=500)
    def do_color_red(self):
        self.__emulator.write_rom(0x1D8C, b'\x3E\x02\x00\x00\x00\x00\x00')
        self.__emulator.write_rom(0x1DD2, b'\x3E\x02\x00\x00\x00\x00\x00')

    @action(id="blue", name="Blue link (color only)", cost=500)
    def do_color_blue(self):
        self.__emulator.write_rom(0x1D8C, b'\x3E\x03\x00\x00\x00\x00\x00')
        self.__emulator.write_rom(0x1DD2, b'\x3E\x03\x00\x00\x00\x00\x00')

    @action(id="disco", name="Disco link (30 seconds, color only)", cost=500)
    def do_color_disco(self):
        self.__emulator.write_rom(0x1D8C, b'\x3E\x00\x00\x00\x00\x00\x00')
        self.__emulator.write_rom(0x1DD2, b'\x3E\x00\x00\x00\x00\x00\x00')
    @do_color_disco.repeat(0.1)
    def repeat_color_disco(self):
        color = random.randint(0, 7)
        self.__emulator.write_rom8(0x1D8D, color)
        self.__emulator.write_rom8(0x1DD3, color)
    @do_color_disco.timeout(30)
    def end_disco(self):
        self.__emulator.write_rom8(0x1D8D, 0)
        self.__emulator.write_rom8(0x1DD3, 0)
