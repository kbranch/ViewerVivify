import socket
import time


class IRC:
    def __init__(self, nick, password):
        self.__socket = None
        self.__nick = nick
        self.__password = password
        self.__recv_buffer = b''
        self.__running = True
        self.__users = {}

    @property
    def is_connected(self):
        return self.__socket is not None

    def get_users(self):
        return self.__users

    def run(self):
        while self.__running:
            if self.__socket is None:
                self.__socket = socket.socket()
                self.__socket.connect(("irc.chat.twitch.tv", 6667))
                self.__socket.sendall(f"PASS {self.__password}\r\nUSER {self.__nick}\r\nNICK {self.__nick}\r\n".encode('utf-8'))
                self.__recv_buffer = b''
            try:
                data = self.__socket.recv(1024)
            except IOError:
                data = b''
            if data == b'':
                self.__socket.close()
                self.__socket = None
                print("Disconnected from IRC, retry in 30 seconds")
                time.sleep(30)
                continue
            self.__recv_buffer += data
            while b'\r\n' in self.__recv_buffer:
                msg, self.__recv_buffer = self.__recv_buffer.split(b'\r\n', 1)
                msg = msg.decode("utf-8")
                tags = {}
                if msg.startswith("@"):
                    tags_string, msg = msg.split(" ", 1)
                    for tag in tags_string[1:].split(";"):
                        k, v = tag.split("=", 1)
                        tags[k] = v
                prefix = ""
                if msg.startswith(":"):
                    prefix, msg = msg[1:].split(" ", 1)
                    if "!" in prefix:
                        prefix = prefix[:prefix.find("!")]
                command, msg = msg.split(" ", 1)
                trailing = ""
                if ":" in msg:
                    msg, trailing = msg.split(":", 1)
                    msg = msg.strip()

                self.__handle(prefix, command, msg, trailing, tags)

    def shutdown(self):
        self.__running = False
        if self.__socket:
            self.__socket.close()

    def __handle(self, prefix, command, msg, trailing, tags):
        print(prefix, command, msg, trailing, tags)
        if command == "001":
            self.__nick = msg
            self.__socket.sendall("CAP REQ :twitch.tv/commands twitch.tv/tags twitch.tv/membership\r\n".encode("utf-8"))
            self.on_server_connected()
        elif command == "353":  # NAMES
            for nick in trailing.split(" "):
                self.__update_user(nick, {"online": True})
        elif command == "JOIN":
            self.__update_user(prefix, {"online": True})
        elif command == "PART":
            if prefix in self.__users:
                self.__update_user(prefix, {"online": False})
        elif command == "PING":
            pong = "PONG :" + trailing + "\r\n"
            self.__socket.sendall(pong.encode("utf-8"))
        elif command == "PRIVMSG":
            user = self.__update_user(prefix, tags)
            user["online"] = True
            if msg.startswith("#"):
                self.on_channel_message(msg[1:], user, trailing)
        elif command == "WHISPER":
            user = self.__update_user(prefix, tags)
            self.on_wisper_message(user, trailing)

    def join(self, channel):
        if self.__socket:
            self.__socket.sendall(f"JOIN #{channel}\r\n".encode("utf-8"))

    def message(self, channel, message):
        if self.__socket:
            self.__socket.sendall(f"PRIVMSG #{channel} :{message}\r\n".encode("utf-8"))

    def whisper(self, channel, user, message):
        if self.__socket:
            self.__socket.sendall(f"PRIVMSG {channel} :/w {user['nick']} {message}\r\n".encode("utf-8"))

    def send(self, channel, message):
        if self.__socket:
            self.__socket.sendall(f"PRIVMSG #{channel} :{message}\r\n".encode("utf-8"))

    def __update_user(self, username, tags):
        if username == self.__nick:
            return
        if username not in self.__users:
            self.__users[username] = {"nick": username}
        self.__users[username].update(tags)
        self.__users[username]["last_activity"] = time.monotonic()
        return self.__users[username]

    def on_server_connected(self):
        pass

    def on_channel_message(self, channel, user, message):
        pass

    def on_wisper_message(self, user, message):
        pass
