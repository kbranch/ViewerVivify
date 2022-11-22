import sched
import threading
import time


class Game:
    """ Base class for games.
            Each game exposes a set of functions for viewer actions.
    """
    def __init__(self):
        self.__actions = []
        for attr_name in dir(self):
            attr = getattr(self, attr_name)
            if hasattr(attr, "game_action"):
                self.__actions.append(attr)
        self.__actions.sort(key=lambda a: a.id)
        self.__sched = sched.scheduler()
        self.__running = True
        self.__thread = threading.Thread(target=self.__run_sched)
        self.__thread.start()
        self.__actions_busy = set()

    def shutdown(self):
        self.__running = False
        self.__thread.join()

    def get_actions(self):
        return self.__actions

    def run_action(self, name):
        for act in self.__actions:
            if act.id.lower() == name.lower() or act.name.lower() == name.lower():
                if act in self.__actions_busy:
                    return False
                self.__sched.enter(0, 0, lambda: act())
                if act.timeout_function:
                    self.__actions_busy.add(act)
                    self.__sched.enter(act.timeout_delay, 0, lambda: self.__action_timeout(act))
                return True
        return False

    def __action_timeout(self, act):
        act.timeout_function(self)
        self.__actions_busy.remove(act)

    def __run_sched(self):
        while self.__running:
            self.__sched.run(blocking=False)
            time.sleep(0.2)


def action(*, id, name, cost):
    """ Marks a function as game action.

    """
    def wrapper(f):
        f.game_action = True
        f.id = id
        f.name = name
        f.cost = cost
        f.timeout_delay = None
        f.timeout_function = None
        def timeout_decorator(delay):
            def timeout_wrapper(timeout_function):
                f.timeout_delay = delay
                f.timeout_function = timeout_function
                return timeout_function
            return timeout_wrapper
        f.timeout = timeout_decorator
        return f
    return wrapper
