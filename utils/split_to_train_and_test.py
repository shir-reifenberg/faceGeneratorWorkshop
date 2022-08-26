import os
import sys
import os.path as path

# This script get a file path containing all the photos spli
if (len(sys.argv) < 2 ):
    print ('a directory path is neccesery!')
source_folder = sys.argv[1]
for f in os.listdir(source_folder):
    try:
        d = os.path.join(source_folder, f)
        if os.path.isdir(d):
            folder = d
            print (f'now in folder: {folder}')
            count = 0
            for sub_file in os.listdir(folder):
                if (sub_file.lower().endswith(('.txt', '.tri', '.fg', '.xml', '.jpg', '.tga', '.csv'))):
                    file_to_delete = os.path.join(folder, sub_file)
                    os.remove(file_to_delete)
                    count +=1
            print (f'{count} files deleted from {folder}')
    except:
        print(f'error in handling:{f}')

    
