import kvm_cgroup
import docker_cgroup
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import subprocess
import os
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass
class MainHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        output = ''
        try:
            contentType = 'text/html'
            modules = self.path.split('/')
            if modules[1] == 'kvm':
                if modules[2] == 'cpu':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if len(vals) == 2:
                            cpu = kvm_cgroup.kvmCpuLimit(vals[0])
                            cpu.cpulimit(vals[1])
                    elif modules[3] == 'unset':
                        uncpu = kvm_cgroup.kvmCpuLimit(modules[4])
                        uncpu.cpuunset()
                    else:
                        self.send_error(404, "api not found")
                elif modules[2] == 'cpuset':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if len(vals) == 2:
                            cpuset = kvm_cgroup.kvmCpusetLimit(vals[0])
                            cpuset.cpusetlimit(vals[1])
                    elif modules[3] == 'unset':
                        uncpuset = kvm_cgroup.kvmCpusetLimit(modules[4])
                        uncpuset.cpusetunset()
                    else:
                        self.send_error(404, "api not found")
                elif modules[2] == 'memory':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if len(vals) == 2:
                            mem = kvm_cgroup.kvmMemLimit(vals[0])
                            mem.memlimit(vals[1])
                    elif modules[3] == 'unset':
                        unmem = kvm_cgroup.kvmMemLimit(modules[4])
                        unmem.memunset()
                    else:
                        self.send_error(404, "api not found")
                elif modules[2] == 'blkio':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if 2 < len(vals) < 5:
                            disk = kvm_cgroup.kvmDiskLimit(vals[0])
                            if vals[1] == 'read':
                                if len(vals)== 3:
                                    disk.diskreadlimit(int(vals[2]))
                                else:
                                    disk.diskreadlimit(int(vals[2]),vals[3])
                            elif vals[1] == 'write':
                                if len(vals) == 3:
                                    disk.diskwritelimit(int(vals[2]))
                                else:
                                    disk.diskwritelimit(int(vals[2]), vals[3])
                    elif modules[3] == 'unset':
                        vals = modules[4].split('&')
                        if 1 < len(vals) < 4:
                            undisk = kvm_cgroup.kvmDiskLimit(vals[0])
                            if vals[1] == 'read':
                                if len(vals) == 3:
                                    undisk.diskreadunset(vals[2])
                                else:
                                    undisk.diskreadunset()
                            if vals[1] == 'write':
                                if len(vals) == 3:
                                    undisk.diskreadunset(vals[2])
                                else:
                                    undisk.diskreadunset()
                    else:
                        self.send_error(404, "api not found")

            elif modules[1] == 'docker':
                if modules[2] == 'cpu':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if len(vals) == 2:
                            cpu = docker_cgroup.dockerCpuLimit(vals[0])
                            cpu.cpulimit(vals[1])
                    elif modules[3] == 'unset':
                        uncpu = docker_cgroup.dockerCpuLimit(modules[4])
                        uncpu.cpuunset()
                    else:
                        self.send_error(404, "api not found")
                elif modules[2] == 'cpuset':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if len(vals) == 2:
                            cpuset = docker_cgroup.dockerCpusetLimit(vals[0])
                            cpuset.cpusetlimit(vals[1])
                    elif modules[3] == 'unset':
                        uncpuset = docker_cgroup.dockerCpusetLimit(modules[4])
                        uncpuset.cpusetunset()
                    else:
                        self.send_error(404, "api not found")
                elif modules[2] == 'memory':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if len(vals) == 2:
                            mem = docker_cgroup.dockerMemLimit(vals[0])
                            mem.memlimit(vals[1])
                    elif modules[3] == 'unset':
                        unmem = docker_cgroup.dockerMemLimit(modules[4])
                        unmem.memunset()
                    else:
                        self.send_error(404, "api not found")
                elif modules[2] == 'blkio':
                    if modules[3] == 'set':
                        vals = modules[4].split("&")
                        if 2 < len(vals) < 5:
                            disk = docker_cgroup.dockerDiskLimit(vals[0])
                            if vals[1] == 'read':
                                if len(vals)== 3:
                                    disk.diskreadlimit(int(vals[2]))
                                else:
                                    disk.diskreadlimit(int(vals[2]),vals[3])
                            elif vals[1] == 'write':
                                if len(vals) == 3:
                                    disk.diskwritelimit(int(vals[2]))
                                else:
                                    disk.diskwritelimit(int(vals[2]), vals[3])
                    elif modules[3] == 'unset':
                        vals = modules[4].split('&')
                        if 1 < len(vals) < 4:
                            undisk = docker_cgroup.dockerDiskLimit(vals[0])
                            if vals[1] =='read':
                                if len(vals) == 3:
                                    undisk.diskreadunset(vals[2])
                                else:
                                    undisk.diskreadunset()
                            if vals[1]=='write':
                                if len(vals) == 3:
                                    undisk.diskreadunset(vals[2])
                                else:
                                    undisk.diskreadunset()
                    else:
                        self.send_error(404, "api not found")
            elif modules[1] == 'net':
                serverpath = os.path.dirname(os.path.realpath(__file__))
                print serverpath
                if len(modules) == 3:
                    vals = modules[2].split("&")
                    if len(vals) == 4 or len(vals) == 2:
                        vals = [serverpath+'/tcscript.sh'] + vals
                        print vals
                        output = subprocess.check_output(vals)
                        print output
                    else:
                        self.send_error(404, "api not found")
                        print 111
            self.send_response(200)
            self.send_header('Content-type', contentType)
            self.end_headers()
            if output:
                self.wfile.write(output)
            else:
                self.wfile.write("OK")
        except IOError:
            self.send_error(404, 'Filf Not Found')
if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 12345), MainHandler)
    print 'Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
