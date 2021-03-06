# Python
# main() function

import sys
import re

from crontab import CronTab
from PlaylistUpdater import PlaylistUpdater
from FileAccess import FileAccess

my_cron = CronTab(user='joseph')


def print_intro_prompt():
    # Intro Prompt
    print("################################")
    print("Welcome to Better Music Friday  ")
    print("################################")

    print_help()


def print_help():
    # Intro Prompt
    print("List of commands ")
    print("--------------------------------")
    print("-Enter 'HELP' to view this menu")
    print("-Enter 'NEW USER' to register a new user")
    print("-Enter 'REMOVE' to remove a user")
    print("-Enter 'INFO' to view program info")
    print("-Enter 'UPDATE' to update playlists")
    print("-Enter 'SETUP' to setup cron")
    print("-Enter 'PRINT' to print cron jobs")
    print("-Enter 'QUIT' to quit application")
    print("--------------------------------")


def print_info(fa):
    user_data = fa.read()

    print("--------------------------------")
    print("List of Users ")
    print("--------------------------------")

    i = 0
    for user in user_data:
        print(user)
        i = i + 1
        if i % 2 == 0:
            print("--------------------------------")


def remove_user(command):
    return None


# Does not check if added duplicate user
def add_user(fa):

    print("Enter your Spotify username")
    user = input()

    # Verify username has correct amount of characters
    if len(user) != 10:
        print("Entered Invalid username! Exiting...")
        return

    print("Enter your name: ")
    name = input()

    # Verify they put something decent
    if not len(name.strip()) > 4:
        print("Entered Invalid name! Exiting...")
        return

    fa.write(
        "name: " + name + "\n",
        "user: " + user + "\n")


def print_cron():
    for job in my_cron:
        print(job)


def schedule_cron():
    my_cron.remove_all()
    job = my_cron.new(command='python3 ~/Library/Mobile\ Documents/com~apple~CloudDocs/GitHub/BetterMusicFriday/main.py')
    job.dow.every(5)
    my_cron.write()


def clear_cron():
    my_cron.remove_all()
    my_cron.write()


# Defining main function
def main(arg=None):

    if arg is None:
        PlaylistUpdater(user="223452345").update()
        sys.exit(0)

    if arg != "update":
        update_all()
        sys.exit(0)

    fa = FileAccess()

    print_intro_prompt()

    while True:
        print("\nEnter a command: ")
        command = input().lower()

        ## Handle Command
        if re.search("^he*", command):
            print_help()
        elif re.search("^up*", command):
            update_all()
        elif re.search("^ne*", command):
            add_user(fa)
        elif re.search("^re*", command):
            print("Remove User")
        elif re.search("^in*", command):
            print_info(fa)
        elif re.search("^se*", command):
            schedule_cron()
        elif re.search("^pr*", command):
            print_cron()
        elif re.search("^qu*", command):
            print("Goodbye!")
            sys.exit(0)
        else:
            print("ERROR: Invalid Command")
            print("Enter 'HELP' for list of commands")

    return 0


# Using the special variable
# __name__
if __name__ == "__main__":
    main()
