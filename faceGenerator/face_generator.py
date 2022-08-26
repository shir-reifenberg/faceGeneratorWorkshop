import os
import random
import shutil
import numpy as np
from PIL import Image
from natsort import natsorted
import fnmatch
import time
import os.path as path

# global parameters:
fg3sdk_root = r"/home/yandex/CSBW2022/reifenberg/Fg3Sdk3S2FullSrc"
dataset_root = r"/home/yandex/CSBW2022/reifenberg/resultDB/chunk72"
real_people_library = r"/home/yandex/CSBW2022/reifenberg/photoDB/chunk7"
# photo = r"C:\Users\1\Desktop\Fg3Sdk3S2FullSrc\Fg3Sdk3S2FullSrc\data\full\Photos\Andrew\front.jpg"
file_sep = '/'

csamdir = f'{fg3sdk_root}{file_sep}data{file_sep}csam'
animatedir = f'{csamdir}{file_sep}Animate'
bearddir = f'{csamdir}{file_sep}3DPrint{file_sep}Beard'
out_db_root = f'{dataset_root}{file_sep}facegendb{file_sep}identities'

rand_im_pref = 'fgdb'
num_identities = len(os.listdir(real_people_library))
num_images_per_id = 300
base_id_num = 1
# image size
new_image_size = 256

# choose from list random hair style and color
hair_styles = ['Balding',
               'LongWavy',
               'MidlengthStraight',
               'MopTop',
               'Roman',
               'Short',
               'ShortCurls',
               'ShortParted',
               'ShortSlick',
               'ShoulderLength',
               'VeryLong',
               'WavyBob']

hair_colors = [['Balding_Dark', 'Balding_Light', 'Balding_Medium'],
               ['LongWavy_Auburn', 'LongWavy_Black', 'LongWavy_Blonde'],
               ['MidLengthMessy_Black', 'MidLengthMessy_Blonde', 'MidLengthMessy_Brown', 'MidLengthMessy_Red'],
               ['MidlengthStraight_Auburn', 'MidlengthStraight_Black', 'MidlengthStraight_Blonde',
                'MidlengthStraight_Brown', 'MidlengthStraight_Dark Brown'],
               ['MopTop_Black', 'MopTop_Blonde', 'MopTop_Brown', 'MopTop_Red'],
               ['Roman_Auburn', 'Roman_Black', 'Roman_Blonde', 'Roman_Brown'],
               ['Short_Black'],
               ['ShortCurls_Auburn', 'ShortCurls_Black', 'ShortCurls_Brown'],
               ['ShortParted_Auburn', 'ShortParted_Black', 'ShortParted_Brown'],
               ['ShortSlick_Black', 'ShortSlick_Blonde', 'ShortSlick_Brown', 'ShortSlick_Red'],
               ['ShoulderLength_Black', 'ShoulderLength_Blonde', 'ShoulderLength_Brown', 'ShoulderLength_Red'],
               ['VeryLong_Auburn', 'VeryLong_Blonde', 'VeryLong_Brunette', 'VeryLong_Platinum'],
               ['WavyBob_Auburn', 'WavyBob_Black', 'WavyBob_Blonde']]

all_expressions = ['Expression Anger',
                   'Expression Dimple Left',
                   'Expression Dimple Right',
                   'Expression Disgust',
                   'Expression Fear',
                   'Expression Frown',
                   'Expression Kiss',
                   'Expression Sad',
                   'Expression Smile Left',
                   'Expression Smile Right',
                   'Expression SmileClosed',
                   'Expression Sneer']


expressions = ['Expression Anger',
               'Expression Disgust',
               'Expression Fear',
               'Expression Sad',
               'Expression SmileClosed']

exp_stren_range = {"Anger": [0.3, 1.2],
                   "Disgust": [0.3, 1.0],
                   "Fear": [0.3, 1.2],
                   "Sad": [1.0, 1.9],
                   "SmileClosed": [0.6, 1.6],
                   }

# Age
min_age = 20
max_age = 60

# Beard
beard_types = ["b00", "b01", "b02", "b03", "b04", "b05", "b06", "b07", "b08"]
beard_colors = [["Auburn", "Black", "Blonde", "Brown", "Grey"],  # b00
                ["Black", "Blonde", "Brown", "Grey"],  # b01
                ["Auburn", "Black", "Blonde", "Brown"],  # b02
                ["Black", "Blonde", "Brown", "Grey"],  # b03
                ["Auburn", "Black", "Blonde", "Brown", "Grey"],  # b04
                ["Black", "Blonde", "Brown", "Grey"],  # b05
                ["Black", "Blonde", "Brown", "Grey", "Red"],  # b06
                ["Black", "Blonde", "Brown", "Grey"],  # b07
                ["Auburn", "Black", "Blonde", "Brown", "Grey"]]  # b08]

# # Glasses
# glasses_types = ["Glasses_blue",
#                  "Glasses_gray",
#                  "Glasses_stripes",
#                  "Glasses_yellow"]
#
# add_sun_glasses_prob = 0.2
# sun_glasses_types = ["Glasses_black_sun",
#                      "Glasses_blue_sun",
#                      "Glasses_brown_sun",
#                      "Glasses_gray_sun"]

# secondary_hair_prob = 0.05
# secondary_beard_prob = 0.05
# secondary_glasses_prob = 0.05

# pose parameters
tilt_min = 0.0
tilt_max = 0.4
pan_min = 0.0
pan_max = 0.8

# light direction params
light_top_left = [1.0, 1.0, 0.0]
light_bottom_left = [1.0, -1.0, 0.0]
light_top_right = [-1.0, 1.0, 0.0]
light_bottom_right = [-1.0, -1.0, 0.0]

