#!/usr/bin/env python3
from diglett import Diglett

if __name__ == '__main__':
    import sys

    service = Diglett('diglett', pid_dir='/tmp')
    if len(sys.argv) != 2:
        sys.exit('Syntax: %s COMMAND' % sys.argv[0])

    cmd = sys.argv[1].lower()
    if cmd == 'start':
        service.start()
    elif cmd == 'stop':
        service.stop()
        print('Stop digg')
    elif cmd == 'status':
        if service.is_running():
            print("Service is running.")
        else:
            print("Service is not running.")
    else:
        sys.exit('Unknown command "%s".' % cmd)