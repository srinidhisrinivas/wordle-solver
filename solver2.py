from wordlegame import WordleGameStandard
import numpy as np
import random
import time
import matplotlib.pyplot as plt
import json
import pandas as pd

class Solver:
	def __init__(self, possible_words = [], length=5):
		self.all_possible_words = []
		self.game_word_length = 5;
		if len(possible_words) != 0:
			self.all_possible_words = possible_words;
		else:
			with open('words_alpha.txt','r') as f:
				self.all_possible_words = f.read().split('\n')
			self.all_possible_words = list(filter(lambda word: len(word) == self.game_word_length, self.all_possible_words));

		
		
		self.current_possible_words = self.all_possible_words.copy();
		#self.current_possible_words = random.sample(self.current_possible_words,100)

		self.letters = [chr(i) for i in range(65,65+26)]
		self.letter_probs = np.zeros(shape=(len(self.letters),self.game_word_length))

		# Lookup table for outcomes
		self.outcome_map = pd.read_csv('outcome_dict.csv')
		self.outcome_map = self.outcome_map.set_index(['W1','W2'])
		# with open('outcome_dict.json', 'r') as f:
		# 	self.outcome_map = json.load(f);
		



	"""
	 Update the word list based on a set of rules. Rules are based on
	 feedback of the guess from the wordle game.

	 Rules are of the form:

	 "<letter> at <position>" - (<letter>, True, <position>)
	 "<letter> not at <position>" - (<letter>, False, <position>)
	 "<letter> not in word" - (<letter>, False, -1)
	"""
	def update_word_list(self, word, evaluation):

		if len(word) == 0: return self.current_possible_words;
		# print(word, evaluation)
		print(word in self.current_possible_words);

		match_words = []
		for word2 in self.current_possible_words:
			eval_ = self.evaluate_guess_fetch(word2, word);
			# if len(self.current_possible_words) < 20:
			# 	print(eval_);
			if eval_ == evaluation:
				# print(word2, eval_);
				match_words.append(word2);

		self.current_possible_words = match_words;
	
	def evaluate_guess(self,word, guess):
		# print(word,guess)
		word_split = [char for char in word]
		evaluation = ['_']*self.game_word_length;
		covered_word_ids = []
		covered_guess_ids = []
		guess_split = [char for char in guess];
		for idx,letter in enumerate(guess_split):
			if letter == word_split[idx]:
				evaluation[idx]='Y'
				covered_word_ids.append(idx);
				covered_guess_ids.append(idx);

		remaining_word_letters = []
		for i in range(self.game_word_length):
			if i not in covered_word_ids:
				remaining_word_letters.append(word_split[i]);
			else:
				remaining_word_letters.append('_')

		for idx,letter in enumerate(guess_split):
			
			if idx in covered_guess_ids: continue;
			if letter in remaining_word_letters:
				evaluation[idx] = 'O'
				found_letter_idx = remaining_word_letters.index(letter)
				covered_word_ids.append(found_letter_idx)
				remaining_word_letters = []
				for i in range(self.game_word_length):
					if i not in covered_word_ids:
						remaining_word_letters.append(word_split[i]);
					else:
						remaining_word_letters.append('_')
			else:
				evaluation[idx] = 'X'


		return ''.join(evaluation)

	"""
	Evaluating guess by searching from lookup table rather than computing output

	Currently does not work much faster than computing output
	"""
	def evaluate_guess_fetch(self, word, guess):
		# print(str((word,guess)))
		# print(self.outcome_map.loc[self.outcome_map.Pair==str((word,guess))].Eval.item());
		return self.outcome_map.loc[(word,guess),'Eval']
	"""
	Finds the word in the remaining set of possible words that creates
	the most uniform distribution of outcomes (evaluations) when 
	evaluated against all other words. 

	This essentially tests out all possible moves at a given step, and
	finds the word that maximize the entropy of the outcome distribution,
	thereby cutting out as many words as possible at each step.
	"""
	def calculate_max_info_split(self, guess_num):
		max_entropy = 0;
		max_entropy_dist = {}
		max_entropy_word = self.current_possible_words[0];

		# Testing each possible word, and building the outcome distribution
		# for each
		start = time.time();
		for idx,word1 in enumerate(self.current_possible_words):
			# Initialize outcome distribution as map of outcome with counts
			current_outcome_dist = {}

			# Calculating the outcome of each word and adding it to the 
			# distribution
			for idx2,word2 in enumerate(self.current_possible_words):
				print(idx,len(self.current_possible_words),idx2, end='\r')
				outcome = self.evaluate_guess_fetch(word2, word1);
				if outcome not in current_outcome_dist:
					current_outcome_dist[outcome] = 1;
				else:
					current_outcome_dist[outcome] += 1;

			outcome_counts = np.array(list(current_outcome_dist.values()));

			outcome_probs = outcome_counts / outcome_counts.sum();
			

			# adjust all probability 0 to 1 to avoid errors in calculating 
			# logarithm for entropy. Both 0 and 1 probabilities map to 
			# 0 information in entropy calculation

			adj_outcome_probs = np.where(outcome_probs == 0, 1, outcome_probs);
			# print(adj_outcome_probs)
			outcome_prob_logs = np.log(adj_outcome_probs)

			outcome_dist_entropy = -(adj_outcome_probs * outcome_prob_logs).sum()

			# print(outcome_dist_entropy);
			if outcome_dist_entropy > max_entropy:
				max_entropy = outcome_dist_entropy;
				max_entropy_dist  = current_outcome_dist.copy();
				max_entropy_word = word1;

		end = time.time();
		print("Time for calculation: " + str(end - start));
		max_outcome_counts = np.array(list(max_entropy_dist.values()));

		# Plot the distribution of outcomes for the distribution with 
		# highest information
		plt.figure();
		plt.bar(list(range(len(max_outcome_counts))), max_outcome_counts);
		plt.title("Guess #{}: {}".format(guess_num, max_entropy_word))
		return (max_entropy_word, max_entropy, max_entropy_dist);


	def generate_solver_guess(self,guess, val, guess_num):
		self.update_word_list(guess, val);
		
		guess, ent, _2 = self.calculate_max_info_split(guess_num);
		print('\n')
		print(len(self.current_possible_words));
		print("Max entropy: " + str(ent));
		return guess
	


# Begin playing:
guess = ''
val = ''
rule_list = []

game = WordleGameStandard()
possible_words = game.get_word_list()
game_state = game.query_game_state();
game.start();
solver = Solver(possible_words=possible_words)
while game_state not in ['win', 'lose']:
	game.output();
	guess = solver.generate_solver_guess(guess, val, game.num_attempts)
	val = game.attempt_guess(guess);
	if val == 'Length': 
		print('Word ' + guess + ' not long enough, try again')
		continue;
	elif val == 'Word': 
		print(guess + ' not a valid word, try again')
		continue;
	# rule_list = solver.process_evaluation(guess, val);
	game_state = game.query_game_state()

game.output()
if game_state == 'win':
	print('Congratulations, you win!')
else:
	print('Damn, you lost!')

plt.show()