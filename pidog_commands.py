from time import sleep
from pidog import Pidog
from preset_actions import scratch, hand_shake, high_five, pant, body_twisting, bark_action, shake_head_smooth, bark, push_up, howling, attack_posture, lick_hand, feet_shake, sit_2_stand, nod, think, recall, alert, surprise,  stretch
from transcribe_mic import transcribe_streaming, get_speech_adaptation

# Import Pidog class
from pidog import Pidog

yaw = 0
roll = 0
pitch = 0
paws_out = False

# instantiate a Pidog with custom initialized servo angles
my_dog = Pidog(leg_init_angles = [25, 25, -25, -25, 70, -45, -70, 45],
                head_init_angles = [0, 0, -25],
                tail_init_angle= [0]
            )

def process_text(text):
    text = str(text).lower()
    print("heard:", text)
    execute(text)
    
def execute(text):
    global yaw, roll, pitch, paws_out
    if ("sit" in text):
        my_dog.do_action('sit', speed=50)
    if ("stand" in text):
        sit_2_stand(my_dog)
    if ("lay" in text) or ("lie" in text):
        if paws_out:
            my_dog.do_action('lie', speed=60)
            paws_out = False
        else:
            my_dog.do_action('lie_with_hands_out', speed=60)
            paws_out = True
    if ("speak" in text):
        bark_action(my_dog)
        bark(my_dog)
    if ("bark" in text):
        bark_action(my_dog)
        bark(my_dog)
    if ("howl" in text):
        howling(my_dog)
    if ("shake" in text):
        my_dog.do_action('sit', speed=50)
        hand_shake(my_dog)
    if ("five" in text) or ("5" in text):
        my_dog.do_action('sit', speed=50)
        high_five(my_dog)
    if ("scratch" in text):
        my_dog.do_action('lie', speed=60)
        scratch(my_dog)
    if ("pant" in text):
        pant(my_dog)
    if ("sleep" in text):
        my_dog.do_action('lie', speed=40)
        my_dog.do_action('doze_off', speed=95)
    if ("twist" in text):
        my_dog.do_action('lie', speed=60)
        body_twisting(my_dog)
    if ("pushup" in text) or ("push" in text) or ("push up" in text):
        push_up(my_dog)
    if ("surprise" in text):
        surprise(my_dog)
    if ("alert" in text):
        alert(my_dog)
    if ("wag tail" in text):
        my_dog.do_action('wag_tail', speed=95)

    if ("no" in text):
        shake_head_smooth(my_dog)
    if ("yes" in text):
        nod(my_dog)
    if ("attack" in text):
        attack_posture(my_dog)
    if ("lick" in text):
        lick_hand(my_dog)
    if ("think" in text):
        think(my_dog)
    if ("recall" in text):
        recall(my_dog)
    if ("look left" in text):
       yaw = 15
       my_dog.head_move([[yaw, roll, pitch]], pitch_comp=0, immediately=True, speed=80)
    if ("look right" in text):
       yaw = -15
       my_dog.head_move([[yaw, roll, pitch]], pitch_comp=0, immediately=True, speed=80)
    if ("look up" in text):
       pitch = 10
       my_dog.head_move([[yaw, roll, pitch]], pitch_comp=0, immediately=True, speed=80)
    if ("look down" in text):
       pitch = -25
       my_dog.head_move([[yaw, roll, pitch]], pitch_comp=0, immediately=True, speed=80)
    if ("forward" in text):
        my_dog.do_action('forward', speed=98)
    if ("backward" in text):
        my_dog.do_action('backward', speed=98)
    if ("turn left" in text):
        my_dog.do_action('turn_left', speed=98)
    if ("turn right" in text):
        my_dog.do_action('turn_right', speed=98)
    if ("reset" in text):
       yaw = 0
       roll = 0
       pitch = 0
       my_dog.head_move([[yaw, roll, pitch]], pitch_comp=0, immediately=True, speed=80)
       sleep(1)
       my_dog.body_stop()

def main():
    adaptation = get_speech_adaptation('phrases.txt')
    transcribe_streaming(sr=44100, callback=process_text, speech_adaptation=adaptation)


if __name__ == '__main__':
    main()