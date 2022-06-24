#:/bin/sh

for i in {1..9}; do
    echo -n "Building challenge0$i... "
    echo "#!/bin/python3

from sys import argv
from local_challs import *

def get_args():
    try:
        with open(argv[1], 'r') as f:
            # Get all args without the \n in the end
            args = [l[:-1] for l in f.readlines()]
    except:
        print('Could not open the input file and read the arguments')
        exit(84)
    return args

if __name__ == '__main__':
    args = get_args()
    try:
        solution = challenge0$i(args)
        print('\n'.join(solution))
    except InputError as e:
        print('Input Error: ' + str(e))
        exit(84)
    except Exception as e:
        print('Error: ' + str(e))
        exit(84)" > challenge0$i
    chmod +x challenge0$i
    echo "DONE"
done

for i in {10..14}; do
    echo -n "Building challenge$i... "
    echo "#!/bin/python3

from remote_challs import *
from local_challs import InputError

if __name__ == '__main__':
    try:
        solution = challenge$i('127.0.0.1:5000/challenge$i')
        print('\n'.join(solution))
    except InputError as e:
        print('Input Error: ' + str(e))
        exit(84)
    except Exception as e:
        print('Error: ' + str(e))
        exit(84)" > challenge$i
    chmod +x challenge$i
    echo "DONE"
done
