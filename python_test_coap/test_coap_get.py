
import struct
import socket
import sys
from time import sleep,time
from optparse import OptionParser

COAP_TYPE_CON = 0
COAP_TYPE_NONCON = 1
COAP_TYPE_ACK = 2
COAP_TYPE_RESET = 3



COAP_METHOD_GET = 0x01
COAP_METHOD_POST = 0x02
COAP_METHOD_PUT  = 0x03
COAP_METHOD_DELETE = 0x04

COAP_OPTION_IF_MATCH = 0x10
COAP_OPTION_URI_HOST = 0x30
COAP_OPTION_URI_PATH = 0xb0




def coap_get_test(msg_id,token,s):
    msg = ''
    msg += struct.pack('!B',0x41)
    msg += struct.pack('!B',COAP_METHOD_GET)
    msg += struct.pack('!H',msg_id)
    msg += struct.pack('!B',token)
    if len(url_host) > 13:
        msg += struct.pack('!B',0x30+0x0d)
        msg += struct.pack('!B',len(url_host)-13)
    else:   
        msg += struct.pack('!B',0x30+len(url_host))
    list_host = [ord(c) for c in url_host]
    for data in list_host:
        msg += struct.pack('!B',int(data))
    if len(url_path) > 0:
        for i in url_path:
            list_path = [ord(c) for c in i]
            msg += struct.pack('!B',0x80+len(list_path))
            for data in list_path:
                msg += struct.pack('!B',int(data))
    print 'send data'
    print ' '.join([hex(ord(c)) for c in msg])
    s.sendto(msg,sa)


def coap_observe_test(msg_id,token,s):
    opt_delta_send = 0
    msg = ''
    msg += struct.pack('!B',0x41)
    msg += struct.pack('!B',COAP_METHOD_GET)
    msg += struct.pack('!H',msg_id)
    msg += struct.pack('!B',token)
    if len(url_host) > 13:
        msg += struct.pack('!B',0x30+0x0d)
        msg += struct.pack('!B',len(url_host)-13)
    else:   
        msg += struct.pack('!B',0x30+len(url_host))
    list_host = [ord(c) for c in url_host]
    for data in list_host:
        msg += struct.pack('!B',int(data))
    opt_delta_send += 3
    opt_delta = 6 - opt_delta_send
    msg += struct.pack('!B',opt_delta << 4)
    opt_delta_send += 3
    opt_delta = 11 - opt_delta_send
    if len(url_path) > 0:
        for i in url_path:
            list_path = [ord(c) for c in i]
            msg += struct.pack('!B',(opt_delta << 4)+len(list_path))
            for data in list_path:
                msg += struct.pack('!B',int(data))
    print 'send data'
    print ' '.join([hex(ord(c)) for c in msg])
    s.sendto(msg,sa)


