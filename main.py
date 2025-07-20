# eWDT MicroPython Firmware for RP2040-Plus
# Implements requirements from README, using VBUS detection via ADC1 (GP27)

from machine import PWM, Pin, ADC
import time

# Pin assignments (adjust if needed)
SERVO_PIN = 13         # PWM output for servo
RELAY_PIN = 15         # Digital output for relay
LED_PIN = 25           # Digital output for internal LED
BUTTON_LED_PIN = 14    # Digital output for BUTTON LED
BATTERY_ADC_PIN = 26   # ADC0 for battery voltage divider
VREF_ADC_PIN = 29      # ADC3 for VSYS detection (via internal voltage divider)

# Constants
SERVO_ON_TIME = 5  # seconds
LOW_BATTERY_VOLTAGE = 3.7  # volts, >10% capacity
FULL_BATTERY_VOLTAGE = 4.1  # volts, ~90% capacity
LED_BLINK_INTERVAL_SLOW = 2  # seconds
LED_BLINK_INTERVAL_FAST = 0.5  # seconds

# Setup pins
servo = PWM(Pin(SERVO_PIN))
servo.freq(50)
relay = Pin(RELAY_PIN, Pin.OUT)
led = Pin(LED_PIN, Pin.OUT)
button_led = Pin(BUTTON_LED_PIN, Pin.OUT)
battery_adc = ADC(BATTERY_ADC_PIN)
vref_adc = ADC(VREF_ADC_PIN)


# Helper: Read battery voltage (adjust conversion for your divider)
def read_battery_voltage():
    raw = battery_adc.read_u16()
    voltage = (raw / 65535) * 3.3 * 2  # 2x for divider
    return voltage


# Helper: Read VREF voltage (internal voltage divider)
def read_vref_voltage():
    raw = vref_adc.read_u16()
    voltage = (raw / 65535) * 3.3 * 3  # 3.3V internal reference, 3x for internal divider
    return voltage


# Helper: Detect USB connection via VBUS (divider to ADC1)
def is_usb_connected():
    vref_voltage = read_vref_voltage()
    return vref_voltage > 4.5 # vref_adc higher than 4.5V means USB connected


def led_on():
    led.on()  # interal LED for debugging
    button_led.on()

def led_off():
    led.off()
    button_led.off()

# Helper: Set servo speed for continuous rotation
def set_servo_speed(speed):
    """
    speed: -1.0 (full speed clockwise) to 0 (stop) to 1.0 (full speed counter clockwise)
    """
    # For 50Hz PWM, 1.5ms pulse is stop, 1.0ms is full reverse, 2.0ms is full forward
    # 1.0ms/20ms = 5%, 1.5ms/20ms = 7.5%, 2.0ms/20ms = 10%
    min_duty = 2100   # 5% of 65535 - decreased by exeperiment
    mid_duty = 4915   # 7.5% of 65535
    max_duty = 7600   # 10% of 65535 - increased by exeperiment
    if speed > 0:
        duty = int(mid_duty + (max_duty - mid_duty) * speed)
    elif speed < 0:
        duty = int(mid_duty + (mid_duty - min_duty) * speed)
    else:
        duty = mid_duty
    print('duty cycle: ', duty)
    servo.duty_u16(duty)

# Helper: Blink LED
def blink_led(times, interval):
    for _ in range(times):
        led_on()
        time.sleep(interval)
        led_off()
        time.sleep(int(interval/2))


# Charging mode: LED blinks slowly until battery is full, then off
def charging_mode():
    while is_usb_connected():
        if read_battery_voltage() < FULL_BATTERY_VOLTAGE:
            blink_led(30, LED_BLINK_INTERVAL_SLOW)
        else:
            # fully charged and usb still connected
            led_on()
            relay.off()
            time.sleep(2)

    # if unplugged befor fully charged
    led_off()
    relay.off()  # Ensure relay is off after charging


def normal_mode():
    # Start servo and relay
    led_on()
    set_servo_speed(1.0)  # Full speed forward
    time.sleep(SERVO_ON_TIME)
    set_servo_speed(0)    # Stop
    led_off()
    if read_battery_voltage() < LOW_BATTERY_VOLTAGE:
        blink_led(4, LED_BLINK_INTERVAL_FAST)  
    relay.off()  # Ensure relay is off after operation


# Main loop
def main():        
    relay.on()
    if is_usb_connected():
        print("USB connected")
        charging_mode()
    else:
        print("USB not connected")
        normal_mode()

    relay.off()  # Ensure relay is off after charging
    

main() 
