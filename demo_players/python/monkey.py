import logging
import os.path
import pickle
import sys

import util

STATE_FILENAME = 'state.pickle'
TRACK_URI_HEADER = 'spotify:track:'

class Monkey(object):
    def __init__(self):
        self._id = 0
        self._w = 0
        self._h = 0
        self._turn_limit = 0
        self._turn = 0
        self._capacity = 0
        self._time_left = 0
        self._top_tracks = None
        self._top_albums = None
        self._top_artists = None
        self._bad_artists = None
        self._bad_tracks = set()
        self._map = {}
        self._pos = None
        self._user = None
        self._boost_cooldown = 0
        self._track_pos = {} # pos -> uri
        self._metadata = {} # uri -> metadata
        self._objective = None
        
    @classmethod
    def process_input(cls, stream):
        monkey = None
        line = stream.readline().strip()
        if line == 'INIT':
            logging.basicConfig(filename='monkey.log', filemode='w', level=logging.DEBUG)
            monkey = cls()
            monkey.initialize(stream)
        else:
            logging.basicConfig(filename='monkey.log', filemode='a', level=logging.DEBUG)
            monkey = cls.load()
            monkey.update(stream)
        return monkey
            
    def initialize(self, stream):
        self._id = stream.readline().strip()
        self._w = util.get_int(stream)
        self._h = util.get_int(stream)
        self._turn_limit = util.get_int(stream)
        self._top_tracks = util.get_set(stream)
        self._top_albums = util.get_set(stream)
        self._top_artists = util.get_set(stream)
        self._bad_artists = util.get_set(stream)
        
    def update(self, stream):
        self._id = stream.readline().strip()
        self._turn = util.get_int(stream)
        self._capacity = util.get_int(stream)
        self._time_left = util.get_int(stream)
        self._boost_cooldown = util.get_int(stream)
        self._track_pos = {}
        self.browse_result(sys.stdin)
        for y in xrange(self._h):
            line = stream.readline().strip()
            for x, square in enumerate(line.split(',')):

                self._map[x, y] = square
                if square == self._id:
                    self._pos = (x, y)
                elif square == 'U':
                    self._user = (x, y)
                elif square.startswith(TRACK_URI_HEADER):
                    self._track_pos[x, y] = square
                    try:
                        metadata = self._metadata[square]
                        self._map[x, y] = '+' if self.track_value(metadata) > 0 else '-'
                    except KeyError:
                        self._map[x, y] = '?'
                        
    def action(self):
        if self._turn >= 1:
          print 'W'
                                
    def browse_result(self, stream):
        browsed_tracks = util.get_set(sys.stdin)
        for track in browsed_tracks:
            logging.debug('[%d] Browsed track: %s', self._turn, track)
            uri, metadata = track.split(',', 1)
            self._metadata[uri] = metadata
        
    def save(self):
        with open(self.save_path(), 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
    
    @classmethod
    def load(cls):
        with open(cls.save_path(), 'rb') as f:
            return pickle.load(f)
    
    @classmethod
    def save_path(cls):
        dir_path = os.path.dirname(__file__)
        return os.path.join(dir_path, STATE_FILENAME)

if __name__ == '__main__':
    monkey = Monkey.process_input(sys.stdin)
    monkey.action()
    monkey.save()
    sys.stdout.flush()
