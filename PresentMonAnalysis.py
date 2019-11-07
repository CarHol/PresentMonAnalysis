from bokeh.plotting import figure, output_file, show
from bokeh.models import Span, Label, Tabs, Panel
from bokeh.models.widgets import Div
from bokeh.layouts import column, row, widgetbox
import numpy as np
import time
from PresentMonResult import PresentMonResult, LoadFromCsv

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


def CreateLineDiagram(data, width):
        p = figure(title="Framtimes", x_axis_label='T (ms)', y_axis_label='Frame')
        p.width = width
        p.toolbar.logo = None

        # Assign data
        x = data.timeStamps
        y = data.msBetweenPresents

        # Add line
        p.line(data.timeStamps, data.msBetweenPresents, line_width=0.5)

        return p

def GenerateTextStatistics(data, width):
        # Calulate average frame-to-frame difference magnitude
        diffs = []
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

        # Generate graphic
        text =  "<div style=\"padding-left:10px\">" + \
                "<h3>Basic statistics</h3>" + \
                "<p>Number of processed frames: " + str(data.timeStamps.size) + \
                "<p>Median: " + "{:10.3f}".format(medianFramerate) + " fps (" + "{:10.3f}".format(medianFrameTime) +" ms)" + \
                "<p>Mean: " + "{:10.3f}".format(meanFramerate) + " fps (" + "{:10.3f}".format(meanFrametime) + " ms)" + \
                "<p>Standard deviation: " + "{:10.3f}".format(stdDevFramerate) + " fps (" + "{:10.3f}".format(stdDevFrameTime) + " ms)" + \
                "<h3>Frame-to-frame statistics</h3>" + \
                "<p>Average magnitude of difference: " + "{:10.3f}".format(avgDiffAmp) + " ms</p>" + \
                "<p>Maximum magnitude of difference: " + "{:10.3f}".format(maxDiffAmp) + " ms</p>" + \
                "<p>Minimum magnitude of difference: " + "{:10.3f}".format(minDiffAmp) + " ms<br/> </p>" + \
                "</div>"
        div = Div(text=text, width=width)
        return div

# SETTINGS
# Hard coded source for now

startTime = time.time()
data = LoadFromCsv("TestData/r5apex-0.csv")

# Set output file
output_file("Analysis.html")

# Generate plots
histogram = CreateTabbedHistogram(data, 1068)
lineDiagram = CreateLineDiagram(data, 1068)
div = GenerateTextStatistics(data, 1068)

endTime = time.time()
print ("Time: " + str(endTime - startTime))
# Output and show
show(row(column(histogram, lineDiagram),div))