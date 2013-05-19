import re

INTEGER = re.compile(r'(\d+).*')

D_POS = {'W': (-1, 0), 'N': (0, -1), 'E': (1, 0), 'S': (0, 1)}
MOVES = dict([(v, k) for k, v in D_POS.iteritems()])

def distance(p0, p1):
    return abs(p0[0] - p1[0]) + abs(p0[1] - p1[1])
    
def move(p_from, p_to):
    dx = p_to[0] - p_from[0]
    dy = p_to[1] - p_from[1]
    return MOVES[dx, dy]
    
def follow_path(self, path):
    return move(path[0], path[1])
    
def get_int(stream):
    line = stream.readline().strip()
    match = INTEGER.match(line)
    return int(match.group(1))
    
def get_set(stream):
    s = set()
    size = get_int(stream)
    for ix in xrange(size):
        s.add(stream.readline().strip())
    return s
