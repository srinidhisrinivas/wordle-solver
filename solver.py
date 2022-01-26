from wordlegame import WordleGameStandard
import numpy as np
import random

class Solver:
	def __init__(self, length=5):
		self.all_possible_words = []
		with open('words_alpha.txt','r') as f:
			self.all_possible_words = f.read().split('\n')

		self.game_word_length = 5;
		self.all_possible_words = list(filter(lambda word: len(word) == self.game_word_length, self.all_possible_words));
		self.current_possible_words = self.all_possible_words.copy();

		self.letters = [chr(i) for i in range(65,65+26)]
		self.letter_probs = np.zeros(shape=(len(self.letters),self.game_word_length))



	"""
	 Update the word list based on a set of rules. Rules are based on
	 feedback of the guess from the wordle game.

	 Rules are of the form:

	 "<letter> at <position>" - (<letter>, True, <position>)
	 "<letter> not at <position>" - (<letter>, False, <position>)
	 "<letter> not in word" - (<letter>, False, -1)
	"""
	def update_word_list(self, rule_list):
		# print(rule_list)
		for (letter, value, position) in rule_list:
			if position == -1:
				self.current_possible_words = list(filter(lambda word: letter.lower() not in word, self.current_possible_words))
			elif value:
				self.current_possible_words = list(filter(lambda word: word[position] == letter.lower(), self.current_possible_words))
			elif not value:
				self.current_possible_words = list(filter(lambda word: word[position] != letter.lower(), self.current_possible_words))

	"""
	Convert the evaluation into a list of rules as follows:

	Y at position -> "<guess[position]> at position" -> (<guess[position]>, True, <position>)
	O at position -> "<guess[position]> not at position" -> (<guess[position]>, False, <position>)
	X at <position> -> check if guess[position] is in the word elsewhere but marked as 'O' or 'Y'
		if yes: "<guess[position] not at position" -> (<guess[position]>, False, <position>)
		if no: "<guess[position]> not in word" -> (<guess[position]>, False, -1)
	"""
	def process_evaluation(self, guess, evaluation):
		guess_split = [char for char in guess];
		evaluation_split = [char for char in evaluation];

		rule_list = [];
		for idx, eval_ in enumerate(evaluation_split):
			if eval_ == 'Y':
				rule_list.append((guess_split[idx], True, idx))
			elif eval_ == 'O':
				rule_list.append((guess_split[idx], False, idx))
			else:
				char = guess_split[idx];
				all_char_ids = []
				for idx2, comp_char in enumerate(guess_split):
					if char == comp_char:
						all_char_ids.append(idx2);

				is_same_char = [(evaluation_split[idx2] in ['Y', 'O']) for idx2 in all_char_ids];
				if any(is_same_char): 
					rule_list.append((guess_split[idx], False, idx));
				else:
					rule_list.append((guess_split[idx], False, -1));

		return rule_list;

	"""
	Update probabilities of each letter occurring in a particular location,
	conditioned on the rules. Conditional probability is implemented by 
	cutting down the list of possible words using the rules, and calculating
	probabilities based on these words.

	prob(letter, position) = count(letter, position) / count(all_letters, position) 
						   = count(letter, position) / count(words)

	Meaning that probability of any letter occurring at a given position is 1.

	"""
	def update_letter_probs(self):
		# Update letter probabilities based on conditional probabilities
		
		self.letter_probs = np.zeros(shape=(len(self.letters),self.game_word_length))

		for word in self.current_possible_words:
			for pos, char in enumerate(word):
				char = char.upper();
				self.letter_probs[self.letters.index(char), pos] += 1;

		self.letter_probs = self.letter_probs / len(self.current_possible_words); 
		

	"""
	Shannon information of a given word calculated based on probabilities
	of letters occurring in those positions. All probabilities are conditioned
	on the same set of previous rules, meaning that probabilities are assumed
	to be independent of the probability of occurrence of another letter at a
	given position in the same word.

	entropy(word) = -sum(prob(letter, position) * ln(prob(letter, position)))

	"""
	def calculate_word_entropy(self,word):
		entropy = 0;
		for pos, char in enumerate(word):
			char = char.upper()
			letter_prob = self.letter_probs[self.letters.index(char), pos]
			if letter_prob != 0:
				entropy += letter_prob * np.log(letter_prob);
			else:
				entropy += 0

		return -entropy;


	def generate_solver_guess(self,rule_list):
		self.update_word_list(rule_list);
		# print(len(self.current_possible_words));
		self.update_letter_probs();

		certainty_level = np.sum(self.letter_probs.max(axis=0))
		print(certainty_level);
		if certainty_level < 4:
			# Calculate the total entropy for all possible words
			word_entropies = np.array([self.calculate_word_entropy(word) for word in self.all_possible_words]);
			max_entropy_idx = np.argmax(word_entropies);
			print(np.max(word_entropies))
			return self.all_possible_words[max_entropy_idx];

		else:

			word_entropies = np.array([self.calculate_word_entropy(word) for word in self.current_possible_words]);
			max_entropy_idx = np.argmax(word_entropies);
			print(np.max(word_entropies))
			return self.current_possible_words[max_entropy_idx];

	def generate_solver_guess2(self,rule_list):
		self.update_word_list(rule_list);
		print(len(self.current_possible_words));
		return random.choice(self.current_possible_words);


# Begin playing:

rule_list = []

game = WordleGameStandard()
game_state = game.query_game_state();
game.start();
solver = Solver()
while game_state not in ['win', 'lose']:
	game.output();
	guess = solver.generate_solver_guess2(rule_list)
	val = game.attempt_guess(guess);
	if val == 'Length': 
		print('Word not long enough, try again')
		continue;
	elif val == 'Word': 
		print('Not a valid word, try again')
		continue;
	rule_list = solver.process_evaluation(guess, val);
	game_state = game.query_game_state()


game.output()
if game_state == 'win':
	print('Congratulations, you win!')
else:
	print('Damn, you lost!')
