import cProfile
import sys
import time


def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        a = func(*args, **kwargs)
        print("--- %s seconds ---" % (time.time() - start_time))
        return a

    return wrapper


def profile(func):
    """Decorator for run function profile"""

    def wrapper(*args, **kwargs):
        profile_filename = func.__name__ + '.prof'
        profiler = cProfile.Profile()
        result = profiler.runcall(func, *args, **kwargs)
        profiler.dump_stats(profile_filename)
        return result

    return wrapper


# TODO Доделать обработчик ошибок по статье https://habr.com/ru/post/74875/
def catch(method=None, message: str = None, *args, **kwargs):
    if method:
        if not message:
            message = 'Error: '
        else:
            pass
        if not isinstance(message, str):
            raise TypeError('Текст сообщения должен быть строкой')
        try:
            return method(*args, **kwargs)
        except exceptions:
            quit(message, *args, **kwargs)


def wrap(method, message, exceptions=(IOError, OSError)):
    def fn(*args, **kwargs):
        return catch(method, message, exceptions, *args, **kwargs)

    return fn


def get_size(obj, seen=None):
    # From https://goshippo.com/blog/measure-real-size-any-python-object/
    # Recursively finds size of objects
    size = sys.getsizeof(obj)
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return 0

    # Important mark as seen *before* entering recursion to gracefully handle
    # self-referential objects
    seen.add(obj_id)
    if isinstance(obj, dict):
        size += sum([get_size(v, seen) for v in obj.values()])
        size += sum([get_size(k, seen) for k in obj.keys()])
    elif hasattr(obj, '__dict__'):
        size += get_size(obj.__dict__, seen)
    elif hasattr(obj, '__iter__') and not isinstance(obj,
                                                     (str, bytes, bytearray)):
        size += sum([get_size(i, seen) for i in obj])
    return size
