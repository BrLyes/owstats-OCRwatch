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
from output import write_to_owstats

import keyboard

latest = {}
tracking = False

def toggle_tracking(e):
    global tracking
    tracking = not tracking
    print("Tracking status switched to: "+tracking)

keyboard.on_press_key('F12', toggle_tracking)


def track(lock):
    global latest, tracking
    start = time.time()

    try:
        if tracking:
            screenshot_name = take_screenshot()
            print("Processing...")

            #Checking if player is in a game
            game_ended = has_game_ended(screenshot_name)
            print(game_ended)
            if game_ended:
                #Game ended let's press tab and take a screenshot
                print("game has ended")
                keyboard.press('tab')
                time.sleep(0.5)
                scoreboard_screenshot = take_screenshot()
                time.sleep(1)
                keyboard.release('tab')

                #Parsing result and sending to owstats
                result = process_screenshot_file(scoreboard_screenshot)
                write_to_owstats(result)

                #Disable tracking
                tracking=False
                print("Your game has been sent to owstats, dont forget to press F12 again for your next game!")
            else:
                print("game is still going on")
    except:
        print('track() broke')
        print(traceback.format_exc())

def track_loop(lock):
    tab_pressed_time = 0
    while 1:
        try:
            track(lock)
            time.sleep(2)  # wait a bit before tracking again
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
    print("init")
    cmd_queue = queue.Queue()
    stdout_lock = threading.Lock()

    cmd_thread = threading.Thread(target=cmd_loop, args=(cmd_queue, stdout_lock), daemon=True)
    cmd_thread.start()

    track_thread = threading.Thread(target=track_loop, args=(stdout_lock,), daemon=True)
    track_thread.start()

    print("ready for tracking, press F12 when you are in a game to start the tracker")
    while (cmd_thread.is_alive() or track_thread.is_alive()):
        cmd_thread.join(1)
        track_thread.join(1)

        cmd = cmd_queue.get()
        if cmd == 'quit':
            break
        else:
            action(stdout_lock)

if __name__ == '__main__':
    main()
