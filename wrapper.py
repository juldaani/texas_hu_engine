#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 16 13:02:17 2019

@author: juho
"""

import numpy as np
from numba import jit

from texas_hu_engine.engine_numba import initGame, executeAction


@jit(nopython=True, cache=True, fastmath=True, nogil=True)
def initGames(nGames):
    
    boardsArr = np.zeros((nGames, 13), dtype=np.int32)
    playersArr = np.zeros((nGames*2, 8), dtype=np.int32)
    controlVariablesArr = np.zeros((nGames, 3), dtype=np.int16)
    availableActionsArr = np.zeros((nGames, 3), dtype=np.int32)
    
    for i in range(nGames):
        tmpCards = np.random.choice(52, size=9, replace=0)
        boardCards = tmpCards[:5]
        holeCards = np.zeros((2,2), dtype=np.int64)
        holeCards[0,:] = tmpCards[5:7]
        holeCards[1,:] = tmpCards[7:]
        smallBlindPlayerIdx = np.random.randint(0,high=2)
        smallBlindAmount = np.random.randint(1,high=100)
        initStacks = np.array([np.random.randint(smallBlindAmount*2, high=smallBlindAmount*1000 + \
                                                 np.random.randint(smallBlindAmount)), 
                               np.random.randint(smallBlindAmount*2, high=smallBlindAmount*1000 + \
                                                 np.random.randint(smallBlindAmount))])
        board, players, controlVariables, availableActions = initGame(boardCards, smallBlindPlayerIdx, 
                                                                      smallBlindAmount, initStacks.copy(), 
                                                                      holeCards)
    
        boardsArr[i,:] = board
        playersArr[i*2:i*2+2,:] = players
        controlVariablesArr[i,:] = controlVariables
        availableActionsArr[i,:] = availableActions
        
    return boardsArr, playersArr, controlVariablesArr, availableActionsArr
    
    

nGames = 1000
boards, players, controlVariables, availableActions = initGames(nGames)




# %%


