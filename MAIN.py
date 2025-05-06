from GetInfoAboutProducts import get_data
from ParseDATA import start_parse


def main():

    CATEGORY, ITEM, FBRAND, FCOLOR = get_data()
    # print(f"{CATEGORY} {ITEM} {FBRAND} {FCOLOR}")
    start_parse(CATEGORY, ITEM, FBRAND, FCOLOR)


if __name__ == '__main__':
    main()