# light_color
allowed_color_variation = 0.5  # 50%

# background color
bg_color = [255, 255, 255]

# default camera position
cam_pos = [0.0, 10.0, -1000.0]

def create_identities():
    cur_dir = os.getcwd()
    photos_list = get_nested_photo_paths(real_people_library)
    num_identities = len(photos_list)

    # go over all identities:
    for i in range(num_identities):
        rand_im_name = make_im_name(rand_im_pref, i + base_id_num)
        if rand_im_name == -1:
            print('error, got rand_im_name {}'.format(rand_im_name))
            exit()

        # generate identities from images (this will create .fg files)
        cmdstr = f'fg3pf photofit {rand_im_name}.fg {photos_list[i]}'
        print(cmdstr)
        print(os.system(cmdstr))

        # make a directory for this identity
        out_dir = f'{out_db_root}{file_sep}{rand_im_name}'
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        # move all generated files to out_dir
        # names of generated files start with i
        tmp_f_pref = make_im_name(rand_im_pref, i)
        gen_files = [f for f in os.listdir(real_people_library) if rand_im_name in f] ###### cur_dir // tmp_f_pref
        print("GEN FILES LEN", (len(gen_files)))
        for g in gen_files:
            # change the file name
            fixed_g = g.replace(tmp_f_pref, rand_im_name)
            print("MOVE FROM", g, " TO", out_dir, fixed_g)
            shutil.move(g, os.path.join(out_dir, fixed_g))

        # prefix for output files
        out_pref = f'{out_dir}{file_sep}{rand_im_name}'
        identity_params_file = set_identity_params(out_dir, rand_im_name)

        # 1. construct head mesh
        cmdstr = f'fg3 cssm {animatedir}{file_sep}Head{file_sep}HeadHires {out_pref}.fg {out_pref}Head.tri'
        print(os.system(cmdstr))

        # 2. construct skin color maps
        cmdstr = f'fg3 cscm {animatedir}{file_sep}Head{file_sep}HeadHires {out_pref}.fg {out_pref}Head.jpg -d 2.0'
        print(os.system(cmdstr))

        # 3. construct mouth (teeth and tongue) meshes
        cmdstr = f'fg3 cssm {animatedir}{file_sep}Head{file_sep}Teeth {out_pref}.fg {out_pref}Teeth.tri'
        print(os.system(cmdstr))

        cmdstr = f'fg3 cssm {animatedir}{file_sep}Head{file_sep}SockTongue {out_pref}.fg {out_pref}SockTongue.tri'
        print(os.system(cmdstr))

        # copy color maps
        # Teeth
        copy_src = f'{animatedir}{file_sep}Head{file_sep}Teeth.jpg'
        copy_dst = f'{out_pref}Teeth.jpg'
        shutil.copy(copy_src, copy_dst)
        # Tongue
        copy_src = f'{animatedir}{file_sep}Head{file_sep}SockTongue.jpg'
        copy_dst = f'{out_pref}SockTongue.jpg'
        shutil.copy(copy_src, copy_dst)

        # 4. select hair style and construct it, copy hair color
        hs_index = np.random.randint(len(hair_styles))
        hs = hair_styles[hs_index]
        hcs = hair_colors[hs_index]
        hc = hcs[np.random.randint(len(hcs))]
        cmdstr = f'fg3 cssm {animatedir}{file_sep}Hair{file_sep}{hs} {out_pref}.fg {out_pref}Hair.tri'
        print(cmdstr)
        print(os.system(cmdstr))

        # Copy hair
        copy_src = f'{animatedir}{file_sep}Hair{file_sep}{hc}.tga'
        copy_dst = f'{out_pref}Hair.tga'
        shutil.copy(copy_src, copy_dst)

        # # Select secondary hair:
        # hs_index = np.random.randint(len(hair_styles))
        # hs = hair_styles[hs_index]
        # hcs = hair_colors[hs_index]
        # hc = hcs[np.random.randint(len(hcs))]
        # cmdstr = f'fg3 cssm {animatedir}{file_sep}Hair{file_sep}{hs} {out_pref}.fg {out_pref}Hair_2.tri'
        # print(os.system(cmdstr))

        # # Copy hair
        # copy_src = f'{animatedir}{file_sep}Hair{file_sep}{hc}.tga'
        # copy_dst = f'{out_pref}Hair_2.tga'
        # shutil.copy(copy_src, copy_dst)

        # 5. select beard/mustache
        beard_type, beard_color = select_beard()
        cmdstr = f'fg3 cssm {bearddir}{file_sep}{beard_type} {out_pref}.fg {out_pref}Beard.tri'
        print(cmdstr)
        print(os.system(cmdstr))

        copy_src = f'{bearddir}{file_sep}{beard_color}.jpg'
        copy_dst = f'{out_pref}Beard.jpg'
        shutil.copy(copy_src, copy_dst)

        # # Secondary beard/mustache
        # beard_type, beard_color = select_beard()
        # cmdstr = f'fg3 cssm {bearddir}{file_sep}{beard_type} {out_pref}.fg {out_pref}Beard_2.tri'
        # print(cmdstr)
        # print(os.system(cmdstr))
        #
        # copy_src = f'{bearddir}{file_sep}{beard_color}.jpg'
        # copy_dst = f'{out_pref}Beard_2.jpg'
        # shutil.copy(copy_src, copy_dst)

        # # 6. select glasses
        # glasses_type = random.choice(glasses_types)
        # cmdstr = f'fg3 cssm {animatedir}{file_sep}Accessories{file_sep}Glasses {out_pref}.fg {out_pref}Glasses.tri'
        # print(cmdstr)
        # print(os.system(cmdstr))
        #
        # copy_src = f'{animatedir}{file_sep}Accessories{file_sep}{glasses_type}.tga'
        # copy_dst = f'{out_pref}Glasses.tga'
        # shutil.copy(copy_src, copy_dst)

        # # secondary glasses
        # glasses_type = random.choice(glasses_types)
        # cmdstr = f'fg3 cssm {animatedir}{file_sep}Accessories{file_sep}Glasses {out_pref}.fg {out_pref}Glasses_2.tri'
        # print(cmdstr)
        # print(os.system(cmdstr))
        #
        # copy_src = f'{animatedir}{file_sep}Accessories{file_sep}{glasses_type}.tga'
        # copy_dst = f'{out_pref}Glasses_2.tga'
        # shutil.copy(copy_src, copy_dst)

        # 6. render:
        # setup render xml file
        cmdstr = f'fgbl render setup {out_pref}Render.xml {out_pref}Head.tri {out_pref}Head.jpg {out_pref}SockTongue.tri ' \
                 f'{out_pref}SockTongue.jpg {out_pref}Teeth.tri {out_pref}Teeth.jpg  {out_pref}Hair.tri {out_pref}Hair.tga ' \
                 # f'{out_pref}Beard.tri {out_pref}Beard.jpg' # {out_pref}Glasses.tri {out_pref}Glasses.tga'

        print(cmdstr)
        print(os.system(cmdstr))
        # actually render
        cmdstr = f'fgbl render run {out_pref}Render.xml {out_pref}Base.jpg'
        print(cmdstr)
        print(os.system(cmdstr))
        # pause before moving files
        time.sleep(1)

        # move output files into identity dir
        gen_files = [f for f in os.listdir(cur_dir) if rand_im_name in f]
        for g in gen_files:
            shutil.move(g, os.path.join(out_dir, g))


