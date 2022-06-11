import os
from PIL import Image
import subprocess
# 

merge_images = []

def compress(file):
    command = "pngquant --quality=50-80 {}".format(file)
    print("command:", command)
    fileName = "encode.bat"
    with open(fileName,"wt") as outFile:
        outFile.write(command)
        outFile.close()
    completeProcess = subprocess.run([fileName], stdout=subprocess.PIPE, shell=True)
    if completeProcess.returncode == 0:
        os.remove(fileName)
        print("compress complete")

def read_dir(dir_path):
    seq_list = []
    for root, dirs, files in os.walk(dir_path):
        root = root.replace('\\', '/')
        re_pa = root
        for re in files:
            (fp, ft) = os.path.splitext(re)
            lines = ''
            if ft == '.png':
                if len(re_pa) == 0:
                    lines = r'' + re
                else:
                    lines = r'' + re_pa + '/' + re
            if len(lines) > 0:
                seq_list.append((lines, re, root, fp))
    return seq_list

def merge():
	target_path = merge_images[0][3]+'_combine_texture.png'
	print(merge_images)
	ceil_size = Image.open(merge_images[0][0]).size
	for img in merge_images:
		merge_img_io.append(Image.open(img[0]))
	target = Image.new('RGBA', (ceil_size[0], ceil_size[1]*len(merge_images)))
	for i in range(len(merge_img_io)):
		target.paste(merge_img_io[i], (0, i*ceil_size[1]))
		merge_img_io[i].close()
	target.save(destination+target_path)
	# compress(destination+target_path)

destination = 'merge/'
merge_images = read_dir(destination)

merge_img_io = []

merge()
