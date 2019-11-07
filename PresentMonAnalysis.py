from bokeh.plotting import figure, output_file, show
from bokeh.models import Span, Label, Tabs, Panel
from bokeh.models.widgets import Div
from bokeh.layouts import column, widgetbox
import numpy as np
import time
from PresentMonResult import PresentMonResult, LoadFromCsv

# FUNCTIONS
def CreateHistogram(data, width, histTitle, xLabel, yLabel):
        # Get data from result:

        # TODO: Add automatic fps conversion in PresentMonResult class
        # TODO: Add parallellization for large datasets
        mu = np.mean(data)
        sigma = np.std(data)

        # Create plot (hard coded settings for now)
        p = figure(title=histTitle, x_axis_label=xLabel,
                   y_axis_label=yLabel)
        p.x_range.end = mu - 4*sigma
        p.x_range.start = mu + 4*sigma
        p.width = width
        p.toolbar.logo = None
        hist, edges = np.histogram(data, density=True, bins=min(2000, len(data)))
        p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
               fill_color="#34d5eb", line_color="#34d5eb")

        # Add markers for mean, stdev
        muLine = Span(location=mu, dimension='height', line_color='red', line_width=1)
        #sigmaLinePos = Span(location=(mu + sigma), dimension='height', line_color='green', line_width=1)
        #sigmaLineNeg = Span(location=(mu - sigma), dimension='height', line_color='green', line_width=1)
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
        #frequencyData = []
        frequencyData = 1000. / np.array(dataSet.msBetweenPresents)
        #for frame in dataSet.msBetweenPresents:
                #frequencyData.append(1000 / frame)

        timeHistogram = CreateHistogram(dataSet.msBetweenPresents, width, histTitle="Frametimes", xLabel="Frame time (ms)", yLabel="Relative frequency")
        frequencyHistogram = CreateHistogram(frequencyData, width, histTitle="Framerate", xLabel="Framerate (fps)", yLabel="Relative frequency")

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
        max = np.max(diffs)
        min = np.min(diffs)
        avg = np.mean(diffs)

        # Generate graphic
        text =  "<p>Frame-to-frame average magnitude of difference: " + "{:10.3f}".format(avg) + \
                "</p> <p>Frame-to-frame maximum magnitude of difference: " + "{:10.3f}".format(max) + \
                "</p>" + "<p>Frame-to-frame minimum magnitude of difference: " + "{:10.3f}".format(min) + "<br/> </p>"
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
show(column(div, histogram, lineDiagram))