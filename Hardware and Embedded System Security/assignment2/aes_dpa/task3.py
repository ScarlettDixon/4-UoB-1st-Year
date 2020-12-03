import matplotlib as mp
import matplotlib.pyplot as plt
import numpy as np

def apply_sbox(sbox, input_byte, key_byte):
	return sbox[input_byte ^ key_byte]

def msb(input_byte):
	return (input_byte & 0b10000000) != 0

# Used for part 3-1, but not thereafter
def plottrace(tracelist):
	x = range(0, 401)
	for trace in tracelist:
		plt.plot(x, trace[0])	
	plt.show()

##################################################################

number_of_traces = int(input("Specify number of traces to load: "))

# Load sbox values from file
sbox = []

sbox_f = open("sbox-concat.txt", "r")
sbox_linear = sbox_f.readline()
sbox_f.close()

for i in range(0, 256):
	sbox.append(int(sbox_linear[i*2:i*2 +2], 16))

print("Loaded sbox:")
count = 0
for v in sbox:
	print(format(v, '02x') + " ", end='')
	count += 1
	if(count % 16 == 0):
		print()

print("", flush=True)



# Load inputs and traces from file, and associate them with each other as tuples
inputs_f = open("./aes_traces/inputs.txt", "r")

# traces are a tuple (trace, input)
tracelist = []
for i in range(0, number_of_traces):
	trace = np.fromfile("./aes_traces/traces/trace" + str(i) + ".dat", np.int8)
	data = int(inputs_f.readline()[0:2], 16)
	tracelist.append((trace,data))

inputs_f.close()
print("Loaded " + str(len(tracelist)) + " traces.")



# print input values
print("First byte of input for loaded traces:")
for trace in tracelist:
	print(format(trace[1], '02x') + ", ", end='')
print("", flush=True)



# key_buckets is a list of tuples (bucket0, bucket1), where each bucket is a list of trace objects that are themselves tuples (trace, input) 
key_buckets = []

# Calculate output of sbox using key candidates 0-15 through all traces, extract MSB of output, and thus allocate traces to buckets
for key in range(0, 16):
	bucket0 = []
	bucket1 = []
	for trace in tracelist:
		# apply the key to all the traces
		b = apply_sbox(sbox, trace[1], key)

		if(msb(b) == 1):
			bucket1.append(trace)
		else:
			bucket0.append(trace)

	key_buckets.append( (bucket0, bucket1) )




# now for each key, take the mean of each bucket, and find the difference between those buckets.
# The mean is taken for corresponding points in each trace, not of all the points in one trace.

# List of difference of mean traces
key_average_buckets = []

# here 'key' is the tuple of the two buckets belonging to that key
for key in key_buckets:
	diff_trace = []
	for i in range(0, 401):
		# zero bucket
		bucket0_point_average = 0
		for trace in key[0]:
			bucket0_point_average += trace[0][i]			# add up corresponding traces...
		bucket0_point_average = bucket0_point_average / len(key[0])     # ...and divide by the size of the bucket

		# one bucket
		bucket1_point_average = 0
		for trace in key[1]:
			bucket1_point_average += trace[0][i]                    # as for bucket0
		bucket1_point_average = bucket1_point_average / len(key[1])

		diff_trace.append(bucket0_point_average - bucket1_point_average)	

	key_average_buckets.append( diff_trace )




# add the difference of mean curves to a plot.
# In the process, find the largest absolute value in the curves and the associated key

x = range(0, 401)
max = 0
max_key = 0
count = 0
for diff in key_average_buckets:
	label = "Key " + str(count)
	plt.plot(x, diff, label=label)
	for i in diff:
		if(abs(i) > abs(max)):
			max = i
			max_key = count

	count += 1

print("Maximum absolute value was " + str(max) + " for key " + str(max_key))
axes = plt.gca()
area = axes.get_position()
axes.set_position([area.x0, area.y0, area.width * 0.75, area.height])
plt.legend(loc='center left', bbox_to_anchor=(1,0.5))
plt.show()
