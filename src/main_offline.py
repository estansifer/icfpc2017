import sys
import json

import ai
import game_state

name = "This is an albatrocity!"

def receive_message():
    size = 0
    while True:
        c = sys.stdin.read(1)
        if c == ':':
            break
        else:
            size = 10 * size + int(c)

    message = sys.stdin.read(c)
    return json.loads(message)

def send_message(j):
    message = json.dumps(j)
    full_message = str(len(message)) + ':' + message
    sys.stdout.write(full_message)
    sys.stdout.flush()

def main(choose_move):
    send_message({'me' : name})
    j = receive_message()

    print(j)

    j = receive_message()

    # Setup
    if 'punter' in j:
        g = game_state.Game.from_json_setup(j)
        state = g.to_json_offline()
        send_message({'ready' : g.me, 'state' : state})

    # Play
    if 'move' in j:
        g = game_state.Game.from_json_offline(j['state'])
        g.apply_moves(j)
        e = choose_move(g)
        move = g.make_move(e)
        move['state'] = g.to_json_offline()
        send_message(move)

    # Done
    if 'stop' in j:
        g = game_state.Game.from_json_offline(j['state'])
        g.apply_moves({'move' : j['stop']})
        print("Final scores (we are {}):".format(g.me))
        print(j['stop']['scores'])

if __name__ == "__main__":
    if len(sys.argv) == 1:
        choose_move = ai.random
    elif len(sys.argv) == 2:
        choose_move = ai.lookup_ai(sys.argv[1])
        if choose_move is None:
            sys.exit(1)
    else:
        sys.exit(1)
    sys.stderr.write('test')
    sys.stderr.flush()
    main(choose_move)
