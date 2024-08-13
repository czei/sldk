import random
import sys

sys.path.append('/src/lib')


def write_random_file(filename, length):
    with open(filename, 'w') as f:
        # Generate random data
        # data = ''.join(random.choice('abcdefghijklmnopqrstuvwxyz0123456789', )
        for i in range(length):
            data = random.getrandbits(8)
            # Write data to file
            f.write(chr(data))


for i in range(1000):
    filename = f"file{i}.dat"
    print(f"Writing file: {filename}")
    write_random_file(filename, 200)
