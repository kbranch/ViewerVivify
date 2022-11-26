import flask
import g
import requests


app = flask.Flask(__name__)


@app.route("/")
def get_index():
    flask.g.twitch = g.instance.irc
    return flask.render_template("index.html")


@app.route("/info")
def get_info():
    return flask.render_template("info.html")


@app.route("/info_content")
def get_info_content():
    flask.g.twitch = g.instance.irc
    flask.g.game = g.instance.game
    return flask.render_template("info_content.html")


@app.route("/status")
def get_status():
    status = {}
    if g.instance.game:
        status["game"] = {
            "name": g.instance.game.__class__.__name__,
            "actions": [{"id": action.id, "name": action.name, "cost": action.cost, "busy": action.busy} for action in Global.instance.game.get_actions()],
        }
    if g.instance.irc:
        status["twitch"] = {
            "connected": g.instance.irc.is_connected,
            "channel": g.instance.irc.channel,
        }
    return flask.jsonify(status)


@app.post("/twitch")
def connect_to_twitch():
    g.instance.start_twitchirc(flask.request.form['twitchname'])
    return flask.redirect("/")


if __name__ == '__main__':
    import logging
    logging.getLogger('werkzeug').setLevel(logging.ERROR)

    g.instance = g.Global()
    import webbrowser
    webbrowser.open("http://127.0.0.1:5000", autoraise=True)
    app.run(debug=True, use_reloader=False)
