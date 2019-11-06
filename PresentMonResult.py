# IMPORTS:
import constants

# CLASSES:
# Simple structure to hold result data
class PresentMonResult:
# Result lists
    dropped = []                # Frame dropped flags
    timeStamps = []             # Time stamps for all frames
    msBetweenPresents = []
    msBetweenDisplayChange = []
    msInPresentApi = []
    msUntilRenderComplete = []
    msUntilDisplayed = []

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
    def addFrame(self, timeInSeconds, msBetweenPresents, msBetweenDisplayChange, msInPresentApi, msUntilRenderComplete,
                 msUntilDisplayed):
        self.timeStamps.append(timeInSeconds)
        self.msBetweenPresents.append(msBetweenPresents)
        self.msBetweenDisplayChange.append(msBetweenDisplayChange)
        self.msInPresentApi.append(msInPresentApi)
        self.msUntilRenderComplete.append(msUntilRenderComplete)
        self.msUntilDisplayed.append(msUntilDisplayed)


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

        # Iterate
        for line in file:
            columns = line.strip().split(',')
            # Ignore blank or incomplete lines
            if len(columns) == 15:
                result.dropped.append(int(columns[8]) == 1)
                result.timeStamps.append(float(columns[9]))
                result.msBetweenPresents.append(float(columns[10]))
                result.msBetweenDisplayChange.append(float(columns[11]))
                result.msInPresentApi.append(float(columns[12]))
                result.msUntilRenderComplete.append(float(columns[13]))
                result.msUntilDisplayed.append(float(columns[14]))

    # Return populated object
    return result
