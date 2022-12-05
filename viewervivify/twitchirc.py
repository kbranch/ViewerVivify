from irc import IRC
import threading
import g
import time


POINTS_PER_SECOND = 1.0
SUB_BONUS = 1.0
ONLINE_LIST_TIME = 600


class TwitchIRC(IRC):
    def __init__(self, nick, password):
        super().__init__(nick, password)
        self.__channel = None

    @property
    def channel(self):
        return self.__channel

    def start(self, channel):
        self.__channel = channel
        threading.Thread(target=self.run).start()
        threading.Thread(target=self.__update_points).start()

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
        game = g.instance.game
        if not game:
            return f"No game found for action {message[1:]}"
        act = game.find_action(message[1:])
        if act is None:
            return f"Action {message[1:]} not found"
        if act.busy:
            return f"{act.id} is still busy"
        if act.cost > user.get("points", 0):
            return f"Not enough points for {act.id} ({int(user.get('points', 0))}/{act.cost})"
        user["points"] = user.get("points", 0) - act.cost
        g.instance.game.run_action(act)
        return f"Executing {act.id}"

    def __update_points(self):
        t0 = time.monotonic()
        while True:
            time.sleep(1)
            t1 = time.monotonic()
            points_delta = (t1 - t0) * POINTS_PER_SECOND
            t0 = t1
            for nick, user in self.get_users().items():
                if user.get("online"):
                    user["points"] = user.get("points", 0.0) + points_delta
                    if user.get("subscriber", "0") == "1":
                        user["points"] = user.get("points", 0.0) + points_delta * SUB_BONUS

    @property
    def users(self):
        return sorted(
            filter(lambda user: (time.monotonic() - (user.get("last_activity", 0) or 0)) < ONLINE_LIST_TIME, self.get_users().values()),
            key=lambda user: -user.get("points", 0.0)
        )
