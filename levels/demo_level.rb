carrying_capacity 5
turn_limit 500
time_limit 20000
boost_cooldown 15

legend "1" => Monkey.player(1),
       "2" => Monkey.player(2),
       "X" => Track.tier(-2),
       "x" => Track.tier(-1),
       "l" => Track.tier(1),
       "t" => Track.tier(2),
       "T" => Track.tier(3),
       "U" => User,
       "#" => Wall

layout <<EOS
 Xl     1 U 2     lX 
t    ll       ll    t
###t ########### t###
#t # #T tlTlt T# # t#
##   #T#l   l#T#   ##
#l ######X X###### l#
##  #   # x #   #  ##
#T#   #t#   #t#   #T#
#x#l##### # #####l#x#
#   #   # l #   #   #
### # # # # # # # ###
#t    #   #   #    t#
#l###l#t#t#t#t#l###l#
EOS
