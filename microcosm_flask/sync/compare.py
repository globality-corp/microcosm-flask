"""
Compare resources from two YAML files.

Useful for validating that a sync in/out retains the same state.

"""
from argparse import ArgumentParser

from yaml import load_all


def to_dict(path):
    """
    Normalize each resource as a dictionary for smarter comparison.

    Relies on link sorting performed by the pull script.

    """
    with open(path) as file_:
        return {
            key: value
            for dct in load_all(file_)
            for key, value in dct.items()
        }


def main():
    parser = ArgumentParser()
    parser.add_argument("left")
    parser.add_argument("right")
    args = parser.parse_args()

    left, right = to_dict(args.left), to_dict(args.right)

    left_keys = set(left.keys())
    right_keys = set(right.keys())
    if left_keys != right_keys:
        print("Only in left:")  # noqa
        for key in left_keys - right_keys:
            print(" - {}".format(key))  # noqa
        print("Only in right:")  # noqa
        for key in right_keys - left_keys:
            print(" - {}".format(key))  # noqa
        exit(1)

    for key in left.keys():
        if left[key] != right[key]:
            print("Different values for: {}".format(key))  # noqa
            print("-" * 20)  # noqa
            print("Left:")  # noqa
            print(left[key])  # noqa
            print("Right:")  # noqa
            print(right[key])  # noqa
            exit(1)


if __name__ == '__main__':
    main()
