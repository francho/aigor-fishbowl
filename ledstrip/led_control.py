#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import getopt
import sys

import time

if __name__ == '__main__':
    sys.path.append('../')

from ledstrip.vendor.neopixel import Adafruit_NeoPixel

# LED strip configuration:

LED_COUNT = 20  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53

SUN_PORT = 23


def color_channels(color):
    color_hex = "%08x" % color
    a = int(color_hex[:2], 16)
    r = int(color_hex[2:4], 16)
    g = int(color_hex[4:6], 16)
    b = int(color_hex[6:8], 16)
    print()
    print("{:08X} r={} g={} b={} a={}".format(color, r, g, b, a))
    return r, g, b, a


class LedControl:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(SUN_PORT, GPIO.OUT)
        self.day_light_leds = [
            self.color(250, 255, 0),
            self.color(255, 205, 0),
            self.color(205, 205, 0),
            self.color(200, 255, 0),
        ]

        self.strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS,
                                       LED_CHANNEL)
        self.strip.begin()

    def color(self, red, green, blue, bright=255):
        return (bright << 24) | (blue << 16) | (red << 8) | green

    def _set_all(self, color):
        for pixel in range(self.strip.numPixels()):
            self.strip.setPixelColor(pixel, color)
            self.strip.show()

    def _leds_from_array(self, colors, delay=0.1, fade_steps=255, fade=True):
        num_colors = len(colors)
        num_pixels = self.strip.numPixels()
        pixels_per_color = num_pixels / num_colors

        color = None
        for fade_step in range(1, fade_steps):
            pixel = 0
            for color_step in range(num_colors):
                for pixel_step in range(pixels_per_color):
                    color = colors[color_step]
                    if fade:
                        self._pixel_fade_to(pixel, color, fade_step, fade_steps)
                    else:
                        self._pixel_set_color(pixel, color)
                    pixel += 1
            for pixel in range(pixel, num_pixels):
                if fade:
                    self._pixel_fade_to(pixel, color, fade_step, fade_steps)
                else:
                    self._pixel_set_color(pixel, color)
            self.strip.show()
            time.sleep(delay)

    def _pixel_set_color(self, pixel, color):
        r, g, b, a = color_channels(color)
        self.strip.setPixelColor(pixel, self.color(r, b, g, a))

    def _pixel_fade_to(self, pixel, color, step, total_steps):
        r1, g1, b1, a1 = color_channels(self.strip.getPixelColor(pixel))
        r2, g2, b2, a2 = color_channels(color)

        r = self._fade_color_channel(r2, r1, step, total_steps)
        g = self._fade_color_channel(g2, g1, step, total_steps)
        b = self._fade_color_channel(b2, b1, step, total_steps)
        a = self._fade_color_channel(a2, a1, step, total_steps)

        print("{} : {} - r:{} g:{} b:{} a:{}".format(step, pixel, r, g, b, a))

        self.strip.setPixelColor(pixel, self.color(r, b, g, a))

    def _fade_color_channel(self, final_c, initial_c, step, total_steps):
        factor = float(final_c - initial_c) / total_steps
        print(factor)
        result = int(initial_c + factor * step)
        print(result)
        if result > 255 or (result > final_c and factor > 0):
            result = final_c
        elif result < 0 or (result < final_c and factor < 0):
            result = final_c
        return int(result)

    def _sun_on(self):
        GPIO.output(SUN_PORT, 0)

    def _sun_off(self):
        if GPIO.input(SUN_PORT) == 0:
            GPIO.output(SUN_PORT, 1)

    def dawn(self):
        #self._leds_from_array(self.day_light_leds, delay=1)
        #self._set_all(self.color(0, 0, 0))
        self._sun_off()
        self._set_all(self.color(255, 255, 255))

    def sunset(self):
        self._set_all(self.color(255, 255, 255))
        self._sun_off()
        self._leds_from_array(self.day_light_leds, delay=1)

    def nightfall(self):
        self._sun_off()
        self._leds_from_array(self.day_light_leds, fade_steps=2, fade=False)
        self._leds_from_array([
            self.color(255, 1, 255, 100),
            self.color(255, 1, 255, 100),
            self.color(255, 1, 255, 100),
        ], delay=0.1)
        self._leds_from_array([
            self.color(255, 1, 255, 1),
            self.color(255, 1, 255, 1),
            self.color(255, 1, 255, 1),
        ], delay=0.1)
        self._set_all(self.color(0, 0, 0))

    def night(self):
        self._sun_off()
        self._set_all(self.color(0, 0, 0, 0))

    def set_color(self, red, blue, green, bright):
        self._set_all(self.color(red,green,blue,bright))


# Main program logic follows:
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["dawn", "sunset", "nightfall", "off", "color"])
    except getopt.GetoptError:
        print('test.py --dawn')
        print('test.py --sunset')
        print('test.py --nightfall')
        print('test.py --night')
        sys.exit(2)

    control = LedControl()
    for opt, arg in opts:
        if opt in '--dawn':
            control.dawn()
        elif opt in '--sunset':
            control.sunset()
        elif opt in '--nightfall':
            control.nightfall()
        elif opt in '--off':
            control.night()
        elif opt in '--color':
            print(args)
            control.set_color(int(args[0]),int(args[1]),int(args[2]),int(args[3]))