def deal_recv(msg_id,token,s):
    mark = 0
    recv_str = ''
    try:
        while True:
            recvdata, addr= s.recvfrom(4095)
            print 'recv data',addr
            #print ' '.join([hex(ord(c)) for c in recvdata])
            #print type(recvdata)
            list_data = [ord(c) for c in recvdata]
            type = (list_data[0] & 0x20) >> 4
            if (type >= COAP_TYPE_CON) and (type <= COAP_METHOD_DELETE):
                if type == COAP_TYPE_CON:
                    print 'recv con'
                elif type == COAP_TYPE_NONCON:
                    print 'recv noncon'
                elif type == COAP_TYPE_ACK:
                    print 'recv ack'
                elif type == COAP_TYPE_RESET:
                    print 'recv reset'
                token_len = list_data[0] & 0x0f
                print 'token len',token_len
                if list_data[1] == 69:
                    print 'code : 2.05'
                print list_data[2],list_data[3]
                mid_recv = (list_data[2] << 8) + list_data[3]
                print 'Message ID:',mid_recv
                token_recv = 0
                for i in range(token_len):
                    token_recv |= (list_data[3+i+1]<<((token_len-1)*8))
                print "token :",hex(token_recv)
                mark = 3+i+2
                print msg_id,hex(token)
                if type == COAP_TYPE_ACK:
                    if (msg_id == mid_recv) and (token == token_recv):
                        print 'this msg is for me '
                    else:
                        print 'get msg error'
                        break
                    
                if list_data[mark] == 0xff:
                    mark += 1
                    recv_str += recvdata[mark:]
                    print recv_str
                    recv_str = ''
                    print 'transmit end'
                    break
                else:
                    opt_delta_recv = 0
                    opt_delta_ex = 0
                    send_ack = 0
                    while (list_data[mark] != 0xff):
                        opt_delta_recv += (list_data[mark] >> 4)
                        opt_length = list_data[mark] & 0x0f
                        mark += 1
                        if opt_delta_recv == 6:
                            if type == COAP_TYPE_ACK or type == COAP_TYPE_NONCON:
                                if opt_length == 0:
                                    print 'observe register %d'%opt_length
                                    continue
                            elif type == COAP_TYPE_CON:
                                if opt_length != 0:
                                    print 'observe register %d'%list_data[mark]
                                send_ack = 1
                        if opt_delta_recv == 13:
                            opt_delta_recv += list_data[mark]
                            mark += 1
                        if opt_delta_recv == 23:
                            recv_opt_len = opt_length
                            recv_N_M_Z = list_data[mark]
                            SZX = recv_N_M_Z & 0X07
                            M = (recv_N_M_Z & 0x08) >> 3
                            NUM = recv_N_M_Z >> 4
                            print 'NUM %d,M %d,SZX %d'%(NUM,M,SZX)
                        if opt_delta_recv == 28:
                            block_size = (list_data[mark] << 8) + list_data[mark+1]
                            print 'Block Size %d'%block_size
                        mark += opt_length
                    mark += 1
                    recv_str += recvdata[mark:]
                    if (opt_delta_recv == 6) and (opt_length == 0):
                        print recv_str
                        recv_str = ''
                    if (type == COAP_TYPE_ACK) and (opt_delta_recv != 6):
                        if M == 1:
                            msg_id += 1
                            token += 1
                            msg = ''
                            msg += struct.pack('!B',0x41)
                            msg += struct.pack('!B',COAP_METHOD_GET)
                            msg += struct.pack('!H',msg_id)
                            msg += struct.pack('!B',token)
                            opt_delta_send = 0
                            if len(url_host) > 13:
                                msg += struct.pack('!B',0x30+0x0d)
                                msg += struct.pack('!B',len(url_host)-13)
                            else:   
                                msg += struct.pack('!B',0x30+len(url_host))
                            
                            list_host = [ord(c) for c in url_host]
                            for data in list_host:
                                msg += struct.pack('!B',int(data))
                            opt_delta_send += 3
                            if len(url_path) > 0:
                                for i in url_path:
                                    list_path = [ord(c) for c in i]
                                    msg += struct.pack('!B',0x80+len(list_path))
                                    for data in list_path:
                                        msg += struct.pack('!B',int(data))
                                opt_delta_send += 8
                            if (23 - opt_delta_send) <= 13:
                                msg += struct.pack('!B',((23 - opt_delta_send)<<4)+recv_opt_len)
                            else:
                                opt_delta_ex = 23 - opt_delta_send -13
                                msg += struct.pack('!B',(13<<4)+recv_opt_len)
                                msg += struct.pack('!B',opt_delta_ex)
                            send_N_M_Z = 0
                            send_N_M_Z |= SZX
                            send_N_M_Z |= ((NUM + 1) << 4)
                            msg += struct.pack('!B',send_N_M_Z)
                            s.sendto(msg,sa)
                        elif M == 0:
                            print recv_str
                            recv_str = ''
                            print 'transmit end'
                            break
                    if type == COAP_TYPE_CON:
                        if send_ack == 1:
                            print recv_str
                            recv_str = ''
                            msg = ''
                            msg += struct.pack('!B',0x60)
                            msg += struct.pack('!B',0x00)
                            msg += struct.pack('!H',mid_recv)
                            s.sendto(msg,sa)
                
            else:
                print 'msg error '
                    
        #print list_data

    except socket.error as e:
        print 'Error : socket.error :',str(e)
        sys.exit()
    except socket.timeout:
        print "Error: closing socket"
        s.close()
    s.close()



if __name__ == "__main__":
    parser = OptionParser()

    parser.add_option('-n','--hostname',
        action='append',
        dest='host_name',
        help='Define COAP host name')
    
    parser.add_option('-p','--port',
        type='int',
        dest='host_port',
        default=5683,
        help='Define COAP port(default:5683)')

    parser.add_option('-m','--method',
        action='append',
        dest='coap_method',
        help='Define COAP method')
    
    (options, args) = parser.parse_args()
    url_path=[]
    print options.host_name
    method = options.coap_method[0].upper()
    print method
    try:
        url_split = ''.join(options.host_name).split('/')
        print url_split
        if len(url_split) >= 3:
            url_host = url_split[2]
            url_path = url_split[3:]
        else:
            print 'url_split error'
            sys.exit()
    except :
        print 'input error'
        sys.exit()
    port = options.host_port
    print url_host,url_path,method

    for res in socket.getaddrinfo(url_host,port,0,socket.SOCK_DGRAM):
        af, socktype, proto, canonnname, sa = res
        try:
            s = socket.socket(af,socktype,proto)
        except socket.error,err_msg:
            print err_msg
            print 'error : faild create socket '
            sys.exit()
    url_host = sa[0]
    print url_host
    print type(url_host)
    token = 0xb1
    msg_id = 0x689a
    if method.startswith("GET"):
        coap_get_test(msg_id,token,s)
        deal_recv(msg_id,token,s)
    elif method.startswith("OBSERVE"):
        coap_observe_test(msg_id,token,s)
        deal_recv(msg_id,token,s)
    else:
        print 'error method'




        