from wordlegame import WordleGameStandard

game = WordleGameStandard()
game_state = game.query_game_state();
game.start();
while game_state not in ['win', 'lose']:
	game.output();
	guess = input();
	val = game.attempt_guess(guess);
	if val == 'Length': print('Word not long enough, try again')
	elif val == 'Word': print('Not a valid word, try again')
	game_state = game.query_game_state()

game.output()
if game_state == 'win':
	print('Congratulations, you win!')
else:
	print('Damn, you lost!')