def create_random_images():
    # go over all identities
    ids = os.listdir(out_db_root)
    # for each identity that was created
    for id_index in range(len(ids)):
        id_dir = ids[id_index]
        cur_dir = os.path.join(out_db_root, id_dir)
        print(cur_dir)
        # for each identity create a directory into which we copy all final rendered images
        print(f'Trying to create image num {id_index}')
        images_dir = os.path.join(cur_dir, 'images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        # general prefix for image names
        out_pref = f'{cur_dir}{file_sep}{id_dir}'
        print(f'Out pref is this dir {out_pref}')
        # create a txt file, and write xml file names into it
        xml_list_fname = f'{out_pref}_xml_list.txt'
        print("Before open")
        with open(xml_list_fname, 'w') as xml_list:
            print("Opened XML File")
            for i in range(num_images_per_id):

                # Age: set random age
                age_set = int(np.random.uniform(min_age, max_age))
                fg_fname = f'{out_pref}.fg'
                out_pref_i = f'{cur_dir}{file_sep}{id_dir}_{i}'
                cmdstr = f'fg3 controls demographic edit {fg_fname} age {age_set} {out_pref_i}.fg'
                print(cmdstr)
                print(os.system(cmdstr))

                # reconstruct meshes
                # 1. construct head mesh
                cmdstr = f'fg3 cssm {animatedir}{file_sep}Head{file_sep}HeadHires {out_pref_i}.fg {out_pref_i}Head.tri'
                print(cmdstr)
                print(os.system(cmdstr))

                # 2. construct skin color maps
                cmdstr = f'fg3 cscm {animatedir}{file_sep}Head{file_sep}HeadHires {out_pref_i}.fg {out_pref_i}Head.jpg'
                print(cmdstr)
                print(os.system(cmdstr))

                # 3. construct mouth (teeth and tongue) meshes
                cmdstr = f'fg3 cssm {animatedir}{file_sep}Head{file_sep}Teeth {out_pref_i}.fg {out_pref_i}Teeth.tri'
                print(cmdstr)
                print(os.system(cmdstr))

                cmdstr = f'fg3 cssm {animatedir}{file_sep}Head{file_sep}SockTongue {out_pref_i}.fg {out_pref_i}SockTongue.tri'
                print(cmdstr)
                print(os.system(cmdstr))

                # Expression:
                expr = random.choice(expressions)
                # create a prefix by removing the word "Expression"
                ex = expr.split()
                expr_pref = ''.join(ex[1:])
                # get expression strength
                min_expression_strength = exp_stren_range[expr_pref][0]
                max_expression_strength = exp_stren_range[expr_pref][1]
                expr_strength = random.uniform(min_expression_strength, max_expression_strength)
                cmdstr = f'fgbl morph anim {expr_pref} {out_pref_i}Head.tri {out_pref_i}Teeth.tri {out_pref_i}SockTongue.tri "{expr}" {str(expr_strength)}'
                print(cmdstr)
                print(os.system(cmdstr))

                # select view params
                # tilt - first in the positive range
                tilt_val = random.uniform(tilt_min, tilt_max)
                # randomly decide whether it's up or down
                tilt_sign = random.choice([-1, 1])
                tilt_val = tilt_val * tilt_sign
                # pan value
                pan_val = random.uniform(pan_min, pan_max)

                # select illumination params
                new_light_direction_vals = [random.uniform(0.0, 1.0), random.uniform(0.0, 1.0),
                                            random.uniform(0.0, 1.0)]
                new_light_color_vals = get_random_light_color()

                new_bg_color_vals = bg_color

                # make a descriptive name
                out_xml_fname = f'{images_dir}{file_sep}{id_dir}_{i}_age_{age_set}_{expr_pref}_{expr_strength:.2f}_tilt_{tilt_val:.2f}_pan_{pan_val:.2f}' \
                                f'_lightdir_{new_light_direction_vals[0]:.2f}_{new_light_direction_vals[1]:.2f}_{new_light_direction_vals[2]:.2f}' \
                                f'_lightcol_{new_light_color_vals[0]:.2f}_{new_light_color_vals[1]:.2f}_{new_light_color_vals[2]:.2f}.xml'

                cmdstr = f'fgbl render setup {out_xml_fname} {out_pref_i}Teeth{expr_pref}.tri {out_pref}Teeth.jpg {out_pref_i}SockTongue{expr_pref}.tri {out_pref}SockTongue.jpg ' \
                         f'{out_pref_i}Head{expr_pref}.tri {out_pref_i}Head.jpg'

                use_secondary_hair = False
                if use_secondary_hair:
                    cmdstr = cmdstr + f' {out_pref}Hair_2.tri {out_pref}Hair_2.tga'
                else:
                    cmdstr = cmdstr + f' {out_pref}Hair.tri {out_pref}Hair.tga'

                # add_beard, add_glasses = do_add_beard_glasses(cur_dir, id_dir)
                add_beard = do_add_beard_glasses(cur_dir, id_dir)
                if add_beard:
                    use_secondary_beard = False
                    if use_secondary_beard:
                        cmdstr = cmdstr + f' {out_pref}Beard_2.tri {out_pref}Beard_2.jpg'
                    else:
                        cmdstr = cmdstr + f' {out_pref}Beard.tri {out_pref}Beard.jpg'
                # if add_glasses:
                #     use_secondary_glasses = False
                #     if use_secondary_glasses:
                #         cmdstr = cmdstr + f' {out_pref}Glasses_2.tri {out_pref}Glasses_2.tga'
                #     else:
                #         cmdstr = cmdstr + f' {out_pref}Glasses.tri {out_pref}Glasses.tga'
                # else:  # add sunglasses if no glasses are added
                #     add_sunglasses = (np.random.choice([0, 1], p=(1 - add_sun_glasses_prob, add_sun_glasses_prob)) == 1)
                #     if add_sunglasses:
                #         sg_type = random.choice(sun_glasses_types)
                #         cmdstr = cmdstr + f' {out_pref}Glasses.tri {animatedir}{file_sep}Accessories{file_sep}{sg_type}.tga'


                print(cmdstr)
                print(os.system(cmdstr))

                # now take the out_xml_fname and modify it to get random pose and illumination
                # create face up and down or left-right
                with open(out_xml_fname, 'r') as xfile:
                    lines = xfile.readlines()
                    new_fname = f'{out_pref}_tmp.xml'
                    new_full_fname = os.path.join(cur_dir, new_fname)
                    with open(new_full_fname, 'w') as out_xml:
                        line_ind = 0
                        while line_ind < len(lines):
                            line = lines[line_ind]
                            # change tilt and pan
                            if line.find('tilt') != -1:
                                new_line = '<tilt>{}</tilt>\n'.format(tilt_val)
                                out_xml.write(new_line)
                            elif line.find('pan') != -1:
                                new_line = '<pan>{}</pan>\n'.format(pan_val)
                                out_xml.write(new_line)
                            elif line.find('imagePixelSize') != -1:
                                line_ind = set_new_image_size(line_ind, out_xml, lines)
                            elif line.find('colour') != -1:
                                line_ind = set_light_color(out_xml, lines, line_ind, new_light_color_vals)
                            elif line.find('direction') != -1:
                                line_ind = set_light_direction(out_xml, lines, line_ind, new_light_direction_vals)
                            elif line.find('backgroundColor') != -1:
                                line_ind = set_bg_color(out_xml, lines, line_ind, new_bg_color_vals)
                            elif line.find('<trans>') != -1:
                                line_ind = set_camera_position(out_xml, lines, line_ind, cam_pos)
                            else:
                                out_xml.write(line)
                            line_ind = line_ind + 1
                # overwrite the tmp file
                shutil.move(new_full_fname, out_xml_fname)
                # write xml file name to the txt file
                xml_list.write(out_xml_fname + '\n')

        # finished creating xml files, render them
        cmdstr = f'fgbl render batch {xml_list_fname} jpg'
        print(cmdstr)
        print(os.system(cmdstr))


# Gets the path that contains all folders with the photos inside
# Returns a list with all photo paths
def get_nested_photo_paths(root_path):
    if not path.isdir(root_path):
        raise Exception(f'The Path:{root_path} is not a directory')
    all_photo_dirs = [d for d in os.listdir(root_path) if path.isdir(path.join(root_path, d))]
    print(all_photo_dirs)
    all_photo_paths = []
    for dir in all_photo_dirs:
        current_photo_dir = path.join(root_path, dir)
        current_photo_name = path.join(current_photo_dir, dir + '.jpg')

        os.chdir(current_photo_dir)
        if not path.exists(current_photo_name):
            raise Exception(f'The Photo:{current_photo_name} does not exists')
        all_photo_paths.append(current_photo_name)
        os.chdir(root_path)
    return all_photo_paths

def make_im_name(pref, ind):
    if ind < 10:
        im_name = pref + '000' + str(ind)
    elif ind < 100:
        im_name = pref + '00' + str(ind)
    elif ind < 1000:
        im_name = pref + '0' + str(ind)
    elif ind < 10000:
        im_name = pref + str(ind)
    else:
        im_name = -1

    return im_name


def set_identity_params(id_dir, id_name):
    # make a txt file with identity parameters
    # 50% of the identities will have 80% of their images with a beard,
    # the rest will have 20%
    beard_prob = np.random.choice([0.2, 0.8])
    # 50% of the identities will have 80% of their images with a glasses,
    # the rest will have 20%
    glasses_prob = np.random.choice([0.2, 0.8])
    params_fname = f'{id_name}_params.txt'
    with open(os.path.join(id_dir, params_fname), 'w') as pfile:
        pfile.write(f'beard_prob: {beard_prob}\n')
        pfile.write(f'glasses_prob: {glasses_prob}\n')

    return params_fname


def select_beard():
    # select beard type and color
    beard_type_index = np.random.randint(len(beard_types))
    beard_type = beard_types[beard_type_index]
    bcs = beard_colors[beard_type_index]
    beard_color = bcs[np.random.randint(len(bcs))]
    beard_color = f'{beard_type}_{beard_color}'
    return beard_type, beard_color


def do_add_beard_glasses(cur_dir, id_name):
    # read identity params file
    params_fname = f'{id_name}_params.txt'
    with open(os.path.join(cur_dir, params_fname), 'r') as pfile:
        lines = pfile.readlines()
        for line in lines:
            line = line.rstrip('\n')
            line = line.split(':')
            if line[0] == 'beard_prob':
                beard_prob = float(line[1])
            if line[0] == 'glasses_prob':
                glasses_prob = float(line[1])

    add_beard = (np.random.choice([0, 1], p=[1 - beard_prob, beard_prob]) == 1)
    # add_glasses = (np.random.choice([0, 1], p=[1 - glasses_prob, glasses_prob]) == 1)

    return add_beard#, add_glasses


def do_add_glasses():
    return np.random.choice([0, 1], p=[1.0 - add_glasses_prob, add_glasses_prob]) == 1


def is_identity_with(id_dir, element):
    return len([f for f in os.listdir(id_dir) if element in f]) > 0


def set_light_direction(out_xml, lines, line_ind, new_val):
    # the 'direction' tag looks like this:
    # <direction>
    # <m>
    # <elems>
    # <count>3</count>
    # <item>1.000000000e+00</item>
    # <item>-1.000000000e+00</item>
    # <item>0.000000000e+00</item>
    # </elems>
    # </m>
    # </direction>
    out_xml.write(lines[line_ind])  # <direction>
    out_xml.write(lines[line_ind + 1])  # <m>
    out_xml.write(lines[line_ind + 2])  # <elems>
    out_xml.write(lines[line_ind + 3])  # <count>3</count>
    # now the 3 direction params:
    new_line = '<item>{}</item>\n'.format(new_val[0])
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[1])
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[2])
    out_xml.write(new_line)
    out_xml.write(lines[line_ind + 7])  # </elems>
    out_xml.write(lines[line_ind + 8])  # </m>
    out_xml.write(lines[line_ind + 9])  # </directions>
    line_ind = line_ind + 9

    return line_ind


