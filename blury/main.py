from os.path import join, expanduser, dirname
from os import walk, pardir
import sys
import argparse
import time

# Insert project path in variable project_dir and 
# src_dir in sys_path to import our module
project_dir = join(dirname(__file__), pardir)
src_dir = join(project_dir, 'src')
sys.path.append(src_dir)

from lib import Blury, read_config_file

parser = argparse.ArgumentParser(
    description=
    'This is Blury, he will help you to blur persons and plate licence car on your images'
)
parser.add_argument('-i', '--data_in_path',
    help='directory which contains input data.')
parser.add_argument('-o', '--data_out_path',
    help='directory which contains output data.')
parser.add_argument('-t', '--threshold',
    help='threshold of the model, value to define how strict is your model',
    type=float)
parser.add_argument('-f', '--filter', help='Power of filter.', type=int)
parser.add_argument('-c', '--config', 
    help='Give an absolute path to config file for directories in and out',
    default=None)

def main(args):

    t0 = time.time()
    
    # Test config file argument, if not None -> load in and out dir 
    # from config file
    if args.config:
        data_in_path, data_out_path = read_config_file(args.config)
    else:
        data_in_path = expanduser(args.data_in_path)
        data_out_path = expanduser(args.data_out_path)
    nb_filter = args.filter
    threshold = args.threshold
    
    # If there is no directories paths, stop blury
    if not data_in_path or not data_out_path:
        print('Errors in directories configuration!')
        return False
    
    # Init our blury instance to blur plates and persons
    blury = Blury(threshold=threshold, nb_filter=nb_filter)
    
    # Generate all in_dir files
    for root, dirs, img_files in walk(data_in_path):
        for img_file in img_files:
            # Use blury to dectect and blur region of interest on the image
            if blury.load_img(join(root, img_file)) == False: continue
            predictions = blury.predict()
            blury.blur(predictions)
            blury.save(data_out_path, img_file)

    print("This take {0:.3f}min\n".format((time.time() - t0) / 60))

    return True


if __name__ == '__main__':
    sys.exit(main(parser.parse_args()))
