#!/usr/bin/env python

import os
from PIL import Image
import requests
import shutil
import string

DESTINATION_DIR = 'tiles/'
URI = string.Template('http://holc.s3-website-us-east-1.amazonaws.com/tiles/CA/SanJose/1937/16/$col/$row.png')
COL_START = 10564
ROW_START = 25424

def download():
	destination_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), DESTINATION_DIR)
	row_id = ROW_START
	col_id = COL_START
	while True:
		found_any_this_row = False
		while True:
			uri = URI.substitute(row=row_id, col=col_id)
			print uri
			r = requests.get(uri, stream=True)
			print r
			if r.status_code == 200:
				found_any_this_row = True
				with open(os.path.join(destination_dir, str(col_id) + '_' + str(row_id) + '.png'), 'wb') as f:
					# Decompress if compressed
					r.raw.decode_content = True
					shutil.copyfileobj(r.raw, f)
			elif r.status_code == 404:
				break
			col_id += 1
		if not found_any_this_row:
			break
		col_id = COL_START
		row_id += 1

def stitch():
	destination_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), DESTINATION_DIR)
	max_widths = {}
	max_heights = {}
	for filename in os.listdir(destination_dir):
		print filename
		col, row = filename.split('.')[0].split('_')
		image = Image.open(os.path.join(destination_dir, filename))
		max_widths[col] = max(max_widths.get(col, 0), image.size[1])
		max_heights[row] = max(max_heights.get(row, 0), image.size[0])

	stitched = Image.new('RGB', (sum(max_widths.values()), sum(max_heights.values())))
	x_offset = 0
	y_offset = 0
	for col in sorted(max_widths.keys()):
		for row in sorted(max_heights.keys()):
			filename = os.path.join(destination_dir, col + '_' + row + '.png')
			if os.path.exists(filename):
				image = Image.open(filename)
				stitched.paste(image, (x_offset, y_offset))
			y_offset += max_heights[row]
		x_offset += max_widths[col]
		y_offset = 0
	stitched.save('output.png')

if __name__ == '__main__':
	download()
	stitch()