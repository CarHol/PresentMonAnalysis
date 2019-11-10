import argparse
import numpy as np
import time
import ntpath
import style
import ArrayUtils
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
    # indicateMu = True, indicateSigma=0
    # TODO: Add automatic fps conversion in PresentMonResult class
    # TODO: Add parallellization for large datasets
    mu = np.mean(data)
    sigma = np.std(data)

    # Create plot (hard coded settings for now)
    p = figure(title=histTitle, x_axis_label=xLabel,
               y_axis_label=yLabel)
    p.x_range.end = mu + 4 * sigma
    p.x_range.start = mu - 4 * sigma
    p.width = width
    p.toolbar.logo = None
    hist, edges = np.histogram(data, density=True, bins=min(2000, data.size))

    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
           fill_color=style.histogramStyle['fill_color'], line_color=style.histogramStyle['line_color'])

    # Add markers for mean, stdev
    if indicateMu:
        muLine = Span(location=mu, dimension='height', line_color='red', line_width=1)
        p.renderers.extend([muLine])

    return p


def CreateTabbedHistogram(dataSet, width):
    # Create the charts
    frequencyData = 1000. /  np.array(dataSet)

    timeHistogram = CreateHistogram(dataSet,
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

    timeChart = CreateLineDiagram(dataSet.msBetweenPresents, dataSet.timeStamps, width, "Framtimes", "Runtime (s)",
                                  "Frame time (ms)")
    frequencyChart = CreateLineDiagram(frequencyData, dataSet.timeStamps, width, "Framerate", "Runtime (s)",
                                       "Framerate (fps)")

    # Create panels
    timeTab = Panel(child=timeChart, title="Frametimes")
    frequencyTab = Panel(child=frequencyChart, title="Framerate")

    return Tabs(tabs=[timeTab, frequencyTab])


def GenerateTextStatistics(data, width):
    # Get components:
    basicStatistics = GenerateBasicStatisticsText(data)
    frameToFrameStatistics = GenerateFrameToFrameStatistics(data)
    thresholdStatistics = GenerateThresholdStatistics(data, [60, 90, 120, 144])

    # Generate graphic
    text = "<div style=\"padding-left:10px\">" + \
           basicStatistics + frameToFrameStatistics + thresholdStatistics + \
           "</div>"
    div = Div(text=text, width=width)
    return div


# Text block generation:
def GenerateBasicStatisticsText(data):
    nFrames = data.timeStamps.size

    # Mean, meadian and standard deviation times
    meanFrametime = np.mean(data.msBetweenPresents)
    medianFrameTime = np.median(data.msBetweenPresents)
    stdDevFrameTime = np.std(data.msBetweenPresents)

    # Corresponding framerates:
    meanFramerate = 1000. / meanFrametime
    medianFramerate = 1000. / medianFrameTime
    stdDevFramerate = 1000. / stdDevFrameTime

    # Generate and return text
    return "<h3>Basic statistics</h3>" + \
           "<p>Number of processed frames: " + str(nFrames) + \
           "<p>Median: " + "{:10.3f}".format(medianFramerate) + " fps (" + "{:10.3f}".format(medianFrameTime) + " ms)" + \
           "<p>Mean: " + "{:10.3f}".format(meanFramerate) + " fps (" + "{:10.3f}".format(meanFrametime) + " ms)" + \
           "<p>Standard deviation: " + "{:10.3f}".format(stdDevFramerate) + " fps (" + "{:10.3f}".format(
        stdDevFrameTime) + " ms)"


def GenerateFrameToFrameStatistics(data):
    # Calulate average frame-to-frame difference magnitude
    diffsMs = ArrayUtils.getArrDiffs(data.msBetweenPresents)
    fpsFrames = 1000. / diffsMs

    maxDiffAmp = np.max(diffsMs)
    minDiffAmp = np.min(diffsMs)
    avgDiffAmp = np.mean(diffsMs)

    # Generate and return text
    return "<h3>Frame-to-frame statistics</h3>" + \
           "<p>Average magnitude of difference: " + "{:10.3f}".format(avgDiffAmp) + " ms</p>" + \
           "<p>Maximum magnitude of difference: " + "{:10.3f}".format(maxDiffAmp) + " ms</p>" + \
           "<p>Minimum magnitude of difference: " + "{:10.3f}".format(minDiffAmp) + " ms</p>"


def GenerateThresholdStatistics(data, thresholdFramerates):
    totalTimeSeconds = data.timeStamps[-1]

    thresholds = []
    for frameRate in thresholdFramerates:
        thresholds.append((frameRate, [], 0.0))

    # Thresholds (time spent above x fps)
    # (threshold fps, list of frames, fraction of total time spent)
    for frame in data.msBetweenPresents:
        for index in range(0, len(thresholds)):
            # for threshold in thresholds:
            if (1000. / frame) > thresholds[index][0]:
                thresholds[index][1].append(frame)
                thresholds[index] = (
                    thresholds[index][0], thresholds[index][1],
                    thresholds[index][2] + (frame / 1000) / totalTimeSeconds)

    # Piece together the values and return
    text = "<h3>Framerate threshold statistics:</h3>"
    for threshold in thresholds:
        text = text + "<p>Fraction of time spent above " + str(threshold[0]) + " fps: " + "{:10.3f}".format(
            threshold[2] * 100) + "%</p>"

    return text


# SETTINGS
plotWidth = 1068

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-debug", help="Enable debug mode", action="store_true")
parser.add_argument("-file", help="Path to a PresentMon generated CSV-file")

startTime = time.time()

args = parser.parse_args()
fileSource = "TestData/csgo-2.csv"
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

# Generate header
fileName = ntpath.basename(fileSource)
header = Div(text="<div class=headerDiv><h1>Analysis: {}</h1></div>".format(fileName), width=plotWidth, style=style.headerStyle)

# Generate plots
histogram = CreateTabbedHistogram(data.msBetweenPresents, plotWidth)  # Relative frequency histograms
frameToFrameHistogram =  CreateHistogram(ArrayUtils.getArrDiffs(data.msBetweenPresents),
                                    plotWidth,
                                    histTitle="Frame-to-frame deviations",
                                    xLabel="Frame time difference (ms)",
                                    yLabel="Relative frequency")
lineDiagram = CreateTabbedLineDiagram(data, plotWidth)  # Framerate/frametimes as line diagram
textStatistics = GenerateTextStatistics(data, plotWidth)  # Statistics in text form

endTime = time.time()  # For debug diagnostics
if debug:
    print("Script runtime: " + str(endTime - startTime))

# Output and show
show(
    column(
        header,
        row(
            column(
                Div(text="<div><h3>Performance distribution</h3></div>", width=plotWidth, style=style.subheaderStyle),
                histogram,
                Div(text="<div><h3>Performance timeline</h3></div>", width=plotWidth, style=style.subheaderStyle),
                lineDiagram,
                Div(text="<div><h3>Frame-to-frame deviations</h3></div>", width=plotWidth, style=style.subheaderStyle),
                frameToFrameHistogram
            ),
            textStatistics
        )
    )
)