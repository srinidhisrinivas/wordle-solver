
import random

	
class WordleGameStandard:
	def __init__(self, length=5,num_tries=6):
		self.word_list = []
		with open('words_alpha.txt','r') as f:
			self.word_list = f.read().split('\n')
		self.guesses_history = []
		self.length = length
		def generate_random_word(length=5):
			filtered_list = list(filter(lambda x: len(x) == self.length, self.word_list));
			#return 'ADDER'
			return random.choice(filtered_list)
		self.game_word = generate_random_word(length).upper();
		self.num_tries = num_tries;
		self.num_attempts = 0;
		self.game_state = 'begin' # begin, guessing, win, lose
		
	def start(self):
		self.game_state = 'guessing'
	def evaluate_guess(self,guess):
		word_split = [char for char in self.game_word]
		evaluation = ['_']*self.length;
		covered_word_ids = []
		covered_guess_ids = []
		guess_split = [char for char in guess];
		for idx,letter in enumerate(guess_split):
			if letter == word_split[idx]:
				evaluation[idx]='Y'
				covered_word_ids.append(idx);
				covered_guess_ids.append(idx);

		# print(covered_word_ids)
		# print(covered_guess_ids)
		remaining_word_letters = []
		for i in range(self.length):
			if i not in covered_word_ids:
				remaining_word_letters.append(word_split[i]);
			else:
				remaining_word_letters.append('_')

		# print(remaining_word_letters);

		for idx,letter in enumerate(guess_split):
			# print('\n')
			# print(idx, letter)
			if idx in covered_guess_ids: continue;
			if letter in remaining_word_letters:
				evaluation[idx] = 'O'
				found_letter_idx = remaining_word_letters.index(letter)
				covered_word_ids.append(found_letter_idx)
				remaining_word_letters = []
				for i in range(self.length):
					if i not in covered_word_ids:
						remaining_word_letters.append(word_split[i]);
					else:
						remaining_word_letters.append('_')
			else:
				evaluation[idx] = 'X'

			# print(covered_word_ids)
			# print(covered_guess_ids)
			# print(remaining_word_letters)

		return ''.join(evaluation)

	def validate_guess(self,guess):

		if len(guess) != self.length:
			return 'Length'
		if guess.lower() not in self.word_list:
			return 'Word'
		return 'Clear'
	def attempt_guess(self,guess):
		guess = guess.upper()
		val = self.validate_guess(guess);
		if val != 'Clear':
			return val;
		self.guesses_history.append((guess, self.evaluate_guess(guess)));
		self.num_attempts += 1;
		if guess == self.game_word:
			self.game_state = 'win'
		elif self.num_attempts == self.num_tries:
			self.game_state = 'lose'
		return self.evaluate_guess(guess)
	def output(self):
		#print(self.game_word.upper())
		if self.game_state in ['begin', 'guessing']:
			print('\nVenture a guess at a {} letter word!'.format(self.length))
		print('Attempts remaining: ' + str(self.num_tries - self.num_attempts))
		print('Previous guesses:');
		for guess, evaluation in self.guesses_history:
			print(guess.upper() + '\t' + evaluation.upper());
		print('\n')
		if self.game_state in ['win','lose']:
			print('The word was ' + self.game_word);

	def query_game_state(self):
		
		return self.game_state
