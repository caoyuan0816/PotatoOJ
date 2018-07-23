import os
import re
import tempfile
import shutil
import subprocess
import shlex
from subprocess import DEVNULL, PIPE
from lrun import LimitRunContext, build_context
from config import config
from define import JudgeStatus, CodeLanguage
from data import pull_data


class JudgeClient:
    """
    JudgeClient, need root
    """
    def __init__(self, code, language, max_time, max_memory, data_id, special_judge=None):
        """
        :param code: 代码
        :param language: 代码语言
        :param max_time: 运行时间限制
        :param max_memory: 运行内存限制
        :param data_id: 题目数据的ID
        """
        self.uid = int(config['Judge']['uid'])
        self.gid = int(config['Judge']['gid'])
        self.code = code
        self.data_id = data_id
        self.data_dir = None
        self.compile_limits = {
            'max_cpu_time': config.getint('Judge', 'MaxCompileTime'),
            'max_real_time': config.getint('Judge', 'MaxCompileTime'),
            'max_memory': config.getint('Judge', 'MaxCompileMemory'),
            'max_output': config.getint('Judge', 'MaxCompileOutput'),
            'max_nprocess': 30
        }
        self.run_limits = {
            'max_cpu_time': max_time,
            'max_real_time': max_time,
            'max_memory': max_memory,
            'max_output': config.getint('Judge', 'MaxOutputLimit'),
            'max_nprocess': 1,
            'syscalls': config.get('Syscalls', language.name)
        }
        self.special_judge = special_judge
        self.spj_execute = None
        self.judge_limits = {
            'max_cpu_time': config.getint('Judge', 'MaxJudgeTime'),
            'max_real_time': config.getint('Judge', 'MaxJudgeTime'),
            'max_memory': config.getint('Judge', 'MaxJudgeMemory'),
            'max_output': config.getint('Judge', 'MaxJudgeOutput'),
            'max_nprocess': 20,
            'syscalls': config.get('Syscalls', language.name)
        }

    def get_test_cases(self):
        in_files = []
        out_files = []
        for entry in os.listdir(self.data_dir):
            entry = os.path.join(self.data_dir, entry)
            # exclude symbolic links for safe reason
            if os.path.isfile(entry) and not os.path.islink(entry):
                basename = os.path.basename(entry)
                # not hided files
                if not basename.startswith('.'):
                    if basename.endswith('.in'):
                        in_files.append(basename[:-3])
                    elif basename.endswith('.out'):
                        out_files.append(basename[:-4])
        return sorted(set(in_files).intersection(out_files))

    def build_special_judge(self, source, target):
        if self.special_judge['language'] in clientMap:
            client = clientMap[self.special_judge['language']]
        else:
            return {'status': JudgeStatus.SystemError, 'info': 'Special Judge Unknown language'}
        instance = client(self.special_judge['code'], self.special_judge['language'], 0, 0, None)
        result = instance.compile(source, target)
        if result:
            return {'status': JudgeStatus.SystemError, 'info': 'Special Judge compile error'}
        return None

    def compile(self, source, target):
        pass

    def run(self, execute, in_file, out_file):
        pass

    def judge_run(self, execute, in_file, out_file, real_out_file):
        pass

    def judge(self, in_file, out_file, real_out_file):
        # Create real_out_file in case it doesn't exist, because in some cases program run doesn't generate any output
        open(real_out_file, 'a').close()

        if not self.special_judge:
            # diff, ignore blank line, spaces and case
            args = ['diff', '-qBbi', '--strip-trailing-cr', out_file, real_out_file]
            if subprocess.call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL):
                return {'status': JudgeStatus.WrongAnswer}
            # full diff
            # args = ['diff', '-q', '--strip-trailing-cr', out_file, real_out_file]
            # Solution from http://superuser.com/q/388276
            args = r"diff -q --strip-trailing-cr <(sed -e '$a\' {}) <(sed -e '$a\' {})"\
                .format(shlex.quote(out_file), shlex.quote(real_out_file))
            proc = subprocess.Popen(args, stdout=DEVNULL, stderr=PIPE, shell=True, executable='/bin/bash')
            outs, errs = proc.communicate()
            return_code = proc.poll()
            # Due to "It is not possible to obtain the exit code of a process substitution command from the shell that
            # created the process substitution", we need to check stderr too.
            if return_code or errs:
                return {'status': JudgeStatus.PresentationError}
            else:
                return {'status': JudgeStatus.Accepted}
        else:
            # special judge
            client = clientMap[self.special_judge['language']]
            instance = client(self.special_judge['code'], self.special_judge['language'], 0, 0, None)
            outs = instance.judge_run(self.spj_execute, in_file, out_file, real_out_file)
            if outs is None:
                return {'status': JudgeStatus.SystemError, 'info': "Special Judge runtime error"}
            outs = outs.strip().lower()
            if outs == 'accepted':
                return {'status': JudgeStatus.Accepted}
            elif outs == 'wronganswer':
                return {'status': JudgeStatus.WrongAnswer}
            elif outs == 'presentationerror':
                return {'status': JudgeStatus.PresentationError}
            else:
                return {'status': JudgeStatus.SystemError, 'info': "Special Judge unknown result"}

    def process(self):
        yield {'status': JudgeStatus.Judging}
        with tempfile.TemporaryDirectory(prefix='judge_home_') as home:
            # print(home)
            source_file = os.path.join(home, 'source')
            with open(source_file, 'w') as f:
                f.write(self.code)
            os.chown(source_file, self.uid, self.gid)
            execute_file = os.path.join(home, 'target')
            yield {'status': JudgeStatus.Compiling}
            compile_result = self.compile(source_file, execute_file)
            if compile_result:
                yield compile_result
                return
            yield {'status': JudgeStatus.Running}
            if self.special_judge:
                judge_source_file = os.path.join(home, 'judge_source')
                with open(judge_source_file, 'w') as f:
                    f.write(self.special_judge['code'])
                os.chown(judge_source_file, self.uid, self.gid)
                self.spj_execute = os.path.join(home, 'spj_execute')
                result = self.build_special_judge(judge_source_file, self.spj_execute)
                if result:
                    yield result
                    return
            self.data_dir = pull_data(self.data_id)
            if self.data_dir is None:
                yield {'status': JudgeStatus.SystemError, 'info': 'Get problem data fail'}
                return
            time_record, memory_record = 0, 0
            for test_case in self.get_test_cases():
                fin = os.path.join(self.data_dir, test_case + '.in')
                fout = os.path.join(self.data_dir, test_case + '.out')
                real_out = os.path.join(home, test_case + '.real_out')
                run_result = self.run(execute_file, fin, real_out)
                if run_result['status'] is not None:
                    yield run_result
                    return
                # TODO: get time and memory info from run_result here
                print('time: {}, meomory: {}'.format(run_result['time'], run_result['memory']))
                if run_result['time'] > time_record:
                    time_record = run_result['time']
                if run_result['memory'] > memory_record:
                    memory_record = run_result['memory']

                judge_result = self.judge(fin, fout, real_out)
                if judge_result['status'] != JudgeStatus.Accepted:
                    yield judge_result
                    return
            yield {'status': JudgeStatus.Accepted, 'info': {'time': time_record, 'memory': memory_record}}
            return

    @staticmethod
    def parse_compile_result(outs, errs, return_code, stat):
        if return_code:
            return {'status': JudgeStatus.SystemError, 'info': 'lrun fail'}
        if stat['EXCEED'] in ['REAL_TIME', 'CPU_TIME']:
            return {'status': JudgeStatus.CompileError, 'info': 'Compile Time Limit Exceed'}
        if stat['EXCEED'] == 'MEMORY':
            return {'status': JudgeStatus.CompileError, 'info': 'Compile Memory Limit Exceed'}
        if stat['EXITCODE'] or stat['SIGNALED'] or stat['TERMSIG']:
            return {'status': JudgeStatus.CompileError, 'info': errs}
        return None

    @staticmethod
    def parse_run_result(outs, errs, return_code, stat):
        if return_code:
            return {'status': JudgeStatus.SystemError, 'info': 'lrun fail'}
        if stat["EXCEED"] == 'MEMORY':
            return {'status': JudgeStatus.MemoryLimitExceeded}
        elif stat["EXCEED"] in ['CPU_TIME', 'REAL_TIME']:
            return {'status': JudgeStatus.TimeLimitExceeded}
        elif stat["EXCEED"] == 'OUTPUT':
            return {'status': JudgeStatus.OutputLimitExceeded}

        if stat['SIGNALED'] or stat['EXITCODE'] or stat['TERMSIG']:
            return {'status': JudgeStatus.RuntimeError, 'info': errs}
        return {'status': None, 'time': stat['REALTIME'], 'memory': stat["MEMORY"]}

    # def update_status(self, status):
    #     print(status)


