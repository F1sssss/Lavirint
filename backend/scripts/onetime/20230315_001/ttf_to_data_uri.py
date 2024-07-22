import base64
import sys

with open(sys.argv[1], 'rb') as input_file:
    with open(sys.argv[2], 'w') as output_file:
        output_file.write('data:font/truetype;charset=utf-8;base64,%s' % base64.b64encode(input_file.read()).decode('utf-8'))
