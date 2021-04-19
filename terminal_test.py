from time import sleep
from os import system


def clear(dt=0.033):
    sleep(dt)
    system("cls")


def alarm():
    for i in range(5):
        print("\033[47m" + " " * 99999999)
        sleep(0.5)
    print("\033[0m")


i = 0
while True:
    i += 1
    print("=" * 100)
    print("=" * 100)
    print("=" * 100)
    print("=" * 100)
    if i % 500 is 0:
        alarm()
