import os
import shutil
import shlex
import stat
import tempfile
import subprocess
import weakref


class LimitRunBuilder:
    nobody = 65534
    template = 'lrun --uid {uid} --gid {gid} --network {network} --remount-dev {remount_dev} ' \
               '--reset-env {reset_env} --max-nprocess {max_nprocess} --max-cpu-time {max_cpu_time} ' \
               '--max-real-time {max_real_time} --max-memory {max_memory} --max-output {max_output} ' \
               '--no-new-privs {no_new_privs}'

    def __init__(self, max_cpu_time, max_real_time, max_memory, max_output, max_nprocess=1, remount_dev=False,
                 reset_env=True, network=False, uid=nobody, gid=nobody, syscalls=None, no_new_privileges=True):
        self.args = {
            'max_cpu_time': max_cpu_time / 1000,
            'max_real_time': max_real_time / 1000,
            'max_memory': max_memory * 1024,
            'max_output': max_output * 1024,
            'max_nprocess': max_nprocess,
            'remount_dev': int(remount_dev),
            'reset_env': int(reset_env),
            'network': int(network),
            'no_new_privs': int(no_new_privileges),
            'uid': uid,
            'gid': gid
        }
        self.command = ''
        self.root = None
        self.dir = None
        self.fs = []
        self.env = []
        self.syscalls = syscalls
        self.stdin = None
        self.stdout = None
        self.stderr = None
        self.statout = None

    def chroot(self, path):
        self.root = path

    def chdir(self, path):
        self.dir = path

    def bindfs(self, source, destination, read_only=True):
        self.fs.append((source, destination, read_only))

    def add_env(self, key, value):
        self.env.append((key, value))

    def set_command(self, command):
        self.command = command

    def redirect_stdin(self, fd):
        self.stdin = fd

    def redirect_stdout(self, fd):
        self.stdout = fd

    def redirect_stderr(self, fd):
        self.stderr = fd

    def redirect_stat(self, fd):
        self.statout = fd

    def build(self):
        command = self.template.format(**self.args)
        for tp in self.fs:
            if tp[2]:
                command += ' --bindfs-ro {dest} {src}'.format(dest=tp[1], src=tp[0])
            else:
                command += ' --bindfs {dest} {src}'.format(dest=tp[1], src=tp[0])
        for env_pair in self.env:
            command += ' --env {key} {value}'.format(key=env_pair[0], value=env_pair[1])
        if self.root:
            command += ' --chroot {root}'.format(root=self.root)
        if self.dir:
            command += ' --chdir {dir}'.format(dir=self.dir)
        if self.syscalls:
            command += ' --syscalls {syscalls}'.format(syscalls=self.syscalls)
        command += ' -- ' + self.command
        if self.stdin:
            command += ' 0<{fd}'.format(fd=self.stdin)
        if self.stdout:
            command += ' 1>{fd}'.format(fd=self.stdout)
        if self.stderr:
            command += ' 2>{fd}'.format(fd=self.stderr)
        if self.statout:
            command += ' 3>{fd}'.format(fd=self.statout)
        return command