class CJudgeClient(JudgeClient):
    def compile(self, source, target):
        with build_context('gcc') as context:
            context.add_dependency(source, '/workspace/main.c')
            compile_command = config['CompileCommand']['C'].format(source='main.c', execute='Main')
            result = context.run_command(compile_command, limits=self.compile_limits, chdir='/workspace')
            status = self.parse_compile_result(*result)
            if status:
                return status
            target = os.path.abspath(target)
            if os.path.exists(target):
                os.remove(target)
            os.link(context.real_path('/workspace/Main'), target)
            return None

    def run(self, execute, in_file, out_file):
        in_file = os.path.abspath(in_file)
        out_file = os.path.abspath(out_file)
        with build_context('c') as context:
            context.add_dependency(execute, '/main')
            result = context.run_command('./main', limits=self.run_limits,
                                         redirect_stdin=in_file, redirect_stdout=out_file)
            return self.parse_run_result(*result)

    def judge_run(self, execute, in_file, out_file, real_out_file):
        with build_context('c') as context:
            context.add_writable_folder('/workspace')
            context.add_dependency(in_file, '/workspace/in')
            context.add_dependency(out_file, '/workspace/out')
            context.add_dependency(real_out_file, '/workspace/real_out')
            context.add_dependency(execute, '/workspace/main')
            outs, errs, code, stat = context.run_command('./main in out real_out', limits=self.judge_limits,
                                                         chdir='/workspace')
            result = self.parse_run_result(outs, errs, code, stat)
            if result['status'] is None:
                return outs
            else:
                return None


