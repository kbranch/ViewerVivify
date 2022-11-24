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
            if isinstance(attr, GameAction) and attr not in self.__actions:
                self.__actions.append(attr)
        self.__actions.sort(key=lambda a: a.id)
        self.__sched = sched.scheduler()
        self.__running = True
        self.__thread = threading.Thread(target=self.__run_sched)
        self.__thread.start()

    def shutdown(self):
        self.__running = False
        self.__thread.join()

    def get_actions(self):
        return self.__actions

    def run_action(self, name):
        for act in self.__actions:
            if act.id.lower() == name.lower() or act.name.lower() == name.lower():
                if act.busy:
                    return False
                self.__sched.enter(0, 0, lambda: act.function(self))
                if act.timeout_function:
                    act.busy = True
                    if act.repeat_function:
                        self.__sched.enter(act.repeat_delay, 0, lambda: self.__action_repeat(act))
                    self.__sched.enter(act.timeout_delay, 0, lambda: self.__action_timeout(act))
                return True
        return False

    def __action_repeat(self, act):
        if act.busy:
            act.repeat_function(self)
            self.__sched.enter(act.repeat_delay, 0, lambda: self.__action_repeat(act))

    def __action_timeout(self, act):
        act.timeout_function(self)
        act.busy = False

    def __run_sched(self):
        while self.__running:
            try:
                self.__sched.run(blocking=False)
            except:
                import traceback
                traceback.print_exc()
            time.sleep(0.2)


class GameAction:
    def __init__(self, function, id, name, cost):
        self.function = function
        self.id = id
        self.name = name
        self.cost = cost
        self.timeout_delay = None
        self.timeout_function = None
        self.repeat_delay = None
        self.repeat_function = None
        self.busy = False

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


def action(*, id, name, cost):
    """ Marks a function as game action.
    """
    def wrapper(f):
        return GameAction(f, id, name, cost)
    return wrapper
