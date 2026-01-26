from db_handler import db_reader

dbr = db_reader()

print(dbr.get_match_history('Falcons', map =0, side = 0, months=3))

print(dbr.get_average_player_rating(23685, map =0, side = 0, months=3))
print(dbr.get_average_ratings_fantasy(591, months=3))

print(dbr.get_average_ratings_fantasy_vs(591, months=3, vs = 11861))


