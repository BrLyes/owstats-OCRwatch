import configparser
import csv
import os.path
import queue
import threading
import time
import traceback

if not os.path.isfile("config.ini"):
    print("config.ini not found!")
    time.sleep(5)
    exit(1)

from output import append_to_csv, write_to_influx, write_output, write_rank
from screenshot import take_screenshot
from ocr import process_screenshot_file, has_game_ended, write_json

import keyboard

ranks = [
    "b5", "b4", "b3", "b2", "b1",
    "s5", "s4", "s3", "s2", "s1",
    "g5", "g4", "g3", "g2", "g1",
    "p5", "p4", "p3", "p2", "p1",
    "d5", "d4", "d3", "d2", "d1",
    "m5", "m4", "m3", "m2", "m1",
    "gm5", "gm4", "gm3", "gm2", "gm1"
]

latest = {}


def track(lock):
    global latest

    start = time.time()

    try:
        screenshot_name = take_screenshot()
        print("Processing...")
        game_ended = has_game_ended(screenshot_name)
        if game_ended:
            print("game has ended")
        else:
            print("game is still going on")
        #print(result)
        #result = process_screenshot_file(screenshot_name)
    except:
        print('track() broke')
        print(traceback.format_exc())

def track_loop(lock):
    tab_pressed_time = 0
    while 1:
        try:
            track(lock)
            time.sleep(10)  # wait a bit before tracking again
        except:
            print("loop broke")
            break


def cmd_loop(q, lock):
    while 1:
        input()
        with lock:
            print("Confirm exit by writing quit")
            cmd = input('> ')

        q.put(cmd)
        if cmd == 'quit':
            print("break")
            break


def main():
    cmd_queue = queue.Queue()
    stdout_lock = threading.Lock()

    cmd_thread = threading.Thread(target=cmd_loop, args=(cmd_queue, stdout_lock), daemon=True)
    cmd_thread.start()

    track_thread = threading.Thread(target=track_loop, args=(stdout_lock,), daemon=True)
    track_thread.start()

    while (cmd_thread.is_alive() or track_thread.is_alive()):
        cmd_thread.join(1)
        track_thread.join(1)

        cmd = cmd_queue.get()
        if cmd == 'quit':
            break
        if cmd in ranks:
            print("Tracking comp rank", cmd)
            write_rank(cmd, ranks)
        else:
            action(stdout_lock)

if __name__ == '__main__':
    main()
