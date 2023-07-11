import json
import os
import signal


def timeout_handler(_, __):
    raise TimeoutError()


def to_jsonl(dict_data, file_path):
    with open(file_path, 'a') as file:
        json_line = json.dumps(dict_data)
        file.write(json_line + os.linesep)


def function_with_timeout(func, args, timeout):
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)

    try:
        result = func(*args)
    finally:
        signal.alarm(0)

    return result