def get_random_light_color():
    # select random value for red
    # then the other values can't be too different
    red = random.uniform(0.0, 1.0)
    max_color = min(1.0, red * (1.0 + allowed_color_variation))
    min_color = max(0.0, red * (1.0 - allowed_color_variation))
    green = random.uniform(min_color, max_color)
    blue = random.uniform(min_color, max_color)
    return [red, green, blue]


def set_light_color(out_xml, lines, line_ind, new_val):
    out_xml.write(lines[line_ind])  # <colour>
    out_xml.write(lines[line_ind + 1])  # <m>
    out_xml.write(lines[line_ind + 2])  # <elems>
    out_xml.write(lines[line_ind + 3])  # <count>3</count>
    # now the 3 color params:
    new_line = '<item>{}</item>\n'.format(new_val[0])  # 4
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[1])  # 5
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[2])  # 6
    out_xml.write(new_line)
    out_xml.write(lines[line_ind + 7])  # </elems>
    out_xml.write(lines[line_ind + 8])  # </m>
    out_xml.write(lines[line_ind + 9])  # </colour>
    line_ind = line_ind + 9

    return line_ind


def set_bg_color(out_xml, lines, line_ind, new_val):
    out_xml.write(lines[line_ind])  # <backgroundColor class_id="19" tracking_level="0" version="0">
    out_xml.write(lines[line_ind + 1])  # <m_c class_id="20" tracking_level="0" version="0">
    out_xml.write(lines[line_ind + 2])  # <elems>
    out_xml.write(lines[line_ind + 3])  # <count>4</count>
    # now the 3 background color params:
    new_line = '<item>{}</item>\n'.format(new_val[0])  # 4
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[1])  # 5
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[2])  # 6
    out_xml.write(new_line)
    out_xml.write(lines[line_ind + 7])  # <item>0.000000000e+00</item>
    out_xml.write(lines[line_ind + 8])  # </elems>
    out_xml.write(lines[line_ind + 9])  # </m_c>
    out_xml.write(lines[line_ind + 10])  # </backgroundColor>
    line_ind = line_ind + 10

    return line_ind


