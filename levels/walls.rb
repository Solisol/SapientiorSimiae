carrying_capacity 4
turn_limit 40
time_limit 1500
boost_cooldown 5

legend "1" => Monkey.player(1),
       "2" => Monkey.player(2), 
       "l" => Track.tier(1),
       "t" => Track.tier(2),
       "T" => Track.tier(3),
       "U" => User,
       "#" => Wall

layout <<EOS
T.t.t.T
.......
###.###
.......
..1U2..
EOS
