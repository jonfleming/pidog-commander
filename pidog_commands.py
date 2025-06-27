from pidog import Pidog
from preset_actions import scratch, hand_shake, high_five, pant, body_twisting, bark_action, shake_head_smooth, bark, push_up, howling, attack_posture, lick_hand, feet_shake, sit_2_stand, nod, think, recall, alert, surprise,  stretch
from transcribe_mic import transcribe_streaming, get_speech_adaptation

# Import Pidog class
from pidog import Pidog

# instantiate a Pidog with custom initialized servo angles
my_dog = Pidog(leg_init_angles = [25, 25, -25, -25, 70, -45, -70, 45],
                head_init_angles = [0, 0, -25],
                tail_init_angle= [0]
            )

def process_text(text):
    print("heard:", str(text))
    execute(text)
    
def execute(text):
    if ("sit" in text):
        my_dog.do_action('sit', speed=80)
    if ("scratch" in text):
        scratch(my_dog)
    if ("shake" in text):
        hand_shake(my_dog)
    if ("five" in text) or ("5" in text):
        high_five(my_dog)
    if ("pant" in text):
        pant(my_dog)
    if ("twist" in text):
        body_twisting(my_dog)
    if ("speak" in text):
        bark_action(my_dog)
        bark(my_dog)
    if ("bark" in text):
        bark_action(my_dog)
        bark(my_dog)
    if ("no" in text):
        shake_head_smooth(my_dog)
    if ("up" in text):
        push_up(my_dog)
    if ("howl" in text):
        howling(my_dog)
    if ("attack" in text):
        attack_posture(my_dog)
    if ("lick" in text):
        lick_hand(my_dog)
    if ("stand" in text):
        sit_2_stand(my_dog)
    if ("yes" in text):
        nod(my_dog)
    if ("think" in text):
        think(my_dog)
    if ("recall" in text):
        recall(my_dog)
    if ("alert" in text):
        alert(my_dog)
    if ("surprise" in text):
        surprise(my_dog)
    if ("stretch" in text):
        stretch(my_dog)        
    
def main():
    adaptation = get_speech_adaptation('phrases.txt')
    transcribe_streaming(sr=44100, callback=process_text, speech_adaptation=adaptation)


if __name__ == '__main__':
    main()