def set_new_image_size(line_ind, out_xml, lines):
    # the imagePixelSize tag looks like this:
    # <imagePixelSize class_id = "10" tracking_level = "0" version = "0" >
    # <m class_id = "11" tracking_level = "0" version = "0" >
    # <elems>
    # <count> 2 </count>
    # <item> 512 </item>
    # <item> 512 </item>
    # </elems>
    # </m>
    # </imagePixelSize>
    out_xml.write(lines[line_ind])  # <imagePixelSize class_id = "10" tracking_level = "0" version = "0" >
    out_xml.write(lines[line_ind + 1])  # <m class_id = "11" tracking_level = "0" version = "0" >
    out_xml.write(lines[line_ind + 2])  # <elems>
    out_xml.write(lines[line_ind + 3])  # <count> 2 </count>
    # now image size
    new_line = '<item>{}</item>\n'.format(str(new_image_size))
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(str(new_image_size))
    out_xml.write(new_line)
    out_xml.write(lines[line_ind + 6])  # </elems>
    out_xml.write(lines[line_ind + 7])  # </m>
    out_xml.write(lines[line_ind + 8])  # </imagePixelSize>
    line_ind = line_ind + 8
    return line_ind


def set_camera_position(out_xml, lines, line_ind, new_val):
    out_xml.write(lines[line_ind])  # <trans>
    out_xml.write(lines[line_ind + 1])  # <m>
    out_xml.write(lines[line_ind + 2])  # <elems>
    out_xml.write(lines[line_ind + 3])  # <count>3</count>
    # now the 3 camera position params:
    new_line = '<item>{}</item>\n'.format(new_val[0])  # 4
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[1])  # 5
    out_xml.write(new_line)
    new_line = '<item>{}</item>\n'.format(new_val[2])  # 6
    out_xml.write(new_line)
    out_xml.write(lines[line_ind + 7])  # </elems>
    out_xml.write(lines[line_ind + 8])  # </m>
    out_xml.write(lines[line_ind + 9])  # </trans>
    line_ind = line_ind + 9

    return line_ind


