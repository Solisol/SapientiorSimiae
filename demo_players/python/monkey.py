import logging
import os.path
import pickle
import sys
import os

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
        self._decades = {}
        self._favorite_decade = 0
        self._track_values = {}
        self._plan = []
        self._file = None

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
        self._file = open("track_values.txt", 'w')
        self._file.close()
        
    def update(self, stream):
        self._id = stream.readline().strip()
        self._turn = util.get_int(stream)
        self._capacity = util.get_int(stream)
        self._time_left = util.get_int(stream)
        self._boost_cooldown = util.get_int(stream)
        self._track_pos = {}
        self.browse_result(sys.stdin)
        self._file = open("track_values.txt", 'r')
        file_content = self._file.read()
        self._metadata, self._track_values, self._plan = file_content.split('%', 2)
        self._file.close()
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
            if len(self._metadata) != len(self._track_pos):
                self.lookup
            else:
                if(self._capacity > 0):
                    print self._plan.pop()        
        self._file = open("track_values.txt", 'w')
        self._file.write(str(self._metadata) + "%" +str(self._track_values) + "%" + str(self._plan))
        self._file.close()

    def lookup(self):
        for pos in self._track_pos:
            track = self._track_pos[pos]
            if not track in self._metadata:
                print track 
                self._track_values[self._metadata[track]] = self.track_value(self._metadata[track])


    """def move(self):
        if self._capacity > 0:
            goal = self.get_track_pos(self.find_track())
        else:
            goal = self._user

        if goal[0] > self._pos[0]:
            if self._map[self._pos[0]+1,self._pos[1]] == "" or (self._pos[0]+1,self._pos[1]) == goal:
                print 'E'
        elif goal[0] < self._pos[0]:
            if self._map[self._pos[0]-1,self._pos[1]] == "" or (self._pos[0]-1,self._pos[1]) == goal:
                print 'W'
        elif goal[1] < self._pos[1]:
            if self._map[self._pos[0],self._pos[1]+1] == "" or (self._pos[0],self._pos[1]+1) == goal:
                print 'N'
        else:
            if self._map[self._pos[0],self._pos[1]-1] == "" or (self._pos[0],self._pos[1]-1) == goal:
                print 'S'"""

    def calc_plan(self, goal):
        spider = goal
        while(spider != self._pos):
            if spider[0] > self._pos[0]:
                if self._map[spider[0]+1,spider[1]] == "" or self._pos == (spider[0]+1, spider[1]):
                    self._plan.append('E')
                else:
                    north = self.find_distance((spider[0], spider[1]+1), self._pos)
                    south = self.find_distance((spider[0], spider[1]-1), self._pos)
                if north < south and (spider[0], spider[1]+1) == "" or (spider[0], spider[1]+1) == self._pos:
                    self._plan.append('N')
                elif (spider[0], spider[1]-1) == "" or (spider[0], spider[1]-1) == self._pos:
                    self._plan.append('S')
                else:
                    self._plan = self.go_back(self._plan, spider)
            elif spider[0] < self._pos[0]:
                if self._map[spider[0]-1,spider[1]] == "" or self._pos == (spider[0]-1, spider[1]):
                    self._plan.append('W')
                else:
                    north = self.find_distance((spider[0], spider[1]+1), self._pos)
                    south = self.find_distance((spider[0], spider[1]-1), self._pos)
                if north < south and (spider[0], spider[1]+1) == "" or (spider[0], spider[1]+1) == self._pos:
                    self._plan.append('N')
                elif (spider[0], spider[1]-1) == "" or (spider[0], spider[1]-1) == self._pos:
                    self._plan.append('S')
                else:
                    self._plan = self.go_back(self._plan, spider)
            elif spider[1] < self._pos[1]:
                if self._map[spider[0],spider[1]+1] == "" or self._pos == (spider[0], spider[1]+1):
                    self._plan.append('N')
                else:
                    west = self.find_distance((spider[0]-1, spider[1]), self._pos)
                    east = self.find_distance((spider[0]+1, spider[1]), self._pos)
                if west < east and (spider[0]-1, spider[1]) == "" or (spider[0]-1, spider[1]) == self._pos:
                    self._plan.append('W')
                elif (spider[0]+1, spider[1]) == "" or (spider[0]+1, spider[1]) == self._pos:
                    self._plan.append('E')
                else:
                    self._plan = self.go_back(self._plan, spider)
            else:
                if self._map[spider[0],spider[1]-1] == "" or self._pos == (spider[0], spider[1]-1):
                    self._plan.append('S')
                else:
                    west = self.find_distance((spider[0]-1, spider[1]), self._pos)
                    east = self.find_distance((spider[0]+1, spider[1]), self._pos)
                if west < east and (spider[0]-1, spider[1]) == "" or (spider[0]-1, spider[1]) == self._pos:
                    self._plan.append('W')
                elif (spider[0]+1, spider[1]) == "" or (spider[0]+1, spider[1]) == self._pos:
                    self._plan.append('E')
                else:
                    self._plan = self.go_back(self._plan, spider)
    
    def go_back(self, plan, spider):
        direction = plan.pop()
        if direction == 'E':
            spider = (spider[0]-1, spider[1])
            north = self.find_distance((spider[0], spider[1]+1), self._pos)
            south = self.find_distance((spider[0], spider[1]-1), self._pos)
            if north < south and (spider[0], spider[1]+1) == "" or (spider[0], spider[1]+1) == self._pos:
                return plan.append('N')
            elif (spider[0], spider[1]-1) == "" or (spider[0], spider[1]-1) == self._pos:
                return plan.append('S')
            else:
                self.go_back(plan, spider)
        elif direction == 'W':
            spider = (spider[0]+1, spider[1])
            north = self.find_distance((spider[0], spider[1]+1), self._pos)
            south = self.find_distance((spider[0], spider[1]-1), self._pos)
            if north < south and (spider[0], spider[1]+1) == "" or (spider[0], spider[1]+1) == self._pos:
                return plan.append('N')
            elif (spider[0], spider[1]-1) == "" or (spider[0], spider[1]-1) == self._pos:
                return plan.append('S')
            else:
                self.go_back(plan, spider)
        elif direction == 'N':
            spider = (spider[0], spider[1]-1)
            west = self.find_distance((spider[0]-1, spider[1]), self._pos)
            east = self.find_distance((spider[0]+1, spider[1]), self._pos)
            if west < east and (spider[0]-1, spider[1]) == "" or (spider[0]-1, spider[1]) == self._pos:
                return plan.append('W')
            elif (spider[0]+1, spider[1]) == "" or (spider[0]+1, spider[1]) == self._pos:
                return plan.append('E')
            else:
                self.go_back(plan, spider)
        else:
            spider = (spider[0], spider[1]+1)
            west = self.find_distance((spider[0]-1, spider[1]), self._pos)
            east = self.find_distance((spider[0]+1, spider[1]), self._pos)
            if west < east and (spider[0]-1, spider[1]) == "" or (spider[0]-1, spider[1]) == self._pos:
                return plan.append('W')
            elif (spider[0]+1, spider[1]) == "" or (spider[0]+1, spider[1]) == self._pos:
                return plan.append('E')
            else:
                self.go_back(plan, spider)

    def find_track(self):
        best_track = None
        best_score = -1000
        for track in self._track_values:
            current = self._track_values[track]
            for pos, metadata in self._track_pos.iteritems():
                if metadata == track:
                    track_pos = pos
                    break
            value = current/find_distance(track_pos, self._pos)
            if best_score < value:
                best_score = value
                best_track = track
        return best_track

    def get_track_pos(self, track):
        for pos, metadata in self._track_pos.iteritems():
            if metadata == track:
                return pos

    def find_distance(self, start, end):
        return math.fabs(start[0] - end[0]) + math.fabs(start[1] - end[1])

    def track_value(self, metadata):
        tier = self.calc_tier(metadata)
        return math.pow(4, tier)

    def calc_tier(self, metadata):
        parsed_metadata = metadata.split(',')
        uri = parsed_metadata[0]
        track = parsed_metadata[1]
        artist = parsed_metadata[2]
        album = parsed_metadata[3]
        year = parsed_metadata[4]
        tier = 0
        for x in self._bad_artists:
            if x == artist:
                return -2
        for x in self._top_tracks:
            if x.split(",")[0] == track:
                return -1
        for x in self._top_artists:
            if x == artist:
                tier =+ 1
        for x in self._top_albums:
            if x.split(",")[0] == album:
                tier =+ 1
        if self._favorite_decade <= year < (self._favorite_decade + 10):
            tier =+ 1
        return tier

    def calc_favorite_decade(self):
        for x in self._top_tracks:
            year = x.split(",")[3]
            self.update_decades(int(year))
        for x in self._top_albums:
            year = x.split(",")[2]
            self.update_decades(int(year))
        best_decade = 0
        local_max = 0
        for key in self._decades:
            if self._decades[key] > local_max:
                local_max = self._decades[key]
                best_decade = key
        self._favorite_decade = best_decade
        
    def update_decades(self, year):
        rest = year % 10
        dec = year - rest
        if dec in self._decades:
            self._decades[dec] += 1
        else:          
            self._decades[dec] = 1


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
    #monkey = Monkey()
    #monkey._top_albums = ['Craft Spells, Idle Labor, 2011','Gary Numan, Premier Hits, 1980']
    #monkey._top_tracks = ['Condemnation, Depeche Mode, Songs Of Faith And Devotion, 1990', 'Enola Gay - 2003 - Remaster, Orchestral Manoeuvres In The Dark, Organisation, 1998']
    #monkey.calc_favorite_decade()
    #print "Favorite decade %i" % monkey._favorite_decade