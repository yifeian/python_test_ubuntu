import struct
import socket
import sys
from time import sleep,time
from optparse import OptionParser


if __name__ == '__main__':
    parser = OptionParser()

    parser.add_option('-n','--hostname',
        action='append',
        dest='host_name',
        help='Define COAP host name')

    parser.add_option('-p','--port',
        action='append',
        dest='host_port',
        help='Define COAP port(default:5683)')

    parser.add_option('-l','--loops',
        type='int',
        dest='ping_loops',
        default = 0,
        help='Number of ping loops(default:0 - forver)')

    parser.add_option('-t','--sleep time',
        type='float',
        dest='sleep_sec',
        default = 1,
        help='time in secondes between two pings (default :1 sec)')

    (options, args) = parser.parse_args()

    host = options.host_name[0]
    port = int(options.host_port[0])
    ping_loops = options.ping_loops
    sleep_sec = options.sleep_sec
    
    print 'ping args %s,%s,%s,%s' %(host,port,ping_loops,sleep_sec)

    ping_no = 1
    ping_cnt = 0

    try:
        s = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)
    except socket.error:
        print 'error : faild create socket '
        sys.exit()

    while True:
        loop_time = time()
        msg='' #[0x40,0x00,0x00,0x00]
        msg += struct.pack('B',0x40)
        msg += struct.pack('B',0x00)
        msg += struct.pack('B',0x00)
        msg += struct.pack('B',ping_no)

        try:
            print '[0x%08X] send ping:' %(ping_cnt),[hex(ord(c)) for c in msg]
            s.sendto(msg,(host,port))

            s.settimeout(2+sleep_sec)

            data, addr= s.recvfrom(4)

            status = bytes(msg)[3] == bytes(data)[3]
            print '[0x%08x] Recv ping from:'%(ping_cnt),addr,[hex(ord(c)) for c in data],'ok' if status else 'fail'


        except socket.error as e:
            print 'Error : socket.error :',str(e)
            sleep(3)
        except socket.timeout:
            print "Error: closing socket"
            s.close()
        
        if ping_no >= 0xff:
            ping_no = 0
        else:
            ping_no += 1
        
        sleep(sleep_sec -(time()-loop_time))
        print 'In %.2f sec'%(time() - loop_time)

        if ping_loops > 0:
            if ping_loops == 1:
                break
            ping_loops -= 1
        ping_cnt += 1


        