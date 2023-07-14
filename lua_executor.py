from .executor_utils import function_with_timeout

from typing import List
from .executor_types import ExecuteResult, Executor


def exec_lua(code, timeout=5):
    import tempfile
    import subprocess

    with tempfile.NamedTemporaryFile(mode="w", suffix=".lua") as f:
        f.write(code)
        f.flush()
        proc = subprocess.Popen(
            ["lua", f.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            outs, errs = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()

        return outs.decode("utf-8"), errs.decode("utf-8")


class LuaExecutor(Executor):
    def execute(self, func: str, tests: List[str], timeout: int = 5) -> ExecuteResult:
        # Combine function code and assert statement
        imports = 'lu = require("luaunit")'
        exec_tests = 'os.exit( lu.LuaUnit.run() )'
        func_test_list = [
            f'{imports}\n{func}\n{test}\n{exec_tests}' for test in tests]

        # Run the tests and collect the results
        success_tests = []
        failed_tests = []
        is_passing = True
        num_tests = len(func_test_list)
        for i in range(num_tests):
            code = func_test_list[i]
            _, errs = exec_lua(code, timeout=timeout)
            # ex failed:
            # lua: /tmp/luaunit_test.lua:3: LuaUnit test FAILURE: expected: 2, actual: 1
            # TODO: this logic is not 100% correct. instead, we should just look for "actual: x", we 
            # don't care about expected.
            if errs:
                is_passing = False
                reason = ""
                if "LuaUnit test FAILURE" in errs:
                    reason = errs.split("LuaUnit test FAILURE: ")[1]
                failed_tests += [tests[i] + f" -- {reason}"]
            else:
                success_tests += [tests[i]]
        state = []
        for test in tests:
            if test in success_tests:
                state += [True]
            else:
                state += [False]

        state = tuple(state)

        feedback = "Tested passed:"
        for test in success_tests:
            feedback += f"\n{test}"
        feedback += "\n\nTests failed:"
        for test in failed_tests:
            feedback += f"\n{test}"

        return ExecuteResult(is_passing, feedback, state)

    def evaluate(self, name: str, func: str, test: str, timeout: int = 5) -> bool:
        """
        Evaluates the implementation on Human-Eval Lua.

        probably should be written in a dataset-agnostic way but not now
        """
        test = "\n".join(test.split("\n")[0:-2])
        test += "\ntest_humaneval()"
        test += "\nos.exit( lu.LuaUnit.run() )"
        code = f"{func}\n{test}"
        _, errs = exec_lua(code, timeout=timeout)
        print(errs)
        return errs == ""
