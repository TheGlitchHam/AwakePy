"""
Script to keep the screen awake and active for *different reasons*
"""
import time
import multiprocessing
import PySimpleGUI as gui
import pyautogui
from directKeys.directKeys import PressKey, ReleaseKey,  LSHIFT, SPACE 

# Disable failsafe as it will cause an exception if you accidentally move the mouse to the edge of the screen

button_dict = {"LSHIFT": (LSHIFT, "shift") , "SPACE": (SPACE, "space") }
keys_list = [*button_dict.keys()]
values_list = [*button_dict.values()]


def AwakeUI():
    """
    Function to generate a gui based on PySimpleGUI Package

    Runs in multiple threads and can start/ stop the keeping awake functionality
    """

    gui.theme("DarkAmber")

    layout = [
        [gui.Text("Awaiting to work", key="-OUTPUT-"), gui.Checkbox("Simulate physical button presses", default=True, key="-PHYSBTN-", enable_events=True)],
        [gui.Button("Start", key="-START-")],
        [gui.Button(f"Pressing {keys_list[0]}", key="-SWITCH-")]
    ]

    window = gui.Window("Awake", layout=layout, size=(370, 100))

    is_awake = False
    timer = 0.0
    manager = multiprocessing.Manager()
    use_primary_key = manager.Value("i", True)
    use_phys_btns = manager.Value("o", True)

    while True:
        event, values = window.read()
        if event == gui.WIN_CLOSED or event == 'Cancel':
            if p2.is_alive():
                p2.terminate()
            break
        elif event == "-PHYSBTN-":
            print(f"Switching to {'physical' if values['-PHYSBTN-'] else 'virtual'} buttons")        
            use_phys_btns.value = values["-PHYSBTN-"]
        elif event == '-START-':
            if is_awake == False:
                timer = time.time()
                p2 = multiprocessing.Process(
                    target=keep_awake, args=(use_primary_key, use_phys_btns, ))
                p2.start()
                window['-START-'].update('Stop')
                window['-OUTPUT-'].update("Active and working")
                is_awake = True
            elif is_awake == True:

                p2.terminate()
                window['-START-'].update('Start')
                timer_finished = convert_to_minutes_seconds(
                    round(time.time() - timer))
                window['-OUTPUT-'].update(timer_finished)
                print(timer_finished)
                is_awake = False
        elif event == "-SWITCH-":
            use_primary_key.value = not use_primary_key.value
            window["-SWITCH-"].update(
                f"Pressing {keys_list[0]}") if use_primary_key.value else window["-SWITCH-"].update(f"Pressing {keys_list[1]}")
            print(
                f"Switching Button-Press to {keys_list[0] if use_primary_key.value else keys_list[1]}")
        
    window.close()
    if p2.is_alive():
        p2.terminate()


def keep_awake(use_primary_key, use_phys_btns, timer: float = 30):
    """
    Function to start a the awake process, which will automatically trigger a "shift" press every given intervall 
    :param use_primary_key: ValueProxy of boolean to switch between primary an secondary key. Multiprocess safe
    :param timer: the intervall in which shift pressess are triggered. The standard is set to 180 seconds
    """
    print(f"Starting to work")
    time.sleep(timer)
    while True:
        button_to_press = values_list[0] if use_primary_key.value else values_list[1]
        print(
            f"Pressing {'physical' if use_phys_btns.value else 'virtual'} Button {keys_list[0] if use_primary_key.value else keys_list[1]}")

        if use_phys_btns.value:
            PressKey(button_to_press[0])
            ReleaseKey(button_to_press[0])
        else: 
            pyautogui.press(button_to_press[1])
        time.sleep(timer)


def convert_to_minutes_seconds(time: float) -> str:
    """ Small utility function to convert given time in seconds to a string representation with minutes and seconds displayed"""
    minutes, seconds = divmod(time, 60)
    minutes_text = ""
    if minutes > 0:
        minutes_text = f"{minutes} minutes "

    return f"Finished working for {minutes_text}{seconds} seconds"


def start():
    """Entrypoint for mulitprocessing UI and script execution"""
    p1 = multiprocessing.Process(target=AwakeUI)
    p1.start()


if __name__ == "__main__":
    start()
