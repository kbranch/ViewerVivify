import sched
import threading
import time
import configparser
import os


class Game:
    """ Base class for games.
            Each game exposes a set of functions for viewer actions.
    """
    def __init__(self):
        self.__actions = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if isinstance(attr, GameAction) and attr not in self.__actions:
                self.__actions.append(attr)
        self.__actions.sort(key=lambda a: (a.group, a.id))
        self.__sched = sched.scheduler()
        self.__running = True
        self.__thread = threading.Thread(target=self.__run_sched)
        self.__thread.start()
        self.__config_filename = ""
        self.__config_timestamp = 0

    def load_config(self, filename: str, *, write=True) -> None:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        cp = configparser.ConfigParser()
        try:
            cp.read_file(open(filename, "rt"))
        except FileNotFoundError:
            pass
        for action in self.__actions:
            if not cp.has_section(action.id):
                cp.add_section(action.id)
            action.cost = cp.getint(action.id, "cost", fallback=action.cost)
            cp.set(action.id, "cost", str(action.cost))
            action.cooldown_time = cp.getfloat(action.id, "cooldown", fallback=action.cooldown_time)
            cp.set(action.id, "cooldown", str(action.cooldown_time))

        if write:
            cp.write(open(filename, "wt"))
        self.__config_filename = filename
        self.__config_timestamp = os.stat(filename).st_mtime

    def shutdown(self):
        self.__running = False
        self.__thread.join()

    def get_actions(self):
        return self.__actions

    def find_action(self, name):
        for act in self.__actions:
            if act.id.lower() == name.lower() or act.name.lower() == name.lower():
                return act
        return None

    def run_action(self, act):
        act.busy = True
        self.__sched.enter(0, 0, lambda: self.__action_start(act))

    def __action_start(self, act):
        act.function(self)
        if act.timeout_function:
            if act.repeat_function:
                self.__sched.enter(act.repeat_delay, 0, lambda: self.__action_repeat(act))
            act.start_time = time.monotonic()
            self.__sched.enter(act.timeout_delay, 0, lambda: self.__action_timeout(act))
        elif act.cooldown_time > 0.0:
            self.__sched.enter(act.cooldown_time, 0, lambda: self.__action_cooldown(act))
        else:
            act.busy = False

    def __action_repeat(self, act):
        if act.busy:
            act.repeat_function(self)
            self.__sched.enter(act.repeat_delay, 0, lambda: self.__action_repeat(act))

    def __action_timeout(self, act):
        act.timeout_function(self)
        if act.cooldown_time > 0.0:
            self.__sched.enter(act.cooldown_time, 0, lambda: self.__action_cooldown(act))
        else:
            act.busy = False

    def __action_cooldown(self, act):
        act.busy = False

    def __run_sched(self):
        while self.__running:
            try:
                self.__sched.run(blocking=False)
            except:
                import traceback
                traceback.print_exc()
            time.sleep(0.2)
            try:
                if self.__config_filename and os.stat(self.__config_filename).st_mtime != self.__config_timestamp:
                    self.load_config(self.__config_filename, write=False)
            except FileNotFoundError:
                pass


class GameAction:
    def __init__(self, function, *, id, name, group="", cost=100, cooldown=0.0):
        self.function = function
        self.id = id
        self.name = name
        self.group = group
        self.cost = cost
        self.timeout_delay = 0.0
        self.timeout_function = None
        self.repeat_delay = 0.0
        self.repeat_function = None
        self.busy = False
        self.start_time = None
        self.cooldown_time = cooldown

    @property
    def progress(self):
        if self.start_time is None or self.timeout_delay == 0.0:
            return 0.0
        return min(1.0, max(0.0, (time.monotonic() - self.start_time) / self.timeout_delay))

    @property
    def cooldown(self):
        if self.start_time is None or self.cooldown_time == 0.0:
            return 0.0
        return min(1.0, max(0.0, (time.monotonic() - self.start_time - self.timeout_delay) / self.cooldown_time))

    def timeout(self, delay):
        def timeout_wrapper(timeout_function):
            self.timeout_delay = delay
            self.timeout_function = timeout_function
            return self
        return timeout_wrapper

    def repeat(self, delay):
        def repeat_wrapper(repeat_function):
            self.repeat_delay = delay
            self.repeat_function = repeat_function
            return self
        return repeat_wrapper


def action(**kwargs):
    """ Marks a function as game action.
    """
    def wrapper(f):
        return GameAction(f, **kwargs)
    return wrapper
