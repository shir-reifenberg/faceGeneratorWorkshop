from genericpath import isdir
import os
import sys
import os.path as path
import random

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
 

# splits the data set to train and test, per id
# e.g after the script we will have a train folder with all the ids
# and a test folder with all the ids
# the script doesnt delete the original id folders (due to permission issues), these should be manually removed after
def split_data_set_per_id(root_folder):
    
    # create a folder to each set
    test_dir_name = os.path.join(root_folder, 'test')
    os.mkdir(test_dir_name) 
    train_dir_name = os.path.join(root_folder, 'train')
    os.mkdir(train_dir_name)
    
    for id in os.listdir(root_folder):
        
        # skip test and train dirs we just created
        if (id == 'test') or (id == 'train'):
            continue
        
        # choose photos for test and train
        id_dir = os.path.join(root_folder, id)
        images = [f for f in os.listdir(id_dir) if os.path.isfile(os.path.join(id_dir,f))]
        train_choice = random.sample(images, 240)
        test_choice = [f for f in images if f not in train_choice]

        # create identidy dir in test folder and in train folder
        train_id_dir_name = os.path.join(train_dir_name, id)
        os.mkdir(train_id_dir_name)
        test_id_dir_name = os.path.join(test_dir_name, id)
        os.mkdir(test_id_dir_name)

        # move files to train and test folders
        for t in train_choice:
            old_image_name = os.path.join(id_dir, t)
            new_image_name = os.path.join(train_id_dir_name, t)
            os.rename(old_image_name, new_image_name)
            
        for t in test_choice:
            old_image_name = os.path.join(id_dir, t)
            new_image_name = os.path.join(test_id_dir_name, t)
            os.rename(old_image_name, new_image_name)
            
# splits the data set to train and test, across all ids
# takes 0.8 of the identities and move it to test dir
def split_data_set_across_ids(root_folder):
    
    all_id_dirs = [d for d in os.listdir(root_folder)]
    
    # create train and test folder under root folder
    test_dir_name = os.path.join(root_folder, 'mainTest')
    os.mkdir(test_dir_name) 
    train_dir_name = os.path.join(root_folder, 'mainTrain') 
    os.mkdir(train_dir_name) 
    
    ids_num = len(all_id_dirs)
    train_num = round(ids_num*0.8)   
    test_num = ids_num - train_num
    print(f'splits {ids_num} identites to train and test')
    print(f'{train_num} for train and {test_num} for test')
    
    # choose identities for test and train
    train_choice = random.sample(all_id_dirs, train_num)
    test_choice = [d for d in all_id_dirs if d not in train_choice]

    # moves train identities under train dir
    for t in train_choice: 
        old_id_dir = os.path.join(root_folder, t)
        new_id_dir = os.path.join(train_dir_name, t)
        os.rename(old_id_dir, new_id_dir)
        
    # moves test identities under test dir
    for t in test_choice:
        old_id_dir = os.path.join(root_folder, t)
        new_id_dir = os.path.join(test_dir_name, t)
        os.rename(old_id_dir, new_id_dir)


if __name__ == '__main__':
    if (len(sys.argv) < 2 ):
        print ('a directory path is neccesery!')
        exit()
    source_folder = sys.argv[1]
    split_data_set_across_ids(source_folder)
    main_train_path = os.path.join(source_folder, 'mainTrain')
    split_data_set_per_id(main_train_path)

