import time

import mss
import numpy as np
import pyautogui as pag
import pytweening
from pyclick import HumanCurve

import utilities.imagesearch as imsearch
from utilities.geometry import Point, Rectangle
from utilities.random_util import truncated_normal_sample


class Mouse:
    click_delay = True
    custom_speeds = {}
    DEFAULT_SPEEDS = {"slowest": (85, 100), "slow": (65, 80), "medium": (45, 60), "fast": (20, 40), "fastest": (10, 15), "insane": (2, 4)}

    def move_to(self, destination: tuple, **kwargs):
        """
        Use Bezier curve to simulate human-like mouse movements.
        Args:
            destination: x, y tuple of the destination point
            destination_variance: pixel variance to add to the destination point (default 0)
        Kwargs:
            knotsCount: number of knots to use in the curve, higher value = more erratic movements
                        (default determined by distance)
            mouseSpeed: speed of the mouse (options: 'slowest', 'slow', 'medium', 'fast', 'fastest')
                        (default 'fast')
            tween: tweening function to use (default easeOutQuad)
        """
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        knotsCount = kwargs.get("knotsCount", self.__calculate_knots(destination))
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.5)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        mouseSpeed = kwargs.get("mouseSpeed", "fast")
        mouseSpeed = self.__get_mouse_speed(mouseSpeed)
        dest_x = destination[0]
        dest_y = destination[1]

        start_x, start_y = pag.position()
        for curve_x, curve_y in HumanCurve(
            (start_x, start_y),
            (dest_x, dest_y),
            offsetBoundaryX=offsetBoundaryX,
            offsetBoundaryY=offsetBoundaryY,
            knotsCount=knotsCount,
            distortionMean=distortionMean,
            distortionStdev=distortionStdev,
            distortionFrequency=distortionFrequency,
            tween=tween,
            targetPoints=mouseSpeed,
        ).points:
            pag.moveTo((curve_x, curve_y))
            start_x, start_y = curve_x, curve_y

    def move_rel(self, x: int, y: int, x_var: int = 0, y_var: int = 0, **kwargs):
        """
        Use Bezier curve to simulate human-like relative mouse movements.
        Args:
            x: x distance to move
            y: y distance to move
            x_var: maxiumum pixel variance that may be added to the x distance (default 0)
            y_var: maxiumum pixel variance that may be added to the y distance (default 0)
        Kwargs:
            knotsCount: if right-click menus are being cancelled due to erratic mouse movements,
                        try setting this value to 0.
        """
        if x_var != 0:
            x += round(truncated_normal_sample(-x_var, x_var))
        if y_var != 0:
            y += round(truncated_normal_sample(-y_var, y_var))
        self.move_to((pag.position()[0] + x, pag.position()[1] + y), **kwargs)

    def click(self, button="left", force_delay=False, check_red_click=False) -> tuple:
        """
        Clicks on the current mouse position.
        Args:
            button: button to click (default left).
            force_delay: whether to force a delay between mouse button presses regardless of the Mouse property.
            check_red_click: whether to check if the click was red (i.e., successful action) (default False).
        Returns:
            None, unless check_red_click is True, in which case it returns a boolean indicating
            whether the click was red (i.e., successful action) or not.
        """
        mouse_pos_before = pag.position()
        pag.mouseDown(button=button)
        mouse_pos_after = pag.position()
        if force_delay or self.click_delay:
            LOWER_BOUND_CLICK = 0.03  # Milliseconds
            UPPER_BOUND_CLICK = 0.2  # Milliseconds
            AVERAGE_CLICK = 0.06  # Milliseconds
            time.sleep(truncated_normal_sample(LOWER_BOUND_CLICK, UPPER_BOUND_CLICK, AVERAGE_CLICK))
        pag.mouseUp(button=button)
        if check_red_click:
            return self.__is_red_click(mouse_pos_before, mouse_pos_after)

    def right_click(self, force_delay=False):
        """
        Right-clicks on the current mouse position. This is a wrapper for click(button="right").
        Args:
            with_delay: whether to add a random delay between mouse down and mouse up (default True).
        """
        self.click(button="right", force_delay=force_delay)

    def __rect_around_point(self, mouse_pos: Point, pad: int) -> Rectangle:
        """
        Returns a rectangle around a Point with some padding.
        """
        # Get monitor dimensions
        max_x, max_y = pag.size()
        max_x, max_y = int(str(max_x)), int(str(max_y))

        # Get the rectangle around the mouse cursor with some padding, ensure it is within the screen.
        mouse_x, mouse_y = mouse_pos
        p1 = Point(max(mouse_x - pad, 0), max(mouse_y - pad, 0))
        p2 = Point(min(mouse_x + pad, max_x), min(mouse_y + pad, max_y))
        return Rectangle.from_points(p1, p2)

    def __is_red_click(self, mouse_pos_from: Point, mouse_pos_to: Point) -> bool:
        """
        Checks if a click was red, indicating a successful action.
        Args:
            mouse_pos_from: mouse position before the click.
            mouse_pos_to: mouse position after the click.
        Returns:
            True if the click was red, False if the click was yellow.
        """
        CLICK_SPRITE_WIDTH_HALF = 7
        rect1 = self.__rect_around_point(mouse_pos_from, CLICK_SPRITE_WIDTH_HALF)
        rect2 = self.__rect_around_point(mouse_pos_to, CLICK_SPRITE_WIDTH_HALF)

        # Combine two rects into a bigger rectangle
        top_left_pos = Point(min(rect1.get_top_left().x, rect2.get_top_left().x), min(rect1.get_top_left().y, rect2.get_top_left().y))
        bottom_right_pos = Point(max(rect1.get_bottom_right().x, rect2.get_bottom_right().x), max(rect1.get_bottom_right().y, rect2.get_bottom_right().y))
        cursor_sct = Rectangle.from_points(top_left_pos, bottom_right_pos).screenshot()

        for click_sprite in ["red_1.png", "red_3.png", "red_2.png", "red_4.png"]:
            try:
                if imsearch.search_img_in_rect(imsearch.BOT_IMAGES.joinpath("mouse_clicks", click_sprite), cursor_sct):
                    return True
            except mss.ScreenShotError:
                print("Failed to take screenshot of mouse cursor. Please report this error to the developer.")
                continue
        return False

    def __calculate_knots(self, destination: tuple):
        """
        Calculate the knots to use in the Bezier curve based on distance.
        Args:
            destination: x, y tuple of the destination point.
        """
        # Calculate the distance between the start and end points
        distance = np.sqrt((destination[0] - pag.position()[0]) ** 2 + (destination[1] - pag.position()[1]) ** 2)
        res = round(distance / 200)
        return min(res, 3)

    def __get_mouse_speed(self, speed: str) -> int:
        """
        Converts a text speed to a numeric speed for HumanCurve (targetPoints).
        """

        speed_range = self.get_speed(speed) or self.DEFAULT_SPEEDS.get(speed)

        if not speed_range:
            raise ValueError("Invalid mouse speed. Try one of: " + ", ".join(self.DEFAULT_SPEEDS.keys()) + ".")

        min, max = speed_range
        return round(truncated_normal_sample(min, max))

    def register_speed(self, speed_name: str, min_val: int, max_val: int):
        self.custom_speeds[speed_name] = (min_val, max_val)

    def register_mouse_speed(self, speed_name: str, min_val: int, max_val: int):
        self.register_speed(speed_name, min_val, max_val)

    def get_speed(self, speed_name: str):
        return self.custom_speeds.get(speed_name)

    def wind_move_to(self, destination: tuple, **kwargs):
        """
        Use Bezier curve to simulate human-like mouse movements.
        Args:
            destination: x, y tuple of the destination point
            destination_variance: pixel variance to add to the destination point (default 0)
        Kwargs:
            knotsCount: number of knots to use in the curve, higher value = more erratic movements
                        (default determined by distance)
            mouseSpeed: speed of the mouse (options: 'slowest', 'slow', 'medium', 'fast', 'fastest')
                        (default 'fast')
            tween: tweening function to use (default easeOutQuad)
        """

        dest_x = destination[0]
        dest_y = destination[1]

        start_x, start_y = pag.position()
        self.wind_mouse(start_x, start_y, dest_x, dest_y, M_0=18, W_0=1)

    def pyautogui_move_mouse(self, x, y):
        pag.moveTo(x, y)

    def wind_mouse(self, start_x, start_y, dest_x, dest_y, G_0=9, W_0=3, M_0=15, D_0=12):
        sqrt3 = np.sqrt(3)
        sqrt5 = np.sqrt(5)

        """
        WindMouse algorithm. Calls the pyautogui_move_mouse method with each new step.
        Released under the terms of the GPLv3 license.
        G_0 - magnitude of the gravitational force
        W_0 - magnitude of the wind force fluctuations
        M_0 - maximum step size (velocity clip threshold)
        D_0 - distance where wind behavior changes from random to damped
        """
        current_x, current_y = start_x, start_y
        v_x = v_y = W_x = W_y = 0
        while (dist := np.hypot(dest_x - start_x, dest_y - start_y)) >= 1:
            W_mag = min(W_0, dist)
            if dist >= D_0:
                W_x = W_x / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
                W_y = W_y / sqrt3 + (2 * np.random.random() - 1) * W_mag / sqrt5
            else:
                W_x /= sqrt3
                W_y /= sqrt3
                if M_0 < 3:
                    M_0 = np.random.random() * 3 + 3
                else:
                    M_0 /= sqrt5
            v_x += W_x + G_0 * (dest_x - start_x) / dist
            v_y += W_y + G_0 * (dest_y - start_y) / dist
            v_mag = np.hypot(v_x, v_y)
            if v_mag > M_0:
                v_clip = M_0 / 2 + np.random.random() * M_0 / 2
                v_x = (v_x / v_mag) * v_clip
                v_y = (v_y / v_mag) * v_clip
            start_x += v_x
            start_y += v_y
            move_x = int(np.round(start_x))
            move_y = int(np.round(start_y))
            if current_x != move_x or current_y != move_y:
                # This should wait for the mouse polling interval
                self.pyautogui_move_mouse(current_x := move_x, current_y := move_y)

        return current_x, current_y


if __name__ == "__main__":
    mouse = Mouse()
    from geometry import Point

    mouse.move_to((1, 1))
    time.sleep(0.5)
    mouse.move_to(destination=Point(765, 503), mouseSpeed="slowest")
    time.sleep(0.5)
    mouse.move_to(destination=(1, 1), mouseSpeed="slow")
    time.sleep(0.5)
    mouse.move_to(destination=(300, 350), mouseSpeed="medium")
    time.sleep(0.5)
    mouse.move_to(destination=(400, 450), mouseSpeed="fast")
    time.sleep(0.5)
    mouse.move_to(destination=(234, 122), mouseSpeed="fastest")
    time.sleep(0.5)
    mouse.move_rel(0, 100)
    time.sleep(0.5)
    mouse.move_rel(0, 100)
