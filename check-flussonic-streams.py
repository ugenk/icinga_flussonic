#!/usr/bin/python3
"""
This Nagios check can be used to monitor percentage of alive streams at flussonic server

Author: Evgeniy Kozhuhovskiy <ugenk@mediatech.by>, 2021
"""

import argparse, sys, os, json, base64, urllib, urllib.request

parser=argparse.ArgumentParser(description='Checks for flussonic servers')
parser.add_argument("-H", "--host", help="flussonic host, e.g. 1.2.3.4", type=str)
parser.add_argument("-l", "--login", help="login for flussonic api", type=str, default='flussonic')
parser.add_argument("-p", "--password", help="password for flussonic api", type=str, default='letmein!')
parser.add_argument("--max_failed_streams_percent", help="percent of streams, that could be in the failed state", type=int, default=70)
parser.add_argument("--max_used_gpu_memory", help="maximum percentage of used gpu memory")
parser.add_argument("--timeout", type=int, default=10)


if len(sys.argv)<3:
    parser.print_help()
    sys.exit(1)

proto = 'http' # TODO: add proto selection and https support

args=parser.parse_args()

if args.host:
    url = proto + '://' + args.host + '/flussonic/api/server'
    req = urllib.request.Request(url)
    if args.login and args.password:
        b64auth = base64.standard_b64encode(("%s:%s" % (args.login,args.password)).encode('utf-8'))
        req.add_header("Authorization", "Basic %s" % b64auth.decode('utf-8'))
    try:
        response = urllib.request.urlopen(req, timeout=args.timeout)
    except ValueError:
        print('UNKNOWN - probably a wrong url')
        sys.exit(3)
    except urllib.error.HTTPError as e:
        print('CRITICAL - The server couldn\'t fulfill the request. Error code: %s', e.code)
        sys.exit(2)
    except urllib.error.URLError as e:
        print('CRITICAL - We failed to reach a server. Reason: %s', e.reason)
        sys.exit(2) 
    else:
        try:
            data = json.loads(response.read().decode())
        except ValueError as e:
            print('CRITICAL - Failed to parse JSON response from flussonic: %s', e.reason)
            sys.exit(2)
        # doing logical tests
        # checking GPUs memory
        gpu_mem_usage_str = gpu_mem_usage_str_tech = ''
        if len(data['transcoder_devices']) > 0:
            for device in data['transcoder_devices']:
                if device['type'] == 'nvenc':
                    gpu_mem_usage_str += 'GPU%i Memory used: %i%%, ' % (device['id'], int(device['memUsed']/device['memTotal']*100))
                    gpu_mem_usage_str_tech += 'gpu%i_mem_free=%i gpu%i_mem_total=%i gpu%i_mem_used=%i ' % (device['id'], device['memFree'], device['id'], device['memTotal'], device['id'], device['memUsed'])

        return_str = 'Total streams = %i, Live streams = %i, %s| total_streams=%i live_streams=%i total_clients=%i %s' % (data['total_streams'], data['online_streams'], gpu_mem_usage_str, data['total_streams'], data['online_streams'], data['total_clients'], gpu_mem_usage_str_tech)

        # checking amount of alive streams
        if data['online_streams'] / data['total_streams'] * 100 < args.max_failed_streams_percent:
            print('CRITICAL - Too much failed streams: %i, %s', data['online_streams'], return_str)
            sys.exit(2)

        print('OK: ' + return_str)
        sys.exit(0)

else:
    print("UNKOWN - something went wrong")
    sys.exit(3)