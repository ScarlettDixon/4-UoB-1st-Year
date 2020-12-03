import matplotlib as mp
import matplotlib.pyplot as plt
import numpy as np


# Load trace
c = np.fromfile("trace_filtered.dat", np.int8)
x = range(1, 520001)



# Loop through trace, identifying peaks and troughs.
# The key power value 50, when crossed, indicates when a peak starts or ends.
# Special provision for the first and final peaks.

cycleList = []
currentStateLength = 30000

# Tracks gradient
peakTracker = False

peakCount = 0
lastTrough = 0

for count in range(30000, 520000):
	if((c[count] > 50) and peakTracker == False):
		peakTracker = True
		peakCount += 1
		
		# record the trough that just ended
		if(peakCount > 1):
			cycleList.append((count - currentStateLength, c[count]))
		
		currentStateLength = 0
		lastPeak = (count,c[count])

	elif((c[count] <= 48) and peakTracker == True):
		peakTracker = False
	
	if(c[count] <= 45 and peakCount > 1):
		lastTrough = (count, c[count])
		break

	currentStateLength += 1

# Add the special cases to the list
cycleList.append(lastPeak)
cycleList.append(lastTrough)

print(str(peakCount) + " peaks")

# The list contains the lengths of each iteration
# Iterations lasting <15000 are square; those longer are square and multiply.

previous = 0
count = 0
print("Cycle lengths (separator: 15000):")

result = ""

for cycle in cycleList:
	plt.plot(cycle[0], cycle[1], 'or')
	if(cycle[0] - previous < 15000):
		result += "0"
		#print("Iteration " + str(count) + " time: " + str(cycle[0] - previous) + "; [SQUARE]")	
	else:
		#print("Iteration " + str(count) + " time: " + str(cycle[0] - previous) + "; [SQUARE + MULTIPLY]")		
		result += "1"

	print(cycle[0]-previous)
	previous = cycle[0]
	count += 1

print("Extracted key: [" + result[:8] + " " + result[8:16] + " " + result[16:24] + " " + result[24:] + "]")
print("               [" + str(hex(int(result, 2))) + "]") 


print("", flush=True)
plt.ylim(42, 60)
plt.plot(x, c)
plt.show()