import numpy as np

def main():
    a = makeMinesweeperMap(10,7,5,(0,1))
    print(a)

def makeMinesweeperMap(w, h, bombs, start: tuple) -> list[list]:
    """
    Takes grid width and height, amount of bombs and start cell
    Returns a list of list of a randomized minesweeper board/map"
    """
    bombLocations = placeBombs(w, h, bombs, start)    
    map = makeHints(w, h, bombLocations)
    return map
    

def makeHints(w, h, bombLocations):
    """
    Takes grid width and height and a numpy array of 1s (bomb) and 0s (no bomb)
    loops the array and creates a new array with >9 meaning bomb
    then incrementing neighbouring hints
    Returns finished minesweeper map
    """
    map = np.zeros((h, w))
    for i in range(w):
        for j in range(h):
            if bombLocations[j, i]:
                map[j, i] += 10
                bombIncrement(map, i, j)
    return map

def placeBombs(w, h, bombs, start):
    """
    Places bombs as 1s in a w*h numpy array, avoiding bombs on start
    Returns an array of bomb locations
    """
    tiles = w * h
    startIndex = start[0] + start[1]*w  # Mapping tuple coordinates to integer index between (0, tiles-1)
    
    allIndexes = np.arange(0, tiles)
    notBombs = getNeighbours(start[0], start[1], w, h)
    notBombs = list(map(lambda pos: pos[0] + pos[1]*w, notBombs))
    notBombs.append(startIndex)
    """notBombs = np.array([startIndex-w-1, startIndex-w, startIndex-w+1,
                        startIndex-1, startIndex, startIndex+1, 
                        startIndex+w-1, startIndex+w, startIndex+w+1])
    """
    possibleIndexes = np.setdiff1d(allIndexes, notBombs)
    np.random.shuffle(possibleIndexes)
    bombIndexes = possibleIndexes[:bombs]
    
    bombLocations = np.zeros(tiles)
    for i in bombIndexes:
        bombLocations[i] = 1
        
    bombLocations = np.reshape(bombLocations, (h, w)) 
    return bombLocations


def bombIncrement(map, i, j, amount=1):
    """
    Loops through a bomb cell's neighbours and increments them
    """
    w, h = map.shape[1], map.shape[0]
    neighbours = getNeighbours(i, j, w, h)
    for n in neighbours:
        map[n[1], n[0]] += amount
        

def getNeighbours(i, j, w, h):
    """
    Finds all valid neighbours to (i,j) in size (w,h)"""
    if 0>i or i>= w:
        raise IndexError("i er utenfor range")
    if 0>j or j>= h:
        raise IndexError("j er utenfor range")
    
    neighb = []
    if i > 0:
        neighb.append((i-1, j)) 
        if j > 0:
            neighb.append((i-1, j-1))
        if j < h-1:
            neighb.append((i-1, j+1))      
    if i < w-1:
        neighb.append((i+1, j))
        if j > 0:
            neighb.append((i+1, j-1))
        if j < h-1:
            neighb.append((i+1, j+1)) 
    if j > 0:
        neighb.append((i, j-1))
    if j < h-1:
        neighb.append((i, j+1))
    return neighb
     
if __name__ == '__main__':
    main()