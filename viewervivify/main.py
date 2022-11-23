import flask
from irc import IRC
import threading
import findgame


class VVIRC(IRC):
    def __init__(self, nick, password):
        super().__init__(nick, password)
        self.__channel = None

    @property
    def channel(self):
        return self.__channel

    def start(self, channel):
        self.__channel = channel
        threading.Thread(target=self.run).start()

    def on_server_connected(self):
        self.join(self.__channel)

    def on_channel_message(self, channel, user, message):
        if message.startswith("!"):
            if Global.instance.game.run_action(message[1:]):
                self.message(self.__channel, f"Executing {message[1:]}")
            else:
                self.message(self.__channel, f"Unknown action {message[1:]}")


class Global:
    instance = None

    def __init__(self):
        self.__irc = None
        self.__game_finder = findgame.GameFinder()

    @property
    def game(self):
        return self.__game_finder.game

    @property
    def irc(self):
        return self.__irc

    def start_twitch(self, target_user):
        if self.__irc:
            self.__irc.shutdown()
        # TODO: Hardcoded oauth data
        self.__irc = VVIRC("Daid303bot", "oauth:5trzi4egxuu6paabmjkebdyq5grukz")
        self.__irc.start(target_user.lower())


app = flask.Flask(__name__)


@app.route("/")
def get_index():
    flask.g.twitch = Global.instance.irc
    return flask.render_template("index.html")


@app.route("/info")
def get_info():
    return flask.render_template("info.html")


@app.route("/info_content")
def get_info_content():
    flask.g.twitch = Global.instance.irc
    flask.g.game = Global.instance.game
    return flask.render_template("info_content.html")


@app.route("/status")
def get_status():
    status = {}
    if Global.instance.game:
        status["game"] = {
            "name": Global.instance.game.__class__.__name__,
            "actions": [{"id": action.id, "name": action.name, "cost": action.cost, "busy": action.busy} for action in Global.instance.game.get_actions()],
        }
    if Global.instance.irc:
        status["twitch"] = {
            "connected": Global.instance.irc.is_connected,
            "channel": Global.instance.irc.channel,
        }
    return flask.jsonify(status)


@app.post("/twitch")
def connect_to_twitch():
    Global.instance.start_twitch(flask.request.form['twitchname'])
    return flask.redirect("/")


if __name__ == '__main__':
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    Global.instance = Global()
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000", autoraise=True)
    app.run(debug=True, use_reloader=False)
