import json
import sys
import argparse
import matplotlib.pyplot as plt
from matplotlib import rcParams
from skimage import io


def read_albums_from_json(library):
    albums = []
    al_covers = []
    al_years = []

    for name, info in library.items():
        if name not in albums:
            albums.append(name)
            al_covers.append(info[1])
            al_years.append(int(info[0]))

    return al_covers, al_years


def generate_and_save_histogram(al_covers, al_years):
    """Matplotlib/skimage magic to generate a histogram of album art.

    Iterates through the years generated, downloads the image from spotify's cached images,
    and plots it on a matplotlib graph.

    Arguments:
        al_covers {list} -- listof album art string URLs
        al_years {list} -- listof album year ints
    """
    low_year = nearest_five(min(al_years))
    high_year = max(al_years) + 1 # add 1 to get highest year albums

    max_num = 0
    for curr_year in range(low_year, high_year):
        num = 0
        index = 0
        for year in al_years:
            if int(year) == curr_year:
                image = io.imread(al_covers[index])
                plt.imshow(image, extent=[
                           int(year) * 10, int(year) * 10 + 10, int(num) * 10, int(num) * 10 + 10])
            if int(year) == curr_year:
                num += 1
                if num > max_num:
                    max_num = num
            index += 1

    plt.tight_layout()
    plt.xlim([low_year * 10, high_year * 10])
    plt.ylim([0, max_num * 10])
    plt.xticks(range(low_year * 10, high_year * 10, 100),
               range(low_year, high_year, 10))
    plt.yticks(range(0, max_num * 10 + 1, 50), range(0, max_num + 1, 5))
    plt.title("Music Library in Album Covers")
    plt.xlabel("Year")
    plt.ylabel("Number of Albums")
    plt.savefig("library.png", transparent=True, dpi=1372)


def nearest_five(num):
    """Gets the nearest multiple of 5 of a number, rounding down.

    Arguments:
        num {int} -- the number to find the nearest multiple of 5
    """
    return num // 5 * 5


def main(args):
    # update matplotlib rc to have correct dimensions
    rcParams.update({'figure.autolayout': True})
    plt.style.use('dark_background')

    parser = argparse.ArgumentParser(
        description='Reads a JSON file of Spotify songs and generates a histogram in matplotlib with album art.')
    parser.add_argument('-a', '--albums', type=str, required=True,
                        help='name of the saved albums JSON file')
    args = parser.parse_args(args)

    dumpfile = open(args.albums, 'r')
    library = json.load(dumpfile)
    al_covers, al_years = read_albums_from_json(library)

    generate_and_save_histogram(al_covers, al_years)


if __name__ == '__main__':
    main(sys.argv[1:])
