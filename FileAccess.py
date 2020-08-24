# Python
# File Access class

text_file = "info.txt"


class FileAccess:

    def __init__(self):
        return

    @staticmethod
    def read():
        # noinspection PyBroadException
        try:
            f = open(text_file)
        except FileNotFoundError:
            print("ERROR: No data exists. Try adding a user.")
            return None

        data = []

        for line in f:
            # Parse Name
            data.append(line.rstrip())
        f.close()

        print("Read from a file")

        return data

    @staticmethod
    def write(*args):

        # noinspection PyBroadException
        try:
            # If file exists
            f = open(text_file, "a")
        except FileNotFoundError:
            # If file does not exist, create
            f = open(text_file, "w")

        for arg in args:
            f.write(arg)

        f.close()
        print("Wrote to file")

