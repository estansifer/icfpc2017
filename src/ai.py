import ai_random
import ai_greedy

# Available AI algorithms.
# Each should be a function that takes as input an instance of Game
# and returns as output an instance of Edge.
random = ai_random.main
greedy = ai_greedy.main

# Look up an AI algorithm by a specified name
ai_list = {'random' : random,
        'greedy' : greedy}

def lookup_ai(name):
    if name in ai_list:
        return ai_list[name]
    else:
        return None
