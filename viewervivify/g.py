import findgame


instance = None


class Global:
    def __init__(self):
        self.__irc = None
        self.__game_finder = findgame.GameFinder()

    @property
    def game(self):
        return self.__game_finder.game

    @property
    def irc(self):
        return self.__irc

    def start_twitchirc(self, target_user):
        if self.__irc:
            self.__irc.shutdown()
        # TODO: Hardcoded oauth data
        from twitchirc import TwitchIRC
        self.__irc = TwitchIRC("Daid303bot", "oauth:5trzi4egxuu6paabmjkebdyq5grukz")
        self.__irc.start(target_user.lower())
