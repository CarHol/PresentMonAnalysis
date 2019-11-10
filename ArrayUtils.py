import numpy as np

def getArrDiffs(dataSet):
    """
    Compares each successive number in a size n numpy array to its predecessor, generating a list of differences,
    returning a size (n - 1) numpy array.
    to a list.
    :param dataSet: A numpy array of numbers
    :return: An array containing the differences from the imput array.
    """
    # Calulate average frame-to-frame difference magnitude
    diffs = []
    frameIterator = iter(dataSet)
    prev = next(frameIterator)  # Get first frame time
    for frame in frameIterator:
        diffs.append(frame - prev)
        prev = frame

    return np.array(diffs)