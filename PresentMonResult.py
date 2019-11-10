# IMPORTS:
import constants
import numpy as np

# CLASSES:
# Simple structure to hold result data
class PresentMonResult:
# Result lists
    dropped = np.array([])                  # Frame dropped flags
    timeStamps = np.array([])               # Time stamps for all frames
    msBetweenPresents = np.array([])
    msBetweenDisplayChange = np.array([])
    msInPresentApi = np.array([])
    msUntilRenderComplete = np.array([])
    msUntilDisplayed = np.array([])

    # Application,ProcessID,SwapChainAddress,Runtime,SyncInterval,PresentFlags,AllowsTearing,PresentMode,Dropped,TimeInSeconds,MsBetweenPresents,MsBetweenDisplayChange,MsInPresentAPI,MsUntilRenderComplete,MsUntilDisplayed
    def __init__(self, application, processId, swapChainAddress, runTime, syncInterval, presentFlags, allowsTearing,
                 presentMode):
        self.application = application
        self.processId = processId
        self.swapChainAddress = swapChainAddress
        self.runTime = runTime
        self.syncInterval = syncInterval
        self.presentFlags = presentFlags
        self.allowsTearing = allowsTearing
        self.presentMode = presentMode

    # Add frame data to the lists
    def addFrame(self, timeInSeconds, dropped, msBetweenPresents, msBetweenDisplayChange, msInPresentApi, msUntilRenderComplete,
                 msUntilDisplayed):
        self.timeStamps             = np.append(self.timeStamps, timeInSeconds)
        self.dropped                = np.append(self.dropped, dropped)
        self.msBetweenPresents      = np.append(self.msBetweenPresents, msBetweenPresents)
        self.msBetweenDisplayChange = np.append(self.msBetweenDisplayChange, msBetweenDisplayChange)
        self.msInPresentApi         = np.append(self.msInPresentApi, msInPresentApi)
        self.msUntilRenderComplete  = np.append(self.msUntilRenderComplete, msUntilRenderComplete)
        self.msUntilDisplayed       = np.append(self.msUntilDisplayed, msUntilDisplayed)

class ZippedPresentMonResult:
    resultRows = []

    def __init__(self, application, processId, swapChainAddress, runTime, syncInterval, presentFlags, allowsTearing,
                 presentMode):
        self.application = application
        self.processId = processId
        self.swapChainAddress = swapChainAddress
        self.runTime = runTime
        self.syncInterval = syncInterval
        self.presentFlags = presentFlags
        self.allowsTearing = allowsTearing
        self.presentMode = presentMode

    def addFrame(self, timeInSeconds, dropped, msBetweenPresents, msBetweenDisplayChange, msInPresentApi,
                 msUntilRenderComplete,
                 msUntilDisplayed):
        self.resultRows.append((timeInSeconds, dropped, msBetweenPresents, msBetweenDisplayChange, msInPresentApi,
                 msUntilRenderComplete,
                 msUntilDisplayed))



# HELPER FUNCTIONS:
# Load CSV file
def LoadFromCsv(filepath):
    # Check file and create result
    with open(filepath, "r+") as file:
        # Read the header and make sure it's correct
        header = file.readline().strip()
        if header == constants.presentMonHeader:
            # Read the first result line
            firstResult = file.readline().strip()
            columns = firstResult.split(',')

            # Verify length
            if len(columns) == 15:
                processName = columns[0]
                processId = columns[1]
                swapChainAddress = columns[2]
                runTime = columns[3]
                syncInterval = int(columns[4])
                presentFlags = int(columns[5])
                allowsTearing = int(columns[6]) == 1
                presentMode = columns[7]

                # Create result object
                result = PresentMonResult(processName, processId, swapChainAddress, runTime, syncInterval,
                                          presentFlags, allowsTearing, presentMode)
            else:
                raise ValueError("Invalid CSV header")
        else:
            raise ValueError("No valid data in CSV")

    # Populate results
    with open(filepath, "r+") as file:
        # Skip header
        file.readline()

        # Declare lists
        dropped = []
        timeStamp = []
        msBetweenPresents = []
        msBetweenDisplayChange = []
        msInPresentApi = []
        msUntilRenderComplete = []
        msUntilDisplayed = []

        # Iterate
        for line in file:
            columns = line.strip().split(',')
            # Ignore blank or incomplete lines
            if len(columns) == 15:
                dropped.append(int(columns[8]) == 1)
                timeStamp.append(float(columns[9]))
                msBetweenPresents.append(float(columns[10]))
                msBetweenDisplayChange.append(float(columns[11]))
                msInPresentApi.append(float(columns[12]))
                msUntilRenderComplete.append(float(columns[13]))
                msUntilDisplayed.append(float(columns[14]))

        # Synchronize timestamps with first frame rendering
        result.timeStamps               = np.array(timeStamp) - (timeStamp[0] - (max([msBetweenPresents[0],
                                                                                     msBetweenDisplayChange[0],
                                                                                     msInPresentApi[0],
                                                                                     msUntilRenderComplete[0],
                                                                                     msUntilDisplayed[0]]) / 1000))

        result.dropped                  = np.array(dropped)
        result.msBetweenPresents        = np.array(msBetweenPresents)
        result.msBetweenDisplayChange   = np.array(msBetweenDisplayChange)
        result.msInPresentApi           = np.array(msInPresentApi)
        result.msUntilRenderComplete    = np.array(msUntilRenderComplete)
        result.msUntilDisplayed         = np.array(msUntilDisplayed)

    # Return populated object
    return result

