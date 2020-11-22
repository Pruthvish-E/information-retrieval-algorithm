import time
from utils import colorize

def timer_decorator(fn):
    """timer_decorator.
    A decorator to print the time taken for a function call.
    :param fn: A function.
    """
    def wrapper(*param):
        start_ns = time.time()
        res = fn(*param)
        end_ns = time.time()

        print(
            colorize.blue("Time taken to run %s : %.4f s"%(fn.__name__, end_ns-start_ns))
            )
        return res
    return wrapper

def timer(fn):
    """time.
    A decorator that returns the function execution time along with the original return values.

    :param fn: A function.
    """
    def wrapper(*param):
        start_ns = time.time()
        res = fn(*param)
        end_ns = time.time()

        print(
            colorize.blue("Time taken to run %s : %.4f s"%(fn.__name__, end_ns-start_ns))
            )
        return res, (end_ns-start_ns)
    return wrapper