class CPPJudgeClient(JudgeClient):
    def compile(self, source, target):
        with build_context('g++') as context:
            context.add_dependency(source, '/workspace/main.cpp')
            compile_command = config['CompileCommand']['CPP'].format(source='main.cpp', execute='Main')
            result = context.run_command(compile_command, limits=self.compile_limits, chdir='/workspace')
            status = self.parse_compile_result(*result)
            if status:
                return status
            target = os.path.abspath(target)
            if os.path.exists(target):
                os.remove(target)
            os.link(context.real_path('/workspace/Main'), target)
            return None

    def run(self, execute, in_file, out_file):
        in_file = os.path.abspath(in_file)
        out_file = os.path.abspath(out_file)
        with build_context('cpp') as context:
            context.add_dependency(execute, '/main')
            result = context.run_command('./main', limits=self.run_limits,
                                         redirect_stdin=in_file, redirect_stdout=out_file)
            return self.parse_run_result(*result)

    def judge_run(self, execute, in_file, out_file, real_out_file):
        with build_context('cpp') as context:
            context.add_writable_folder('/workspace')
            context.add_dependency(in_file, '/workspace/in')
            context.add_dependency(out_file, '/workspace/out')
            context.add_dependency(real_out_file, '/workspace/real_out')
            context.add_dependency(execute, '/workspace/main')
            outs, errs, code, stat = context.run_command('./main in out real_out', limits=self.judge_limits,
                                                         chdir='/workspace')
            result = self.parse_run_result(outs, errs, code, stat)
            if result['status'] is None:
                return outs
            else:
                return None


