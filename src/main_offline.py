import sys
import json

import ai
import client

def main(choose_move):
    client.client_offline(choose_move)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        choose_move = ai.lookup_ai(sys.argv[1])
        if choose_move is None:
            sys.exit(1)
    else:
        sys.exit(1)
    sys.stderr.write('test\n')
    sys.stderr.flush()
    main(choose_move)