def create_systematic_images():
    # go over identities
    ids = os.listdir(out_db_root)
    for id_dir in ids:
        cur_dir = os.path.join(out_db_root, id_dir)
        print(cur_dir)
        # for each identity create a directory into which we copy all final rendered images
        images_dir = os.path.join(cur_dir, 'images')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        out_pref = f'{cur_dir}{file_sep}{id_dir}'
        # for each identity create all expressions with maximum strength
        add_all_expressions(out_pref, 0, set_max_strength=True, render=False)
        # now go over all *Render*xml files (one for each expression) and edit them:
        render_xmls = [f for f in os.listdir(cur_dir) if 'Render' in f and f.endswith('.xml')]
        print('after add_expressions found {} xml files'.format(str(len(render_xmls))))
        # first we add tilt poses
        for xmlfile in render_xmls:
            # test tilt range
            render_pose(cur_dir, xmlfile, 'tiltRadians', -0.3, images_dir)
            render_pose(cur_dir, xmlfile, 'tiltRadians', -0.4, images_dir)
            render_pose(cur_dir, xmlfile, 'tiltRadians', -0.5, images_dir)
            render_pose(cur_dir, xmlfile, 'tiltRadians', -0.6, images_dir)
            render_pose(cur_dir, xmlfile, 'tiltRadians', 0.3, images_dir)
            render_pose(cur_dir, xmlfile, 'tiltRadians', 0.4, images_dir)
            render_pose(cur_dir, xmlfile, 'tiltRadians', 0.5, images_dir)
            render_pose(cur_dir, xmlfile, 'tiltRadians', 0.6, images_dir)
        # now go over all resulting xmls, and add pan,
        # which should give us 6 more images, a total of 9 per expression
        render_xmls = [f for f in os.listdir(cur_dir) if 'Render' in f and f.endswith('.xml')]
        print('after adding tilt found {} xml files'.format(str(len(render_xmls))))
        for xmlfile in render_xmls:
            #            render_pose(cur_dir, xmlfile, 'panRadians', face_quarter_left_val,images_dir)
            render_pose(cur_dir, xmlfile, 'panRadians', 0.5, images_dir)
            render_pose(cur_dir, xmlfile, 'panRadians', 0.6, images_dir)
            render_pose(cur_dir, xmlfile, 'panRadians', 0.7, images_dir)
            render_pose(cur_dir, xmlfile, 'panRadians', 0.8, images_dir)
            render_pose(cur_dir, xmlfile, 'panRadians', 0.9, images_dir)
        # now go over all resulting xmls, and add lighting
        # which should give us 4 more images, a total of 9 per expression
        # render_xmls = [f for f in os.listdir(cur_dir) if 'Render' in f and f.endswith('.xml')]
        # print('after adding pan found {} xml files'.format(str(len(render_xmls))))
        # for xmlfile in render_xmls:
        #     render_light(cur_dir, xmlfile, 'light_top_left', light_top_left,images_dir)
        #     render_light(cur_dir, xmlfile, 'light_bottom_left', light_bottom_left,images_dir)
        #     render_light(cur_dir, xmlfile, 'light_top_right', light_top_right,images_dir)
        #     render_light(cur_dir, xmlfile, 'light_bottom_right', light_bottom_right,images_dir)

        render_xmls = [f for f in os.listdir(cur_dir) if 'Render' in f and f.endswith('.xml')]
        print('after adding light found {} xml files'.format(str(len(render_xmls))))


# take one face and put all possible hairs on it
def make_all_hairs(out_pref):
    for i in range(len(hair_styles)):
        hs = hair_styles[i]
        hcs = hair_colors[i]
        for j in range(len(hcs)):
            hc = hcs[j]
            cmdstr = f'fg3 construct {animatedir}{file_sep}Hair{file_sep}{hs} {out_pref}.fg {out_pref}_{hc}Hair'
            print(cmdstr)
            print(os.system(cmdstr))
            cmdstr = f'copy {animatedir}{file_sep}Hair{file_sep}{hc}.tga {out_pref}_{hc}Hair.tga'
            print(cmdstr)
            print(os.system(cmdstr))

            # 4. render
            cmdstr = 'fg3 render {}_{}Render {}Teeth.tri {}SockTongue.tri {}Head.tri {}Head.bmp {}_{}Hair.tri {}_{}Hair.tga'. \
                format(out_pref, hc, out_pref, out_pref, out_pref, out_pref, out_pref, hc, out_pref, hc)
            print(cmdstr)
            print(os.system(cmdstr))


