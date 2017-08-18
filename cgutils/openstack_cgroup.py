import cgroup
import fileops
import os

class NoSuchKVMError(Exception):
    pass
class ValOutofRanege(Exception):
    pass
class kvmCgroup(cgroup.CGroup):
    def __init__(self, kvmname, subsystem):
        if kvmname.find("-") != -1:
            kvmname = kvmname.split('-')[1]
        self.kvmname = kvmname
        subsystemPath = os.path.join(cgroup.SubsystemStatus().paths[subsystem], "machine.slice")
        fullPath = fileops.find(kvmname, subsystemPath)
        if not fullPath:
            self.cgroup = False
            raise NoSuchKVMError("No such vm found: " + kvmname)
        else:
            self.cgroup = True
            subsys = cgroup._get_subsystem(subsystem)
            print fullPath
            cgroup.CGroup.__init__(self, subsys, fullPath)

class kvmCpuLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'cpu')
    def cpulimit(self, kvmname, percentage):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
#         if int(percentage) < 0 or int(percentage) > 100:
#             raise ValOutofRanege("The percentage value out of range:  " + percentage)
        current_cpu_num = os.popen('virsh dominfo %s | grep CPU | head -n 1 | awk \'{print $2}\'' %(kvmname)).readlines()[0].strip()
        setval = 100000 / (float(current_cpu_num) / (float(percentage) / 100))
        print os.popen('virsh schedinfo %s --set vcpu_quota=%s' %(kvmname, int(setval))).readlines()
#         self.set_config('cfs_quota_us', 1000*int(percentage))
    def cpuunset(self, kvmname):
        print os.popen('virsh schedinfo %s --set vcpu_quota=%s' %(kvmname, "-1")).readlines()
        
class kvmCpuPriority(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'cpu')
    def cpuPriority(self, kvmname, priority):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
        print os.popen('virsh schedinfo %s --set cpu_shares=%s' %(kvmname, priority)).readlines()
    def cpuunsetPriority(self, kvmname):
        current_cpu_num = os.popen('virsh dominfo %s | grep CPU | head -n 1 | awk \'{print $2}\'' %(kvmname)).readlines()[0].strip()
        os.popen('virsh schedinfo %s --set cpu_shares=%s' %(kvmname, "%s" %(int(current_cpu_num) * 1024)))

class kvmCpusetLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'cpuset')
    def cpusetlimit(self, cpuset):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
        print cpuset
        params = self.get_default_configs()
        cpuseq = params['cpus']
        print cpuseq
        cpunum = int(cpuseq.split('-')[1])
        print cpunum
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
        print 11111111
        self.set_config('cpus', cpuset)
    def cpusetunset(self):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
        params = self.subsystem.get_default_configs()
        cpuseq = params['cpus']
        self.set_config('cpus', cpuseq)

class kvmMemLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'memory')
    def memlimit(self, memory):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
        params = self.get_default_configs()
        memmax = int(params['limit_in_bytes'])
        memory = int(memory)
        if memory > memmax:
            raise ValOutofRanege("Memory out of range: " + memory)
        self.set_config('limit_in_bytes', memory)
    def memunset(self):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
        self.set_config('limit_in_bytes', -1)

class kvmMemMinGuaranteeLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'memory')
    def memlimit(self, kvmname, memory):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
        memory = int(memory) / 1024
        memmax = os.popen('virsh dominfo %s | grep Max | awk \'{print $3}\'' %(kvmname)).readlines()[0].strip()
        if memory > memmax:
            raise ValOutofRanege("Memory out of range: " + memory + " KB.")
        print os.popen('virsh memtune %s --min-guarantee %s --live' %(kvmname, memory)).readlines()
    def memunset(self, kvmname):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
        os.popen('virsh memtune %s --min-guarantee %s --live' %(kvmname, "-1")).readlines()

class kvmDiskLimit(kvmCgroup):
    def __init__(self, kvmname):
        kvmCgroup.__init__(self, kvmname, 'blkio')
    def diskreadlimit(self, val, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.read_bps_device', '%d:%d %d' %(major, minor, val))
        return True
    def diskreadunset(self, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.read_bps_device', '%d:%d 0' %(major, minor))
        return True
    def diskwritelimit(self, val, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.write_bps_device', '%d:%d %d' %(major, minor, val))
        return True
    def diskwriteunset(self, devpath='/var'):
        if not self.cgroup:
            raise NoSuchKVMError("No such vm found: " + self.kvmname)
            return False
        minor = int(os.stat(devpath).st_dev & 0xff)
        major = int(os.stat(devpath).st_dev >> 8 & 0xff)
        self.set_config('throttle.write_bps_device', '%d:%d 0' %(major, minor))
        return True