class LimitRunContext:
    """
    Upon exiting the context, the directory and everything contained
    in it are removed.

    Notice:
    Bindfs two folder dependencies which one is prefix of another may cause lrun crash, for example, '/usr/lib/' and
    '/usr/lib/jvm/'
    """
    def __init__(self, dependencies):
        self.temporary_directory = tempfile.mkdtemp(prefix='lrun_')
        st = os.stat(self.temporary_directory)
        os.chmod(self.temporary_directory, st.st_mode | stat.S_IROTH | stat.S_IXOTH)
        # os.chdir(self.temporary_directory)
        self.file_dependencies = set()
        self.dir_dependencies = set()
        self._build_dependencies(dependencies)
        self.symlinks = set()
        self.writable_folders = set()
        self.env = dict()

        self._finalizer = weakref.finalize(self, self._cleanup, path=self.temporary_directory)

    def real_path(self, path):
        return os.path.join(self.temporary_directory, path[1:])

    def _build_dependencies(self, dependencies):
        dirs = {'/proc', '/dev'}
        files = set()
        for dependency in dependencies:
            if os.path.isfile(dependency):
                abspath = os.path.abspath(dependency)
                dirs.add(os.path.dirname(abspath))
                files.add(abspath)
                self.file_dependencies.add((abspath, abspath))
            else:
                folder = os.path.abspath(dependency)
                dirs.add(folder)
                self.dir_dependencies.add((folder, folder))
        for path in dirs:
            os.makedirs(self.real_path(path), mode=0o775, exist_ok=True)
        for path in files:
            os.link(path, self.real_path(path))

    def add_dependency(self, source, destination=None):
        source = os.path.abspath(source)
        destination = destination if destination else source
        if os.path.isfile(source):
            if (source, destination) in self.file_dependencies:
                return
            os.makedirs(self.real_path(os.path.dirname(destination)), mode=0o775, exist_ok=True)
            os.link(source, self.real_path(destination))
            self.file_dependencies.add((source, destination))
        else:
            if (source, destination) in self.dir_dependencies:
                return
            os.makedirs(self.real_path(destination), mode=0o775, exist_ok=True)
            self.dir_dependencies.add((source, destination))

    def add_symlink(self, source, destination):
        src, dest = self.real_path(source), self.real_path(destination)
        # dest_dir = dest if os.path.isdir(src) else os.path.dirname(dest)
        dest_dir = os.path.dirname(dest)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir, mode=0o775, exist_ok=True)
        os.symlink(os.path.relpath(src, dest_dir), dest)
        self.symlinks.add((source, destination))

    def add_writable_folder(self, path):
        real_path = self.real_path(path)
        os.makedirs(real_path, mode=0o777, exist_ok=True)
        # On some systems, mode is ignored. Where it is used, the current umask value is first masked out.
        # So change mode explicitly
        os.chmod(real_path, 0o777)
        self.writable_folders.add(path)

    def set_env(self, env):
        self.env = env

    def add_env(self, key, value):
        self.env[key] = value

    def run_command(self, command, limits, redirect_stdin=None, redirect_stdout=None, redirect_stderr=None, chdir=None,
                    stdin=None, stdout=None, stderr=None, timeout=180):
        lrb = LimitRunBuilder(**limits)
        lrb.chroot(self.temporary_directory)
        path = chdir if chdir else '/'
        lrb.chdir(path)
        for dir_dependency in self.dir_dependencies:
            lrb.bindfs(dir_dependency[0], self.real_path(dir_dependency[1]))
        for key, value in self.env.items():
            lrb.add_env(key, value)
        lrb.set_command(command)
        if redirect_stdin:
            lrb.redirect_stdin(shlex.quote(redirect_stdin))
        if redirect_stdout:
            lrb.redirect_stdout(shlex.quote(redirect_stdout))
        if redirect_stderr:
            lrb.redirect_stderr(shlex.quote(redirect_stderr))
        _, tmp_pathname = tempfile.mkstemp(prefix='lrun_stat_', text=True)
        lrb.redirect_stat(tmp_pathname)
        lrun_command = lrb.build()

        # print(lrun_command)

        stdio = dict()
        if stdin:
            stdio['stdin'] = stdin
        stdio['stdout'] = stdout if stdout else subprocess.PIPE
        stdio['stderr'] = stderr if stderr else subprocess.PIPE

        proc = subprocess.Popen(lrun_command, shell=True, universal_newlines=True, **stdio)
        try:
            outs, errs = proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            outs, errs = proc.communicate()
        return_code = proc.poll()
        if return_code:
            statistics = None
        else:
            with open(tmp_pathname) as f:
                output = f.read()
                statistics = self.parse_lrun_result(output)
        os.remove(tmp_pathname)
        return outs, errs, return_code, statistics

    @classmethod
    def _cleanup(cls, path):
        shutil.rmtree(path)

    def cleanup(self):
        if self._finalizer.detach():
            shutil.rmtree(self.temporary_directory)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    @staticmethod
    def parse_lrun_result(output):
        output = output.strip()
        info = dict([line.split() for line in output.split('\n')])
        try:
            info["MEMORY"] = int(info["MEMORY"]) / 1024
            info["CPUTIME"] = float(info["CPUTIME"]) * 1000
            info["REALTIME"] = float(info["REALTIME"]) * 1000
            info["SIGNALED"] = int(info["SIGNALED"])
            info["EXITCODE"] = int(info["EXITCODE"])
            info["TERMSIG"] = int(info["TERMSIG"])
        except (KeyError, ValueError):
            # log here
            pass
        return info

    @staticmethod
    def find_executable(name):
        return os.path.realpath(shutil.which(name))


def build_context(utility):
    if utility in ['gcc', 'g++']:
        real_path = LimitRunContext.find_executable(utility)
        context = LimitRunContext(['/lib', '/lib64', '/usr'])
        # context.add_dependency(real_path, '/usr/bin/' + utility)
        context.add_writable_folder('/workspace')
        context.set_env({'PATH': '/usr/bin'})
        return context
    elif utility in ['java', 'javac']:
        real_path = LimitRunContext.find_executable(utility)
        # jdk_path = os.path.abspath(os.path.dirname(real_path) + '/..')
        # context = LimitRunContext(['/lib', '/lib64', jdk_path])
        context = LimitRunContext(['/lib', '/lib64', '/usr/lib/'])
        context.add_symlink(real_path, '/usr/bin/' + utility)

        if utility == 'javac':
            context.add_writable_folder('/workspace')
            # if is javac context, add jar command as well
            jar_real_path = LimitRunContext.find_executable('jar')
            context.add_symlink(jar_real_path, '/usr/bin/' + 'jar')
        context.set_env({'PATH': '/usr/bin'})
        return context
    elif utility in ['python', 'python3']:
        real_path = LimitRunContext.find_executable(utility)
        context = LimitRunContext(['/lib', '/lib64', '/usr/lib'])
        context.add_dependency(real_path, '/usr/bin/' + utility)
        context.set_env({'PATH': '/usr/bin'})
        return context
    elif utility == 'c':
        return LimitRunContext(['/lib', '/lib64'])
    elif utility == 'cpp':
        return LimitRunContext(['/lib', '/lib64', '/usr/lib/'])
    else:
        return None
