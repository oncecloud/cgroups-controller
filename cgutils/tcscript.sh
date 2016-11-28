#!/bin/bash
#
#  tc uses the following units when passed as a parameter.
#  kbps: Kilobytes per second 
#  mbps: Megabytes per second
#  kbit: Kilobits per second
#  mbit: Megabits per second
#  bps: Bytes per second 
#       Amounts of data can be specified in:
#       kb or k: Kilobytes
#       mb or m: Megabytes
#       mbit: Megabits
#       kbit: Kilobits
#  To get the byte figure from bits, divide the number by 8 bit
#

#
# Name of the traffic control command.
TC=/sbin/tc

# Download limit (in mega bits)
DNLD=$3          # DOWNLOAD Limit

# Upload limit (in mega bits)
UPLD=$4          # UPLOAD Limit


start() {

    echo $IF
    $TC qdisc add dev $IF root handle 1: htb default 1
    $TC class add dev $IF parent 1: classid 1:1 htb rate $DNLD ceil $DNLD burst $DNLD
    $TC qdisc add dev $IF parent 1:1 handle 2: sfq perturb 10
    $TC filter add dev $IF parent 1:0 protocol all prio 1 handle 1 fw flowid 1

    $TC qdisc add dev $IF ingress
    $TC filter add dev $IF parent ffff: protocol all u32 match u32 0 0 police rate $UPLD burst $UPLD mtu 64kb drop flowid :1


}

stop() {

# Stop the bandwidth shaping.
    $TC qdisc del dev $IF root
    $TC qdisc del dev $IF ingress

}

restart() {

# Self-explanatory.
    stop
    sleep 1
    start

}

show() {

# Display status of traffic control status.
    $TC -s qdisc ls dev $IF

}

if [  -z "$2" ]; then
    echo "Please input the interface"
    exit
else
    IF=$2
fi
case "$1" in

  start)

    echo -n "Starting bandwidth shaping: "
    start
    echo "done"
    ;;

  stop)

    echo -n "Stopping bandwidth shaping: "
    stop
    echo "done"
    ;;

  restart)

    echo -n "Restarting bandwidth shaping: "
    restart
    echo "done"
    ;;

  show)

    echo "Bandwidth shaping status for $IF:"
    show
    echo ""
    ;;

  *)

    pwd=$(pwd)
    echo "Usage: tc.bash {start|stop|restart|show}"
    ;;

esac

exit 0
