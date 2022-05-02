average_num = 1
num_points = 260
sample_interval_s = 0.0000000005
x_origin = 0
x_reference = 0

# Create time array
times_s = [0] * num_points
for i in range(num_points):
    times_s[i] = (i - x_reference) * sample_interval_s + x_origin

print(times_s)
