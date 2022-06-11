import os
import shutil
import subprocess
from PIL import Image, ImageEnhance
import numpy as np
from skimage import io

merge_images = []

png_seq = []
last_motion = ''
motion_unit = []

compress_images = []
compress_index = 0

stroke_ext_name = ''

exec_path = "pngquant --quality=0-50 {} --ext {}" 

def pixellize(input_file_path, output_file_path, **kwargs):
	global pixelated
	img = Image.open(input_file_path)
	img_size = img.size
	if pixelated is True:
		# boost saturation of image 
		sat_booster = ImageEnhance.Color(img)
		img = sat_booster.enhance(float(kwargs.get("saturation", 1.0)))

		# increase contrast of image
		contr_booster = ImageEnhance.Contrast(img)
		img = contr_booster.enhance(float(kwargs.get("contrast", 1.0)))

		# reduce the number of colors used in picture
		img = img.convert('P', palette=Image.ADAPTIVE, colors=int(kwargs.get("n_colors", 32)))

		# reduce image size
		superpixel_size = int(kwargs.get("superpixel_size", 2))
		reduced_size = (img_size[0] // superpixel_size, img_size[1] // superpixel_size)
		img = img.resize(reduced_size, Image.BICUBIC ) # NEAREST BILINEAR ANTIALIAS BICUBIC  

		# resize to original shape to give pixelated look
		img = img.resize(img_size, Image.BICUBIC )

	# plot result
	# print(output_file_path)
	img.save(output_file_path)

def extend_file_name(file, extend_name = '_stroke'):
	global stroke_ext_name
	stroke_ext_name = extend_name
	(fp, ft) = os.path.splitext(file)
	ext_name = fp + extend_name + ft
	return ext_name

def stroke(file_path, root,  critical = 8):
	img = io.imread(file_path)

	row = img.shape[0]
	col = img.shape[1]

	for x in range(row):
		for y in range(col):
			color = (np.intc(img[x,y,0])+np.intc(img[x,y,1])+np.intc(img[x,y,2])) // 3
			# color = img[x,y,3]

			if color > 4:
				# left-top
				# if img[x-1, y-1, 3] == 0: 
				# 	img[x-1, y-1, 3] = 255
				if img[x, y-1, 3] == 0:
					img[x, y-1, 3] = 255
				
				# right-top
				# if img[x+1, y-1, 3] == 0:
				# 	img[x+1, y-1, 3] = 255

				if img[x-1, y, 3] == 0:
					img[x-1, y, 3] = 255
				if img[x, y, 3] == 0:
					img[x, y, 3] = 255
				if img[x+1, y, 3] == 0:
					img[x+1, y, 3] = 255

				# left-bottom
				# if img[x-1, y+1, 3] == 0:
				# 	img[x-1, y+1, 3] = 255
				if img[x, y+1, 3] == 0:
					img[x, y+1, 3] = 255

				# right-bottom
				# if img[x+1, y+1, 3] == 0:
				# 	img[x+1, y+1, 3] = 255		
				# pass
	update_file_path = file_path.split('/').pop()
	save_path = "stroked_png/" + root  +'/'+ update_file_path
	to_makedirs("stroked_png/" + root  +'/')
	# # save_path = extend_file_name(file_path)
	io.imsave(save_path, img)
	pass

def merge_process(motion_name):
	global merge_images, merge_dir, compress_images
	target_path = merge_dir + motion_name+'.png'
	target = Image.new('RGBA', (ceil_size * (frames+1), ceil_size))
	for i in range(len(merge_images)):
		target.paste(merge_images[i], (i*ceil_size, 0))
		merge_images[i].close()
	print("merge_process -> target_path:", target_path)
	target.save(target_path)
	compress_images.append(target_path)
	pass


def gen_real_path(motion_name):
	global merge_images
	merge_images.clear()
	# print("motion_unit:", motion_unit)
	motion_unit.reverse()
	for mo_img in motion_unit:
		merge_images.append(Image.open(mo_img))
	merge_process(motion_name)
	pass

def start_process(file_dir):
	global merge_dir
	to_makedirs(merge_dir)

	for root, dirs, files in os.walk(file_dir):
		root = root.replace('\\', '/')
		'''
		print("root",root)
		print("dirs",dirs)
		print("files",files)
		'''
		for re in files:
			(fp, ft) = os.path.splitext(re)
			lines = ''
			re_pa = root
			if ft == '.png':
				if len(re_pa) == 0:
					lines = r''+re
				else: 
					lines = r''+re_pa+'/'+re
			if len(lines) > 0:
				# png_seq.append((lines, re, root, fp))
				''' add outline, stroke '''

				'''stroke pixelate '''
				stroke(lines, root)
				next_path = "stroked_png/" + lines
				to_makedirs("pixelated_png/" + root)
				pixelate_path = "pixelated_png/"+lines
				pixellize(next_path, pixelate_path)
				next_file_name = pixelate_path.split('/').pop()
				png_seq.append((pixelate_path, next_file_name, root))

				'''pixelate stroke'''
				# next_path = "pixelated_png/" + lines
				# to_makedirs("pixelated_png/" + root) 
				# pixellize(lines, next_path, saturation=1.0, contrast=1.0, superpixel_size=1, n_colors=16)
				# stroke(next_path, root)
				# stroke_path = 'stroked_png/' + lines
				# next_split = stroke_path.split('/')
				# next_file_name = next_split.pop()
				# png_seq.append((stroke_path, next_file_name, 'stroked_png/' +root))
		pass
	# print("png_seq:", png_seq[0])
	if len(png_seq)>0:
		# print(png_seq[0])
		divide(png_seq.pop())
		pass
	pass

def to_makedirs(dist_dir):
	is_exists=os.path.exists(dist_dir)
	if not is_exists:
		os.makedirs(dist_dir)
		pass

def divide(png_file):
	global last_motion, motion_unit

	uncompress = png_file[0]

	if last_motion == '':
		last_motion = png_file[2]
		motion_unit.append(uncompress)
	elif png_file[2] == last_motion:
		motion_unit.append(uncompress)
	elif png_file[2] != last_motion:
		# print("not last_motion",last_motion)
		gen_real_path(last_motion.split('/').pop())
		last_motion = png_file[2]
		motion_unit.clear()
		motion_unit.append(uncompress)

	if len(png_seq)>0:
		divide(png_seq.pop())
	else:
		# print("png_file",png_file)
		gen_real_path(png_file[2].split('/').pop())


def compress_process():
	global exec_path, compress_index

	if compress_index == len(compress_images):
		return
	
	file = compress_images[compress_index]
	file_name = file.split('/').pop()
	command = exec_path.format(file, 'min_' + file_name)
	bat_file = "encode.bat"
	with open(bat_file,"wt") as cmd_file:
		cmd_file.write(command)
		cmd_file.close()
	completeProcess = subprocess.run([bat_file], stdout=subprocess.PIPE, shell=True)
	if completeProcess.returncode == 0:
		os.remove(bat_file)
		compress_index += 1
		compress_process()
		pass
	pass

# 帧数
frames = 4
# 尺寸
ceil_size = 128
merge_dir = 'merge/'
pixelated = False 
start_process('AnimationDefault/')