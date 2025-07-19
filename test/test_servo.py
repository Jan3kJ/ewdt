from machine import Pin, PWM
import time

SERVO_ON_TIME = 2  # seconds
SERVO_PIN = 15         # PWM output for servo

def set_servo_speed(speed):
    """
    speed: -1.0 (full reverse) to 0 (stop) to 1.0 (full forward)
    """
    # For 50Hz PWM, 1.5ms pulse is stop, 1.0ms is full reverse, 2.0ms is full forward
    # 1.0ms/20ms = 5%, 1.5ms/20ms = 7.5%, 2.0ms/20ms = 10%
    min_duty = 2100   # 5% of 65535 - decreased by exepriemnt
    mid_duty = 4915   # 7.5% of 65535
    max_duty = 7600   # 10% of 65535 - increased by exepriemnt
    if speed > 0:
        duty = int(mid_duty + (max_duty - mid_duty) * speed)
    elif speed < 0:
        duty = int(mid_duty + (mid_duty - min_duty) * speed)
    else:
        duty = mid_duty
    print('duty cycle: ', duty)
    servo.duty_u16(duty)


servo = PWM(Pin(SERVO_PIN))
servo.freq(50)

print('start')
set_servo_speed(1)  # Full speed forward
time.sleep(SERVO_ON_TIME)
set_servo_speed(0)
time.sleep(1)
set_servo_speed(-1)
time.sleep(SERVO_ON_TIME)

# for duty in range(7000, 7700, 100):
#     print("duty:", duty)
#     servo.duty_u16(duty)
#     time.sleep(1)

set_servo_speed(0)
print('end')
