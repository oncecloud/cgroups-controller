# cgrouputils
## cpu
限制使用cpu时间的百分比

**kvm set：http://ip:port/kvm/cpu/set/kvmname&per**

**kvm unset: http://ip:port/kvm/cpu/unset/kvmname**

**docker set: http://ip:port/kvm/cpu/set/dockerid&per**

**docker unset http://ip:port/docker/cpu/unset/dockerid**

**kvmname**:kvm 的名称

**dockerid**: docker的id

**per**:cpu百分比，取值范围1-100

## cpuset
限制使用cpu的个数
docker可用，kvm不可用

**docker set: http://ip:port/docker/cpuset/set/dockerid&set**

**docker unset: http://ip:port/docker/cpuset/unset/dockerid&set**

**dockerid**: docker的id

**set**: 可以使用的cpu序号，如1,2,3或者1-3或者1-3,9-12

## memory
限制使用的内存的总量

**kvm set：http://ip:port/kvm/memory/set/kvmname&val**

**kvm unset: http://ip:port/kvm/memory/unset/kvmname**

**docker set: http://ip:port/kvm/memory/set/dockerid&val**

**docker unset http://ip:port/docker/memory/unset/dockerid**

**kvmname**:kvm 的名称

**dockerid**: docker的id

**val**:可以使用的内存总量，单位为B，例如1024576是1MB

## disk
限制磁盘的读写速度
**kvm set：http://ip:port/kvm/blkio/set/kvmname&read&val**

**kvm set：http://ip:port/kvm/blkio/set/kvmname&read&val&path**

**kvm unset: http://ip:port/kvm/blkio/unset/kvmname&&read**

**docker set：http://ip:port/kvm/blkio/set/dockerid&read&val**

**docker set：http://ip:port/kvm/blkio/set/dockerid&read&val&path**

**docker unset: http://ip:port/kvm/blkio/unset/dockerid&&read**

**kvmname**:kvm 的名称

**dockerid**: docker的id

**val**:限制的速度大小，单位是B，如1024576是1MB

**read**：读取或者写入，替换成write时是写入速度

**path**: docker或者kvm硬盘的挂载位置，默认是/var，可以只填写前缀

## net

限制网络的上传下载速度

**set:http://ip:port/net/vnet&start&upload&&download**

**unset:http://ip:port/net/vnet&stop**

不区分docker与kvm，需要提供对应的虚拟网卡

**vnet**: docker或者kvm所对应的虚拟网卡

**upload**：上传速度，必须同时提供上传下载速度 格式是1mb表示1MB上传速度

**download**：下载速度，必须同时提供上传下载速度 格式是1mb表示1MB上传速度


