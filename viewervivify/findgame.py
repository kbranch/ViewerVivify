import evilemu
import threading
import time
from games.ladxr import LADXR

GAMES = [LADXR]


class GameFinder:
    def __init__(self):
        self.__thread = threading.Thread(target=self.__run)
        self.__thread.start()
        self.__active_game = None

    def __run(self):
        while True:
            for emu in evilemu.find_gameboy_emulators():
                for game in GAMES:
                    if game.is_running(emu):
                        self.__run_game(game, emu)
            time.sleep(5)

    def __run_game(self, game, emu):
        print("Found game:", game)
        self.__active_game = game(emu)
        self.__active_game.load_config(f"config/{game.__name__}.ini")
        try:
            while game.is_running(emu):
                time.sleep(1)
        except IOError:
            pass
        print("Game stopped")
        self.__active_game.shutdown()
        self.__active_game = None

    @property
    def game(self):
        return self.__active_game
