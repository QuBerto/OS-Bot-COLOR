import math

import cv2
import numpy as np
import pyautogui

import utilities.api.locations as loc
import utilities.imagesearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.geometry import Point, Rectangle, RuneLiteObject
from utilities.walker import Walker


class OSRSWalkingExample(OSRSBot):
    def __init__(self):
        super().__init__(bot_title="Wanderer", description="Walk almost anywhere.")

    def create_options(self):
        locations = [name for name in vars(loc) if not name.startswith("__")]
        self.options_builder.add_dropdown_option("dest", "Destination:", locations)

    def save_options(self, options: dict):
        for option in options:
            if option == "dest":
                self.log_msg(f"dest: {options[option]}")
                self.dest = options[option]
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):
        while True:
            self.compass_needle = imsearch.BOT_IMAGES.joinpath("ui_templates", "compass_needle.png")
            re = Rectangle(self.win.compass_orb.get_center().x - 6, self.win.compass_orb.get_center().y - 6, 14, 14)
            result = self.calculate_compass_angle(re.screenshot(), re.get_center(), debug=True)
            print(result)

    def calculate_compass_angle(self, image, compass_center, debug=False):
        # Convert image to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Define range for red color and create mask
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = cv2.bitwise_or(mask1, mask2)

        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            raise ValueError("No red regions found in the image.")

        # Find the furthest red pixel from the center
        max_distance = -1
        furthest_point = None

        for contour in contours:
            for point in contour:
                x, y = point[0]
                dx = x - 7
                dy = y - 7
                distance = math.sqrt(dx**2 + dy**2)
                if distance > max_distance:
                    max_distance = distance
                    furthest_point = (x, y)

        if furthest_point is None:
            raise ValueError("No furthest red pixel found.")

        if debug:
            # Highlight the furthest red pixel in green and the center in blue
            debug_image = image.copy()
            cv2.circle(debug_image, furthest_point, 1, (0, 255, 0), -1)  # Draw green circle at furthest point
            cv2.circle(debug_image, (7, 7), 1, (255, 0, 0), -1)  # Draw blue circle at center

            # Zoom in the debug image by 8x
            zoom_factor = 8
            debug_image = cv2.resize(debug_image, (0, 0), fx=zoom_factor, fy=zoom_factor, interpolation=cv2.INTER_NEAREST)

            cv2.imshow("Compass Debug", debug_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        print(furthest_point)

        # Define the center and the furthest point
        center = (7, 7)

        # Calculate the differences in x and y coordinates
        dx = furthest_point[0] - center[0]
        dy = furthest_point[1] - center[1]

        # Calculate the angle in radians and then convert to degrees
        angle_radians = math.atan2(dy, dx)
        angle_degrees = math.degrees(angle_radians)

        print(f"Angle in degrees: {angle_degrees}")
        # angle = math.degrees(math.atan2(dy, dx))
        # # Convert angle to compass degrees (0 degrees is North)
        # compass_angle = (450 - angle) % 360
        # return compass_angle
