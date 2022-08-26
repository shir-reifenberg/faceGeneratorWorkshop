from aifc import Error
import os
import sys
import os.path as path

from numpy import identity

# This function performs some operations required before splitting the data to test and train:
# 1. removes all .xml files
# 2. creates a unique name for each folder and photo
# 3. remove the redundent /images nested folder
def chunk_preproccess(root_folder):
    chunk_name = root_folder.split('\\')
    print (f'chunk name is: {chunk_name[-1]}')
    for f in os.listdir(root_folder):
        identity_dir = os.path.join(root_folder, f)
        if os.path.isdir(identity_dir):
            # change the directory name
            new_dir = os.path.join(root_folder, chunk_name[-1]+'_'+f)
            os.rename(identity_dir, new_dir)
            images_dir = os.path.join(new_dir+'\\images')
            for file_name in os.listdir(images_dir):
                file_path = os.path.join(images_dir, file_name)
                # remove file if its xml
                if (file_name.lower().endswith(('.xml'))):
                    file_to_delete = file_path
                    os.remove(file_to_delete)
                else: 
                # change file name to contain chunk name
                    new_file_name = os.path.join(new_dir, chunk_name[-1]+'_'+file_name)
                    os.rename(file_path, os.path.join(new_dir, new_file_name))
 
def split_data_set():
    Error('not implemented yet')
        
if __name__ == '__main__':
    if (len(sys.argv) < 2 ):
        print ('a directory path is neccesery!')
        exit()
    source_folder = sys.argv[1]
    chunk_preproccess(source_folder)
