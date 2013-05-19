#!/usr/bin/env ruby
require 'yaml'

if RUBY_VERSION =~ /1.9/
  Encoding.default_external = Encoding::UTF_8
  Encoding.default_internal = Encoding::UTF_8
end

class DemoPlayer

  @@cache_prefix = "cache"

  def initialize(id)
    @id = id
    @known_tracks = {}
    @unknown_tracks = {}
    @track_positions = []
    @cache_file = DemoPlayer.cache_file(id)
  end

  def do_init_phase!
    @width = Integer($stdin.gets.chomp)
    @height = Integer($stdin.gets.chomp)
    @turn_limit = Integer($stdin.gets.chomp)
    # Read toplists
    @toplists = {}
    [:top_tracks, :top_albums, :top_artists, :disliked_artists].each do |toplist|
      @toplists[toplist] = []
      n = Integer($stdin.gets.chomp)
      n.times { @toplists[toplist] << $stdin.gets.chomp }
    end
  end

  def do_turn_phase!
    read_turn!
    read_level!
    if (@remaining_capacity > 0) && (not @track_positions.empty?)
      puts move_toward(*closest_track)
    else
      puts move_toward(*@user_position)
    end
  end

  def write_to_file!
    File.open(@cache_file, "w+") do |f| 
      f.write YAML::dump(self)
    end
  end

  def self.read_from_file(id)
    YAML::load IO.read(DemoPlayer.cache_file(id))
  end

  private

  def self.cache_file(id)
    File.join(Dir.getwd, "#{@@cache_prefix}_#{id}") 
  end

  def read_turn!
    @turn = Integer($stdin.gets.chomp)
    @remaining_capacity = Integer($stdin.gets.chomp)
    @remaining_time = Integer($stdin.gets.chomp)
    @boost_cooldown = Integer($stdin.gets.chomp)
    # Read metadata query responses
    num_responses = Integer($stdin.gets.chomp)
    num_responses.times do
      response = $stdin.gets.chomp.split(",")
      uri = response.unshift
      @known_tracks[uri] = response
    end
  end

  def read_level!
    @track_positions = []
    @height.times do |y|
      row = $stdin.gets.chomp.split(',')
      @width.times do |x|
        case row[x]
        when @id then @x, @y = x, y
        when /spotify:track/ then @track_positions << [x, y]
        when "U" then @user_position = [x, y]
        end
      end
    end
  end

  def move_toward(x, y)
    if @x < x
      "E"
    elsif @x > x
      "W"
    elsif @y < y
      "S"
    elsif @y > y
      "N"
    end
  end
  
  def distance_to(x, y)
    (@x - x).abs + (@y - y).abs
  end

  def closest_track
    return if @track_positions.empty?
    curr_closest = @track_positions[0]
    curr_smallest_distance = distance_to(*curr_closest)
    @track_positions.each do |track|
      curr_distance = distance_to(*track)
      if curr_distance < curr_smallest_distance
        curr_closest = track
        curr_smallest_distance = curr_distance
      end
    end
    curr_closest
  end

end

type = $stdin.gets.chomp
id = $stdin.gets.chomp

if type == "INIT"
  player = DemoPlayer.new(id)
  player.do_init_phase!
elsif type == "TURN"
  player = DemoPlayer.read_from_file(id)
  player.do_turn_phase!
end

player.write_to_file!
