from irc import IRC
import threading
import g
import time
import configparser
import os


class TwitchIRC(IRC):
    def __init__(self, nick, password):
        super().__init__(nick, password)
        self.__channel = None
        os.makedirs("config", exist_ok=True)
        self.__config_timestamp = 0
        self.__points_per_second = 1.0
        self.__sub_bonus = 1.0
        self.__active_time = 600
        self.__max_points = -1
        self.__max_points_inactive = -1
        self.load_config()

    @property
    def channel(self):
        return self.__channel

    def start(self, channel):
        self.__channel = channel
        threading.Thread(target=self.run).start()
        threading.Thread(target=self.__update_points).start()

    def load_config(self, *, write=True):
        cp = configparser.ConfigParser()
        try:
            cp.read_file(open("config/twitch.ini", "rt"))
        except FileNotFoundError:
            pass
        if not cp.has_section("twitch"):
            cp.add_section("twitch")

        self.__points_per_second = cp.getfloat("twitch", "points_per_second", fallback=self.__points_per_second)
        cp.set("twitch", "points_per_second", str(self.__points_per_second))

        self.__sub_bonus = cp.getfloat("twitch", "sub_bonus", fallback=self.__sub_bonus)
        cp.set("twitch", "sub_bonus", str(self.__sub_bonus))

        self.__active_time = cp.getfloat("twitch", "active_time", fallback=self.__active_time)
        cp.set("twitch", "active_time", str(self.__active_time))

        self.__max_points = cp.getfloat("twitch", "max_points", fallback=self.__max_points)
        cp.set("twitch", "max_points", str(self.__max_points))

        self.__max_points_inactive = cp.getfloat("twitch", "max_points_inactive", fallback=self.__max_points_inactive)
        cp.set("twitch", "max_points_inactive", str(self.__max_points_inactive))

        if write:
            cp.write(open("config/twitch.ini", "wt"))

        self.__config_timestamp = os.stat("config/twitch.ini").st_mtime

    def on_server_connected(self):
        self.join(self.__channel)

    def on_wisper_message(self, user, message):
        reply = self.__handle_message(user, message)
        if reply is not None:
            self.whisper(self.__channel, user, reply)

    def on_channel_message(self, channel, user, message):
        reply = self.__handle_message(user, message)
        if reply is not None:
            self.message(channel, f"{user['nick']}: {reply}")

    def __handle_message(self, user, message):
        if not message.startswith("!"):
            return None
        if message == "!points":
            return f"has {int(user.get('points', 0))} points"
        action_name, _, params = message[1:].partition(" ")
        game = g.instance.game
        if not game:
            return f"No game found for action {action_name}"
        act = game.find_action(action_name)
        if act is None:
            return f"Action {action_name} not found"
        if act.busy:
            return f"{act.id} is still busy"
        if act.cost > user.get("points", 0):
            return f"Not enough points for {act.id} ({int(user.get('points', 0))}/{act.cost})"
        user["points"] = user.get("points", 0) - act.cost
        g.instance.game.run_action(act, params)
        return f"Executing {act.id} ({int(user.get('points', 0))} points left)"

    def __update_points(self):
        t0 = time.monotonic()
        while True:
            time.sleep(1)
            t1 = time.monotonic()
            time_delta = (t1 - t0)
            t0 = t1
            for nick, user in self.get_users().items():
                if not user.get("online"):
                    continue
                max_points = self.__max_points_inactive
                if (time.monotonic() - (user.get("last_activity", 0) or 0)) < self.__active_time or max_points < 0:
                    max_points = self.__max_points
                if max_points < 0:
                    max_points = float("inf")
                points_delta = time_delta * self.__points_per_second
                if user.get("subscriber", "0") == "1":
                    points_delta += time_delta * self.__sub_bonus
                if user.get("points", 0) < max_points:
                    user["points"] = min(max_points, user.get("points", 0.0) + points_delta)

            try:
                if os.stat("config/twitch.ini").st_mtime != self.__config_timestamp:
                    self.load_config(write=False)
            except FileNotFoundError:
                pass

    @property
    def users(self):
        return sorted(
            filter(lambda user: (time.monotonic() - (user.get("last_activity", 0) or 0)) < self.__active_time, self.get_users().values()),
            key=lambda user: -user.get("points", 0.0)
        )
