# wordle-solver

Here is the game Wordle: https://www.powerlanguage.co.uk/wordle/

It is a word game where the object is to guess an N-letter word. Each time, the game gives feedback on each letter:
* Green - Letter is in the correct position
* Yellow - Letter is in the word but wrong position
* Gray - Letter is not in the word

Since there are limited moves and limited letters that can be played on each move, some moves are better at gaining information on the possible target word than others. For example, if one knows that 'E' is present in the last place in the word, playing that again in the same spot on the next turn does not lead to any new information. Instead of this, trying new letters that have not been tried before may instead give a clue as to which of those letters may exist in the word, even if not at that exact spot. With these principles in mind, I have attempted and will attempt to write solvers that solve the game using information-theoretical measures, i.e., trying to gain the most information out of each guess using probability measures, to solve the game in as few steps as possible. 

Of course, this repository also contains a simple command-line implementation of the game so that the solvers can interact with it.

More description to come soon, on the different solvers and how they attempt to gain information.