def render_pose(cur_dir, xmlfile, tag, new_val, images_dir):
    print(f'inside render_pose, {cur_dir}{file_sep}{xmlfile},{tag},{new_val}')
    # get name without extension
    file_name = os.path.splitext(xmlfile)[0]
    # create face up and down or left-right
    with open(os.path.join(cur_dir, xmlfile), 'r') as xfile:
        lines = xfile.readlines()
        new_fname = '{}_{}_{}.{}'.format(file_name, tag, str(new_val), 'xml')
        new_full_fname = os.path.join(cur_dir, new_fname)
        with open(new_full_fname, 'w') as out_xml:
            line_ind = 0
            while line_ind < len(lines):
                line = lines[line_ind]
                # search for line containing tag
                if line.find(tag) != -1:
                    new_line = '<{}>{}</{}>\n'.format(tag, str(new_val), tag)
                    out_xml.write(new_line)
                elif line.find('imagePixelSize') != -1:
                    line_ind = set_new_image_size(line_ind, out_xml, lines)
                elif line.find('outputFile') != -1:
                    # name of output image
                    out_im_fname = '{}_{}_{}.{}'.format(file_name, tag, str(new_val), 'jpg')
                    out_im_full_fname = os.path.join(images_dir, out_im_fname)
                    new_line = '<outputFile>{}</outputFile>\n'.format(out_im_full_fname)
                    out_xml.write(new_line)
                else:
                    out_xml.write(line)
                line_ind = line_ind + 1

    # render:
    cmdstr = 'fg3 render {}'.format(os.path.splitext(new_full_fname)[0])
    print(cmdstr)
    print(os.system(cmdstr))


def render_light(cur_dir, xmlfile, light_dir, new_val, images_dir):
    print(f'inside render_light, {cur_dir}{file_sep}{xmlfile},{light_dir},{new_val}')
    # get name without extension
    file_name = os.path.splitext(xmlfile)[0]
    # create face up and down
    with open(os.path.join(cur_dir, xmlfile), 'r') as xfile:
        lines = xfile.readlines()
        new_fname = '{}_{}.{}'.format(file_name, light_dir, 'xml')
        new_full_fname = os.path.join(cur_dir, new_fname)
        with open(new_full_fname, 'w') as out_xml:
            line_ind = 0
            while line_ind < len(lines):
                line = lines[line_ind]
                # search for line containing tag "direction"
                if line.find('direction') != -1:
                    line_ind = set_light_direction(out_xml, lines, line_ind, new_val)
                elif line.find('imagePixelSize') != -1:
                    line_ind = set_new_image_size(line_ind, out_xml, lines)
                elif line.find('outputFile') != -1:
                    # name of output image
                    out_im_fname = '{}_{}.{}'.format(file_name, light_dir, 'jpg')
                    out_im_full_fname = os.path.join(images_dir, out_im_fname)
                    new_line = '<outputFile>{}</outputFile>\n'.format(out_im_full_fname)
                    out_xml.write(new_line)
                else:
                    out_xml.write(line)
                line_ind = line_ind + 1

    # render:
    cmdstr = 'fg3 render {}'.format(os.path.splitext(new_full_fname)[0])
    print(cmdstr)
    print(os.system(cmdstr))


def add_all_expressions(out_pref, strength, set_max_strength=False, render=False):
    # add all possible expressions
    for expr in expressions:
        # create a prefix by removing the word "Expression"
        ex = expr.split()
        pref = ''.join(ex[1:])

        if set_max_strength == True:
            # set max strentgth for this expression
            strength = exp_stren_range[pref][1]
        else:
            strength = strength

        cmdstr = 'fg3 morph anim {} {}Head.tri {}Teeth.tri {}SockTongue.tri "{}" {}'. \
            format(pref, out_pref, out_pref, out_pref, expr, str(strength))
        print(cmdstr)
        print(os.system(cmdstr))

        cmdstr = f'fg3 render {out_pref}_{pref}_{strength:.2f}_Render {out_pref}Teeth{pref}.tri {out_pref}Teeth.jpg {out_pref}SockTongue{pref}.tri ' \
                 f'{out_pref}SockTongue.jpg {out_pref}Head{pref}.tri {out_pref}Head.bmp {out_pref}Hair.tri {out_pref}Hair.tga'
        print(cmdstr)
        print(os.system(cmdstr))

        if render == True:
            # modify xml file
            cmdstr = f'fg3 render {out_pref}_{pref}_{strength:.2f}_Render'
            print(cmdstr)
            print(os.system(cmdstr))


def test_expression_strengths():
    ids = os.listdir(out_db_root)
    for id_dir in ids:
        cur_dir = os.path.join(out_db_root, id_dir)
        print(cur_dir)
        # for each identity create a directory into which we copy all final rendered images
        images_dir = os.path.join(cur_dir, 'expressions')
        if not os.path.exists(images_dir):
            os.makedirs(images_dir)

        out_pref = f'{cur_dir}{file_sep}{id_dir}'
        # for each identity create expressions in varying strengths
        min_expression_strength = 0.3
        max_expression_strength = 1.9
        for stren in np.arange(start=min_expression_strength, stop=max_expression_strength, step=0.1):
            add_all_expressions(out_pref, stren, set_max_strength=False, render=True)


