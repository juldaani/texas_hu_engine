#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 25 15:32:22 2018

@author: juho
"""

import unittest
import numpy as np
import itertools

from hand_eval.evaluator import evaluate
from texas_hu_engine.engine import initGame, executeAction
from hand_eval.params import cardToInt, intToCard

SEED = 123


"""
- evaluate cards correctly
- pot not negative
- stacks not negative
- bets not negative
- money is not appearing/disappearing out of the blue (pot, stacks, bets)
- money is transferred correctly:
    - when betting round is finished money is transferred to pot
    - after raise/call action money is transferred properly to player's stacks
    - valid amount of money is transferred to bets/pot after each action/betting round
- raise amounts are correct
- call amount correct
- pre/postflop start player correct
- visible cards are correct through betting rounds
- available actions are correct (raise amount not lower than call amount..)
- if player folds:
    - stacks/pot/bets are transferred correctly
    - gameEndState bit is turned on
- if showdown:
    - gameEndState bit is turned on
    - stacks/pot/bets are transferred correctly
- betting rounds are handled correctly:
    - go to next betting round if both players have acted at least once and bets
      are equal
- check that game goes to showdown if:
    - all-in
    - river
"""


# %%
# Evalueate cards correctly


np.random.seed(SEED)



def convertCardToInt(cards):
    return [cardToInt[card] for card in cards]

def convertIntToCard(ints):
    return [intToCard[intt] for intt in ints]



board = np.array(
        ['2h', '4h', '5h', '6s', '7d'],
        )

worseHoleCards = np.array(
        [']
        )
betterHoleCards = np.array(
        ['9s', 'Kc'],
        )

high = ['2h', '4h', '5h', '6s', '7d', '9s', 'Kc']
pair = ['Qs', 'Qc', '2c', '3d', '4h', '5s', 'Th']
twopairs = ['Ks', 'Kc', '2c', '2d', '4h', '5s', 'Th']
three = ['Th', 'Ts', 'Td', '2d', '5h', '8s', '7c']
straight = ['4s', '5s', '6s', '7d', '8h', 'Tc', 'Qh']
flush = ['3s', '5s', 'Js', 'Qs', 'Ks', '2d', '4h']
fullhouse = ['7c', '7h', 'Tc', 'Th', 'Td', '2h', '3c']
four = ['Kc', 'Ks', 'Kh', 'Kd', 'Td', '2s', '3s']
straighflush = ['5d', '6d', '7d', '8d', '9d', 'Jh', 'Qs', 'Kc']
royalflush = ['Ts', 'Js', 'Qs', 'Ks', 'As', '2d', '6c']

handsToTest = np.array([royalflush, straighflush, four, fullhouse, flush, straight, three, 
              twopairs, pair, high])

n = len(handsToTest)
k = 2
combs = np.array(list(itertools.combinations(np.arange(n), k)))

for comb in combs:
    betterHand = handsToTest[comb[0]]
    worseHand = handsToTest[comb[1]]
    
    evaluatedRankForBetterHand, _ = evaluate(convertCardToInt(betterHand))
    evaluatedRankForWorseHand, _ = evaluate(convertCardToInt(worseHand))
    
    # Lower rank means better hand
    assert evaluatedRankForBetterHand < evaluatedRankForWorseHand













