#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 20:33:04 2019

@author: juho
"""

import numpy as np
from scipy.sparse import lil_matrix

from texas_hu_engine.wrappers import initRandomGames, executeActions, createActionsToExecute


class GameDataContainer:
    
    def __init__(self, gameStates):
        self.nGames = len(gameStates.boards)
        self.__shapeBoard = gameStates.boards.shape[1]
        self.__shapePlayers = (2, gameStates.players.shape[1])
        self.__shapeControlVars = gameStates.controlVariables.shape[1]
        self.__shapeAvailableActs = gameStates.availableActions.shape[1]

        # Initialize sparse matrixes for storing the game data. Sparse matrix was chosen 
        # as a data structure for storing the game data because it allows easy access to the 
        # data via numpy array slicing convention.
        maxNumberGameEvents = 500
        self.boardsMat = lil_matrix((self.nGames, maxNumberGameEvents*self.__shapeBoard), 
                                    dtype=np.int32)
        self.playersMat = lil_matrix((self.nGames*self.__shapePlayers[0], 
                                      maxNumberGameEvents*self.__shapePlayers[1]), dtype=np.int32)
        self.controlVariablesMat = lil_matrix((self.nGames, 
                                               maxNumberGameEvents*self.__shapeControlVars), 
                                              dtype=np.int16)
        self.availableActionsMat = lil_matrix((self.nGames, 
                                               maxNumberGameEvents*self.__shapeAvailableActs), 
                                              dtype=np.int64)
        
        # 'numEventsForGames' is used for slicing the sparse matrix. We need this to be able to 
        # separate the "true" zeros from empty zeros.
        self.__numEventsPerGame = np.zeros(self.nGames, dtype=np.int)
        self.__gameEventCounter = 1
        
        self.__boardsIdx, self.__playersIdx, self.__controlVariablesIdx, self.__availableActionsIdx \
            = 0,0,0,0
            
        self.addData(gameStates)
            
        
    def addData(self, gameStates):
        validMask, validMaskPlayers = gameStates.validMask, gameStates.validMaskPlayers
        boardsIdx, shapeBoard = self.__boardsIdx, self.__shapeBoard
        playersIdx, shapePlayers = self.__playersIdx, self.__shapePlayers
        controlVariablesIdx, shapeControlVars = self.__controlVariablesIdx, self.__shapeControlVars
        availableActionsIdx, shapeAvailableActs = self.__availableActionsIdx, \
            self.__shapeAvailableActs
        
        self.__numEventsPerGame[validMask] = self.__gameEventCounter
        
        # Store game data
        self.boardsMat[validMask, boardsIdx:boardsIdx+shapeBoard] = gameStates.boards[validMask]
        self.playersMat[validMaskPlayers, playersIdx:playersIdx+shapePlayers[1]] = \
            gameStates.players[validMaskPlayers]
        self.controlVariablesMat[validMask, 
                                   controlVariablesIdx:controlVariablesIdx+shapeControlVars] = \
            gameStates.controlVariables[validMask]
        self.availableActionsMat[validMask, 
                                   availableActionsIdx:availableActionsIdx+shapeAvailableActs] = \
            gameStates.availableActions[validMask]
        
        # Increase index counters
        self.__boardsIdx += shapeBoard
        self.__playersIdx += shapePlayers[1]
        self.__controlVariablesIdx += shapeControlVars
        self.__availableActionsIdx += shapeAvailableActs
        self.__gameEventCounter += 1
        
    
    def getGame(self, numGame):
        numEvents = self.__numEventsPerGame[numGame]
        
        boards = self.boardsMat[numGame, :numEvents*self.__shapeBoard].toarray()
        boards = boards.reshape((numEvents,-1))
        
        players = self.playersMat[numGame*2:numGame*2+self.__shapePlayers[0], 
                                  :numEvents*self.__shapePlayers[1]].toarray()
#        players = players.reshape((2,-1,9))
        
        controlVars = self.controlVariablesMat[numGame, :numEvents*self.__shapeControlVars].toarray()
        controlVars = controlVars.reshape((numEvents,-1))
        
        availableActions = self.availableActionsMat[numGame, 
                                                    :numEvents*self.__shapeAvailableActs].toarray()
        availableActions = availableActions.reshape((numEvents,-1))
        
        return boards, players, controlVars, availableActions


class Game:
    
    def __init__(self, boardStates, playerStates, controlVariables, availableActions):
        self.boardStates = boardStates
        self.playerStates = playerStates
        self.controlVariables = controlVariables
        self.availableActions = availableActions
        
        # TODO: status, winner, win amount..
#        self.status = 


import copy


# %%

datas = []

states = initRandomGames(5)

container = GameDataContainer(states)
datas.append(copy.deepcopy(states))

# %%

acts = createActionsToExecute(states.availableActions[:,0])
states = executeActions(states, acts)

container.addData(states)
datas.append(copy.deepcopy(states))

print(states.availableActions)

len(datas)

#boards, players = container.getGame(2)

# %%

n = 2

boards, players, controlVars, availableActs = container.getGame(n)


boards.shape
players.shape
controlVars.shape
availableActs.shape


ii = 0
datas[ii].players[n*2:n*2+2]
asd[ii*2:ii*2+2,:]
#players[:,:,ii]

asd = players.reshape((9*2,-1))

asd.shape
states.players.shape


# %%



nGames = 4
boards, players, controlVariables, availableActions = initGamesWrapper(nGames)

shapeBoard = boards.shape[1]
shapePlayers = (2, players.shape[1])
shapeControlVars = controlVariables.shape[1]
shapeAvailableActs = availableActions.shape[1]

boardsMat = lil_matrix((nGames, 500*shapeBoard), dtype=np.int32)
playersMat = lil_matrix((nGames*shapePlayers[0], 500*shapePlayers[1]), dtype=np.int32)
controlVariablesMat = lil_matrix((nGames, 500*shapeControlVars), dtype=np.int16)
availableActionsMat = lil_matrix((nGames, 500*shapeAvailableActs), dtype=np.int64)

# This is used for slicing the sparse matrix. We need this for separating the "true" zeros from
# empty zeros.
numEventsForGames = np.zeros(nGames, dtype=np.int)

boardsIdx, playersIdx, controlVariablesIdx, availableActionsIdx = 0,0,0,0


# %%


validMask = np.ones(len(boards), dtype=np.bool_)
validMaskPlayers = np.ones((len(boards)*2), dtype=np.bool_)

c = 1
#while(1):
    
    #%%
    
    #foldIdx = np.random.choice(len(amounts), size=int(0.05*len(amounts)), replace=0)
    #amounts[foldIdx] = 23151234
    
    numEventsForGames[validMask] = c
    
    boardsMat[validMask, boardsIdx:boardsIdx+shapeBoard] = boards[validMask]
    playersMat[validMaskPlayers, playersIdx:playersIdx+shapePlayers[1]] = players[validMaskPlayers]
    controlVariablesMat[validMask, controlVariablesIdx:controlVariablesIdx+shapeControlVars] = \
        controlVariables[validMask]
    availableActionsMat[validMask, availableActionsIdx:availableActionsIdx+shapeAvailableActs] = \
        availableActions[validMask]
    
    boardsIdx += shapeBoard
    playersIdx += shapePlayers[1]
    controlVariablesIdx += shapeControlVars
    availableActionsIdx += shapeAvailableActs

    amounts = availableActions[np.arange(len(boards)),np.random.randint(0,3,size=len(boards))]
    actionsToExec = createActionsToExecute(amounts)
    
    boards, players, controlVariables, availableActions, validMask, validMaskPlayers = \
        executeActionsWrapper(actionsToExec, boards, players, controlVariables, availableActions)
    
    c += 1
    
    # All games have finished
#    if(np.sum(validMask) == 0):
#        break


    print(np.sum(validMask))

#np.sum(controlVariables[:,-1] == -1) / len(controlVariables)



# %%

kk = 3

asd1 = boardsMat[kk,:numEventsForGames[kk]*shapeBoard].toarray()
asd2 = availableActionsMat[kk,:numEventsForGames[kk]*shapeAvailableActs].toarray()

asd2.reshape((numEventsForGames[kk],-1))
asd1.reshape((numEventsForGames[kk],-1)).shape