class JavaJudgeClient(JudgeClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.run_limits['max_nprocess'] = 20
        self.judge_limits['syscalls'] = None
        self.class_name = self.parse_public_class(self.code)

    def compile(self, source, target):
        if self.class_name is None:
            return {'status': JudgeStatus.CompileError, 'info': "Public Class Not Found"}
        with build_context('javac') as context:
            # self.class_name = self.parse_public_class(self.code)
            # if self.class_name is None:
                # return {'status': JudgeStatus.CompileError, 'info': "Public Class Not Found"}
            source_file = '{}.java'.format(self.class_name)
            context.add_dependency(source, '/workspace/' + source_file)
            compile_command = config['CompileCommand']['JAVA'].format(source=source_file)
            result = context.run_command(compile_command, limits=self.compile_limits, chdir='/workspace')
            status = self.parse_compile_result(*result)
            if status:
                return status
            # The default SecurityManager of Java does not forbid using Thread,
            # we define a subclass of java.lang.SecurityManager, ThreadSecurityManager(OJSecurityManager) to do that.
            # http://stackoverflow.com/questions/15868534/why-java-security-manager-doesnt-forbid-neither-creating-new-thread-nor-start/31039987#31039987
            context.add_dependency(os.path.join(os.path.dirname(__file__), '../conf/java/OJSecurityManager.class'),
                                   "/workspace/OJSecurityManager.class")
            class_files = []
            for file in os.listdir(context.real_path('/workspace')):
                if file.endswith('.class'):
                    # Add quote to filename, since java class file name maybe Main$InputReader.class, that cause shell
                    # unexpected result
                    class_files.append(shlex.quote(file))
            outs, errs, code, stat = context.run_command('jar -cf target.jar {}'.format(' '.join(class_files)),
                                                         limits=self.compile_limits, chdir='/workspace')
            if code or stat["EXITCODE"] or stat['EXCEED'] != "none" or stat['SIGNALED'] or stat['TERMSIG']:
                return {'status': JudgeStatus.CompileError, 'info': "Jar class file fail"}
            target = os.path.abspath(target)
            if os.path.exists(target):
                os.remove(target)
            os.link(context.real_path('/workspace/target.jar'), target)
            return None

    def run(self, execute, in_file, out_file):
        in_file = os.path.abspath(in_file)
        out_file = os.path.abspath(out_file)
        with build_context('java') as context:
            context.add_dependency(os.path.join(os.path.dirname(__file__), '../conf/java/java_run.policy'), '/java.policy')
            context.add_dependency(execute, '/target.jar')
            command = config['RunCommand']['JAVA'].format(execute='target.jar', name=self.class_name)
            result = context.run_command(command, limits=self.run_limits, redirect_stdin=in_file,
                                         redirect_stdout=out_file)
            return self.parse_run_result(*result)

    def judge_run(self, execute, in_file, out_file, real_out_file):
        with build_context('java') as context:
            context.add_writable_folder('/workspace')
            context.add_dependency(in_file, '/workspace/in')
            context.add_dependency(out_file, '/workspace/out')
            context.add_dependency(real_out_file, '/workspace/real_out')
            context.add_dependency(execute, '/workspace/target.jar')
            context.add_dependency(os.path.join(os.path.dirname(__file__), '../conf/java/java_judge.policy'),
                                   '/workspace/java.policy')
            command = "java -Djava.security.manager -Djava.security.policy=./java.policy -cp {jar} {name}" \
                      " in out real_out".format(jar='target.jar', name=self.class_name)
            outs, errs, code, stat = context.run_command(command, limits=self.judge_limits, chdir='/workspace')
            result = self.parse_run_result(outs, errs, code, stat)
            if result['status'] is None:
                return outs
            return None

    @staticmethod
    def parse_public_class(code):
        # remove all comment in Java code
        # Regex comes from http://stackoverflow.com/questions/2613432/remove-source-file-comments-using-intellij
        code = re.sub(r'(/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+/|[ \t]*//.*)', '', code)
        match = re.search(r"^\s*public\s+class\s+(\w+)", code, flags=re.M)
        if not match:
            return None
        return match.group(1)


class Py2JudgeClient(JudgeClient):
    def compile(self, source, target):
        shutil.copyfile(source, target)
        shutil.chown(target, self.uid, self.gid)

    def run(self, execute, in_file, out_file):
        in_file = os.path.abspath(in_file)
        out_file = os.path.abspath(out_file)
        with build_context('python') as context:
            context.add_dependency(execute, '/main.py')
            command = config['RunCommand']['PY2'].format(execute='main.py')
            result = context.run_command(command, limits=self.run_limits, redirect_stdin=in_file,
                                         redirect_stdout=out_file)
            return self.parse_run_result(*result)

    def judge_run(self, execute, in_file, out_file, real_out_file):
        with build_context('python') as context:
            context.add_writable_folder('/workspace')
            context.add_dependency(in_file, '/workspace/in')
            context.add_dependency(out_file, '/workspace/out')
            context.add_dependency(real_out_file, '/workspace/real_out')
            context.add_dependency(execute, '/workspace/main.py')
            command = 'python -S {execute} in out real_out'.format(execute='main.py')
            outs, errs, code, stat = context.run_command(command, limits=self.judge_limits, chdir='/workspace')
            result = self.parse_run_result(outs, errs, code, stat)
            if result['status'] is None:
                return outs
            return None


class Py3JudgeClient(JudgeClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # python3 runtime need /dev/urandom
        self.run_limits['remount_dev'] = True

    def compile(self, source, target):
        shutil.copyfile(source, target)
        shutil.chown(target, self.uid, self.gid)

    def run(self, execute, in_file, out_file):
        in_file = os.path.abspath(in_file)
        out_file = os.path.abspath(out_file)
        with build_context('python3') as context:
            context.add_dependency(execute, '/main.py')
            command = config['RunCommand']['PY3'].format(execute='main.py')
            result = context.run_command(command, limits=self.run_limits, redirect_stdin=in_file,
                                         redirect_stdout=out_file)
            return self.parse_run_result(*result)

    def judge_run(self, execute, in_file, out_file, real_out_file):
        with build_context('python3') as context:
            context.add_writable_folder('/workspace')
            context.add_dependency(in_file, '/workspace/in')
            context.add_dependency(out_file, '/workspace/out')
            context.add_dependency(real_out_file, '/workspace/real_out')
            context.add_dependency(execute, '/workspace/main.py')
            limits = self.judge_limits.copy()
            limits['remount_dev'] = True
            command = 'python3 -S {execute} in out real_out'.format(execute='main.py')
            outs, errs, code, stat = context.run_command(command, limits=limits, chdir='/workspace')
            result = self.parse_run_result(outs, errs, code, stat)
            if result['status'] is None:
                return outs
            return None


clientMap = {
    CodeLanguage.C: CJudgeClient,
    CodeLanguage.CPP: CPPJudgeClient,
    CodeLanguage.JAVA: JavaJudgeClient,
    CodeLanguage.PY2: Py2JudgeClient,
    CodeLanguage.PY3: Py3JudgeClient
}


def judge_client(code, language, max_time, max_memory, data_id, special_judge=None):
    language = CodeLanguage(language)
    client = clientMap[language]
    return client(code, language, max_time, max_memory, data_id, special_judge)
