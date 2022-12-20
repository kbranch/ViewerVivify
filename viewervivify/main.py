import flask
import g
import requests
import json


app = flask.Flask(__name__)


@app.route("/")
def get_index():
    flask.g.twitch = g.instance.irc
    return flask.render_template("index.html")


@app.route("/info")
def get_info():
    return flask.render_template("info.html")


@app.route("/info/<info_type>")
def get_info_content(info_type):
    flask.g.twitch = g.instance.irc
    flask.g.game = g.instance.game

    return flask.render_template(f"info_{info_type}.html")


@app.route("/api/points")
def get_points():
    flask.g.twitch = g.instance.irc
    flask.g.game = g.instance.game

    points = {}

    for user in flask.g.twitch.users:
        points[user.get("nick")] = user.get("points")

    response = app.response_class(
        response=json.dumps(points),
        status=200,
        mimetype='application/json'
    )

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


@app.route("/api/actions")
def get_actions():
    flask.g.twitch = g.instance.irc
    flask.g.game = g.instance.game

    response = app.response_class(
        response=json.dumps(flask.g.game.get_actions()),
        status=200,
        mimetype='application/json'
    )

    response.headers.add('Access-Control-Allow-Origin', '*')

    return response


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