def resize_images(dir_name, ext, pattern=''):
    if pattern != '':
        im_names = [f for f in os.listdir(dir_name) if pattern in f and f.endswith(ext)]
    else:
        im_names = [f for f in os.listdir(dir_name) if f.endswith(ext)]

    for im_name in im_names:
        im = Image.open(os.path.join(dir_name, im_name), 'r')
        im = im.convert('RGB')
        im = im.resize((new_image_size, new_image_size))
        file_name = os.path.splitext(im_name)[0]
        file_name = file_name + '.jpg'
        im.save(os.path.join(dir_name, file_name))


def rename_dirs():
    root_dir = '/home/n/d_datasets/identities'
    trgt_dir = '/home/n/d_datasets/facegendb/identities'
    ids = os.listdir(root_dir)
    base_target_name = 832
    for id_index in range(len(ids)):
        dir_name = ids[id_index]
        trgt_name = f'fgdb0{base_target_name + id_index}'
        shutil.move(os.path.join(root_dir, dir_name), os.path.join(trgt_dir, trgt_name))


def move_images():
    root_dir = '/home/n/d_datasets/facegendb/train'
    extra_dir = '/home/n/d_datasets/facegendb/train_extra'
    ids = natsorted(os.listdir(root_dir))
    for id_dir in ids:
        im_dir = os.path.join(root_dir, id_dir)
        imgs = natsorted(fnmatch.filter(os.listdir(im_dir), '*.jpg'))
        if len(imgs) < 300:
            print(f'identity {id_dir} has {len(imgs)} images')
            continue
        ex_dir = os.path.join(extra_dir, id_dir)
        if not os.path.exists(ex_dir):
            os.makedirs(ex_dir)
        for i in range(300, len(imgs)):
            shutil.move(os.path.join(im_dir, imgs[i]), os.path.join(ex_dir, imgs[i]))


def count_images():
    root_dir = '/home/n/d_datasets/facegendb_3/align'
    num_images = 0
    for i in range(1000):
        id_dir = make_im_name(rand_im_pref, i)
        dir_name = os.path.join(root_dir, id_dir)
        if os.path.exists(dir_name):
            #            im_dir = os.path.join(root_dir,dir_name,'images')
            #            if os.path.exists(im_dir):
            #                imgs = natsorted(fnmatch.filter(os.listdir(im_dir),'*.jpg'))
            imgs = natsorted(fnmatch.filter(os.listdir(dir_name), '*.jpg'))
            num_images += len(imgs)
            if len(imgs) < 300:
                print(f'identity {id_dir} has {len(imgs)} images')
            # else:
            #     print(f'{id_dir} has no images')
        else:
            print(f'{id_dir} missing')

    print(f'total num images: {num_images}')


def move_files_to_dir():
    work_dir = os.getcwd()
    ids = os.listdir(out_db_root)
    for id_index in range(435, len(ids)):
        id_dir = ids[id_index]
        cur_dir = os.path.join(out_db_root, id_dir)
        print(cur_dir)

        gen_files = [f for f in os.listdir(work_dir) if id_dir in f]
        for g in gen_files:
            shutil.move(g, os.path.join(cur_dir, g))


def move_images():
    ids = os.listdir(out_db_root)
    dest_root = 'E:\\datasets\\facegendb_2\\identities'
    for id_index in range(848, len(ids)):
        id_dir = ids[id_index]
        cur_dir = os.path.join(out_db_root, id_dir)
        print(cur_dir)
        images_dir = os.path.join(cur_dir, 'images')
        os.makedirs(os.path.join(dest_root, id_dir), exist_ok=True)
        os.makedirs(os.path.join(dest_root, id_dir, 'images'), exist_ok=True)
        imgs = fnmatch.filter(os.listdir(images_dir), '*.jpg')
        for img in imgs:
            shutil.move(os.path.join(images_dir, img), os.path.join(dest_root, id_dir, 'images', img))


def rename_files():
    id_dir = 'fgdb0433'
    rep_id = 'fgdb1003'
    dir_name = f'E:\\datasets\\facegendb_2\\identities\\{id_dir}'
    files = [f for f in os.listdir(dir_name) if rep_id in f]
    for f in files:
        new_name = f.replace(rep_id, id_dir)
        shutil.move(os.path.join(dir_name, f), os.path.join(dir_name, new_name))
    imgdir = os.path.join(dir_name, 'images')
    files = [f for f in os.listdir(imgdir) if rep_id in f]
    for f in files:
        new_name = f.replace(rep_id, id_dir)
        shutil.move(os.path.join(imgdir, f), os.path.join(imgdir, new_name))


def clean_db():
    ids = os.listdir(out_db_root)
    for id_index in range(len(ids)):
        # for id_index in range():
        id_dir = ids[id_index]
        cur_dir = os.path.join(out_db_root, id_dir)
        print(cur_dir)
        files = [f for f in os.listdir(cur_dir) if id_dir in f]
        for f in files:
            os.remove(os.path.join(cur_dir, f))


if __name__ == '__main__':
    create_identities()
    create_random_images()
# make_all_hairs('D:\\datasets\\facegendb\\fgdb0000\\fgdb0000')
# add_expressions('D:\\datasets\\facegendb\\fgdb0001\\fgdb0001')
#   create_systematic_images()
#    test_expression_strengths()
#    resize_images('D:\\datasets\\facegendb\\identities\\fgdb0001\\expressions','png','Render')
#    rename_dirs()
#    move_images()
#    count_images()
#    move_files_to_dir()
#    move_images()
#    rename_files()
#    clean_db()
# fgdb0213 missing
# fgdb0431 missing
# fgdb0432 missing
# fgdb0433 missing
# identity fgdb0842 has 338 images
