from bokeh.plotting import figure, output_file, show
from bokeh.models import Span, Label
import numpy as np
from PresentMonResult import PresentMonResult, LoadFromCsv

# Hard coded source for now
data = LoadFromCsv("TestData/r5apex-0.csv")

# Get data from result:
x = data.timeStamps
y = data.msBetweenPresents
# TODO: Add automatic fps conversion in PresentMonResult class
# TODO: Add parallellization for large datasets
fps = []
for frame in y:
        fps.append(1000/frame)

mu = np.mean(fps)
sigma = np.std(fps)

# Set output file
output_file("Analysis.html")

# Create plot (hard coded settings for now)
p = figure(title="Performance distribution", x_axis_label='F (fps)', y_axis_label='Relative frequency (p(F = x))')
p.x_range.end = 100
p.x_range.start = 0
p.width = 1068
p.toolbar.logo = None
hist, edges = np.histogram(fps, density=True, bins=len(y))
p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
        fill_color="#34d5eb", line_color="#34d5eb")

# Add markers for mean, stdev
muLine = Span(location=mu, dimension='height', line_color='red', line_width=1)
sigmaLinePos = Span(location=(mu+sigma), dimension='height', line_color='green', line_width=1)
sigmaLineNeg = Span(location=(mu-sigma), dimension='height', line_color='green', line_width=1)
p.renderers.extend([muLine, sigmaLinePos, sigmaLineNeg])

# Create descriptive label:
dataDescription = "Mean: " + "{:10.3f}".format(mu) + ",   StdDev: " + "{:10.3f}".format(sigma)
labels = Label(x = 0, y = 0, x_units='screen', y_units='screen', text=dataDescription, border_line_color='black', render_mode='css', background_fill_color='white')
p.add_layout(labels)

p.legend.append("Test")
# Output and show
show(p)