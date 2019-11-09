import argparse
import numpy as np
import time
from bokeh.plotting import figure, output_file, show
from bokeh.models import Span, Label, Tabs, Panel
from bokeh.models.widgets import Div
from bokeh.layouts import column, row, widgetbox
from PresentMonResult import PresentMonResult, LoadFromCsv

# Debug?
debug = False

# FUNCTIONS
def CreateHistogram(data, width, histTitle, xLabel, yLabel, indicateMu=True):
        # Get data from result:
        #indicateMu = True, indicateSigma=0
        # TODO: Add automatic fps conversion in PresentMonResult class
        # TODO: Add parallellization for large datasets
        mu = np.mean(data)
        sigma = np.std(data)

        # Create plot (hard coded settings for now)
        p = figure(title=histTitle, x_axis_label=xLabel,
                   y_axis_label=yLabel)
        p.x_range.end = mu + 4*sigma
        p.x_range.start = mu - 4*sigma
        p.width = width
        p.toolbar.logo = None
        hist, edges = np.histogram(data, density=True, bins=min(2000, data.size))
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color="#34d5eb", line_color="#34d5eb")

        # Add markers for mean, stdev
        if indicateMu:
            muLine = Span(location=mu, dimension='height', line_color='red', line_width=1)
            p.renderers.extend([muLine])


        # Create descriptive label:
        dataDescription = "Mean: " + "{:10.3f}".format(mu) + ",   StdDev: " + "{:10.3f}".format(sigma)
        labels = Label(x=0, y=0, x_units='screen', y_units='screen', text=dataDescription, border_line_color='black',
                       render_mode='css', background_fill_color='white')
        p.add_layout(labels)

        # Return
        return p

def CreateTabbedHistogram(dataSet, width):
        # Create the charts
        frequencyData = 1000. / dataSet.msBetweenPresents

        timeHistogram = CreateHistogram(dataSet.msBetweenPresents,
                                        width,
                                        histTitle="Frametimes",
                                        xLabel="Frame time (ms)",
                                        yLabel="Relative frequency")

        frequencyHistogram = CreateHistogram(frequencyData,
                                             width,
                                             histTitle="Framerate",
                                             xLabel="Framerate (fps)",
                                             yLabel="Relative frequency")

        # Create panels
        timeTab = Panel(child=timeHistogram, title="Frametimes")
        frequencyTab = Panel(child=frequencyHistogram, title="FPS")

        # Create tabs
        return Tabs(tabs=[timeTab, frequencyTab])




def CreateLineDiagram(frameData, timeData, width, chartTitle, xLabel, yLabel):
        p = figure(title=chartTitle, x_axis_label=xLabel, y_axis_label=yLabel)
        p.width = width
        p.toolbar.logo = None

        # Add line
        p.line(timeData, frameData, line_width=0.5)

        return p


def CreateTabbedLineDiagram(dataSet, width):
    # Create charts
    frequencyData = 1000. / dataSet.msBetweenPresents

    timeChart = CreateLineDiagram(dataSet.msBetweenPresents, dataSet.timeStamps, width, "Framtimes", "Runtime (s)", "Frame time (ms)")
    frequencyChart = CreateLineDiagram(frequencyData, dataSet.timeStamps,  width, "Framerate", "Runtime (s)", "Framerate (fps)")

    # Create panels
    timeTab = Panel(child=timeChart, title="Frametimes")
    frequencyTab = Panel(child=frequencyChart, title="Framerate")

    return Tabs(tabs=[timeTab, frequencyTab])

def GenerateTextStatistics(data, width):
        # Number of frames:
        nFrames = data.timeStamps.size
        totalTimeSeconds = data.timeStamps[-1]

        # Calulate average frame-to-frame difference magnitude
        diffs = []
        fpsFrames = 1000. / data.msBetweenPresents
        frameIterator = iter(data.msBetweenPresents)
        prev = next(frameIterator)      # Get first frame time
        for frame in frameIterator:
                diffs.append(abs(frame - prev))
                prev = frame
        maxDiffAmp = np.max(diffs)
        minDiffAmp = np.min(diffs)
        avgDiffAmp = np.mean(diffs)

        # Mean, meadian and standard deviation times
        meanFrametime = np.mean(data.msBetweenPresents)
        medianFrameTime = np.median(data.msBetweenPresents)
        stdDevFrameTime = np.std(data.msBetweenPresents)

        # Corresponding framerates:
        meanFramerate = 1000. / meanFrametime
        medianFramerate = 1000. / medianFrameTime
        stdDevFramerate = 1000. / stdDevFrameTime

        # Thresholds (time spent above x fps)
        # (threshold fps, list of frames, fraction of total time spent)
        thresholds = [(60, [], 0.0),
                      (120, [], 0.0),
                      (144, [], 0.0)]
        for frame in data.msBetweenPresents:
            for index in range (0,len(thresholds)):
            #for threshold in thresholds:
                if (1000. / frame) > thresholds[index][0]:
                    thresholds[index][1].append(frame)

                    thresholds[index] = (thresholds[index][0], thresholds[index][1], thresholds[index][2] + (frame / 1000)/totalTimeSeconds)

        # Threshold statistics

        # Generate graphic
        text =  "<div style=\"padding-left:10px\">" + \
                "<h3>Basic statistics</h3>" + \
                "<p>Number of processed frames: " + str(nFrames) + \
                "<p>Median: " + "{:10.3f}".format(medianFramerate) + " fps (" + "{:10.3f}".format(medianFrameTime) +" ms)" + \
                "<p>Mean: " + "{:10.3f}".format(meanFramerate) + " fps (" + "{:10.3f}".format(meanFrametime) + " ms)" + \
                "<p>Standard deviation: " + "{:10.3f}".format(stdDevFramerate) + " fps (" + "{:10.3f}".format(stdDevFrameTime) + " ms)" + \
                "<h3>Frame-to-frame statistics</h3>" + \
                "<p>Average magnitude of difference: " + "{:10.3f}".format(avgDiffAmp) + " ms</p>" + \
                "<p>Maximum magnitude of difference: " + "{:10.3f}".format(maxDiffAmp) + " ms</p>" + \
                "<p>Minimum magnitude of difference: " + "{:10.3f}".format(minDiffAmp) + " ms</p>"
        text = text + "<h3>Framerate threshold statistics:</h3>"
        for threshold in thresholds:
            text = text + "<p>Fraction of time spent above " + str(threshold[0]) + " fps: " + "{:10.3f}".format(threshold[2]*100) + "%</p>"
        text = text + "</div>"
        div = Div(text=text, width=width)
        return div

# SETTINGS
# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-debug", help="Enable debug mode", action="store_true")
parser.add_argument("-file", help="Path to a PresentMon generated CSV-file")

startTime = time.time()

args = parser.parse_args()
fileSource = "TestData/r5apex-0.csv"
if args.file:
    fileSource = args.file
elif args.debug:
    debug = True
else:
    parser.error('Either file or debug mode most be selected')

# Load data
data = LoadFromCsv(fileSource)

# Set output file
output_file("Analysis.html")

# Generate plots
histogram = CreateTabbedHistogram(data, 1068)               # Relative frequency histograms
lineDiagram = CreateTabbedLineDiagram(data, 1068)           # Framerate/frametimes as line diagram
div = GenerateTextStatistics(data, 1068)                    # Statistics in text form

endTime = time.time()                                       # For debug diagnostics
if debug:
    print ("Script runtime: " + str(endTime - startTime))

# Output and show
show(row(column(histogram, lineDiagram),div))