from .py_executor import PyExecutor
from .rs_executor import RsExecutor
from .executor_types import Executor
from .leet_executor import LeetExecutor


def executor_factory(lang: str, is_leet: bool = False) -> Executor:
    base = base_executor_factory(lang)
    if is_leet:
        return leet_executor_factory(lang)
    else:
        return base


def leet_executor_factory(lang: str) -> Executor:
    from .leetcode_env.leetcode_env.leetcode_types import ProgrammingLanguage
    from .leetcode_env.leetcode_env.utils import PySubmissionFormatter, RsSubmissionFormatter
    pl = None
    sf = None
    if lang == "py" or lang == "python":
        pl = ProgrammingLanguage.PYTHON3
        sf = PySubmissionFormatter
    elif lang == "rs" or lang == "rust":
        pl = ProgrammingLanguage.RUST
        sf = RsSubmissionFormatter
    else:
        raise ValueError(f"Invalid language for executor: {lang}")

    return LeetExecutor(pl, base_executor_factory(lang), sf)


def base_executor_factory(lang: str) -> Executor:
    if lang == "py" or lang == "python":
        return PyExecutor()
    elif lang == "rs" or lang == "rust":
        return RsExecutor()
    else:
        raise ValueError(f"Invalid language for executor: {lang}")
