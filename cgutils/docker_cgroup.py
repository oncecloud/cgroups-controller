import cgroup
import fileops
import os

class NoSuchDockerError(Exception):
    pass
class ValOutofRanege(Exception):
    pass
class dockerCgroup(cgroup.CGroup):
    def __init__(self, dockerid, subsystem):
        self.dockerid = dockerid
        subsystemPath = cgroup.SubsystemStatus().paths[subsystem]
        fullPath = fileops.find(dockerid, subsystemPath)
        if not fullPath:
            self.cgroup = False
            raise NoSuchDockerError("No such docker found: " + dockerid)
        else:
            self.cgroup = True
            subsys = cgroup._get_subsystem(subsystem)
            cgroup.CGroup.__init__(self, subsys, fullPath)

class dockerCpuLimit(dockerCgroup):
    def __init__(self, dockerid):
        dockerCgroup.__init__(self, dockerid, 'cpu')
    def cpulimit(self, percentage):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
        if int(percentage) < 0 or int(percentage) > 100:
            raise ValOutofRanege("The percentage value out of range:  " + percentage)
        self.set_config('cfs_period_us', 100*int(percentage))
    def cpuunset(self):
        self.set_config('cfs_period_us', 10000)

class dockerCpusetLimit(dockerCgroup):
    def __init__(self, dockerid):
        dockerCgroup.__init__(self, dockerid, 'cpuset')
    def cpusetlimit(self, cpuset):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
        params = self.get_default_configs()
        cpuseq = params['cpus']
        cpunum = int(cpuseq.split('-')[1])
        if cpunum < 1:
            raise Exception("Cpu number is wrong")
        for cpus in cpuset.split(','):
            if '-' in cpus:
                up, down = cpus.split('-')
                up, down = int(up), int(down)
                if up > down or up < 0 or down < 0 or up > cpunum or down > cpunum:
                    raise Exception("Wrong in cpuset: " + cpuset)
            else:
                if int(cpus) > cpunum:
                    raise Exception("Wrong in cpuset: " + cpuset)
        self.set_config('cpus', cpuset)
    def cpusetunset(self):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
        params = self.subsystem.get_default_configs()
        cpuseq = params['cpus']
        self.set_config('cpus', cpuseq)

class dockerMemLimit(dockerCgroup):
    def __init__(self, dockerid):
        dockerCgroup.__init__(self, dockerid, 'memory')
    def memlimit(self, memory):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
        params = self.get_default_configs()
        memmax = int(params['limit_in_bytes'])
        memory = int(memory)
        if memory > memmax:
            raise ValOutofRanege("Memory out of range: " + memory)
        self.set_config('limit_in_bytes', memory)
    def memunset(self):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
        self.set_config('limit_in_bytes', -1)

class dockerDiskLimit(dockerCgroup):
    def __init__(self, dockerid):
        dockerCgroup.__init__(self, dockerid, 'blkio')
    def diskreadlimit(self, val, devpath='/var'):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.read_bps_device', '%d:%d %d' %(major, minor, val))
        return True
    def diskreadunset(self, devpath='/var'):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.read_bps_device', '%d:%d 0' %(major, minor))
        return True
    def diskwritelimit(self, val, devpath='/var'):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.write_bps_device', '%d:%d %d' %(major, minor, val))
        return True
    def diskwriteunset(self, devpath='/var'):
        if not self.cgroup:
            raise NoSuchDockerError("No such docker found: " + self.dockerid)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.write_bps_device', '%d:%d 0' %(major, minor))
        return True



