# Mouse Documentation

## move_to()

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

## move_rel()

Use Bezier curve to simulate human-like relative mouse movements.
Args:
    x: x distance to move
    y: y distance to move
    x_var: maxiumum pixel variance that may be added to the x distance (default 0)
    y_var: maxiumum pixel variance that may be added to the y distance (default 0)
Kwargs:
    knotsCount: if right-click menus are being cancelled due to erratic mouse movements,
                try setting this value to 0.

## click()

Clicks on the current mouse position.
Args:
    button: button to click (default left).
    force_delay: whether to force a delay between mouse button presses regardless of the Mouse property.
    check_red_click: whether to check if the click was red (i.e., successful action) (default False).
Returns:
    None, unless check_red_click is True, in which case it returns a boolean indicating
    whether the click was red (i.e., successful action) or not.

## right_click()

Right-clicks on the current mouse position. This is a wrapper for click(button="right").
Args:
    with_delay: whether to add a random delay between mouse down and mouse up (default True).

## __rect_around_point()

Returns a rectangle around a Point with some padding.

## __is_red_click()

Checks if a click was red, indicating a successful action.
Args:
    mouse_pos_from: mouse position before the click.
    mouse_pos_to: mouse position after the click.
Returns:
    True if the click was red, False if the click was yellow.

## __calculate_knots()

Calculate the knots to use in the Bezier curve based on distance.
Args:
    destination: x, y tuple of the destination point.

## __get_mouse_speed()

Converts a text speed to a numeric speed for HumanCurve (targetPoints).

## register_speed()

None

## register_mouse_speed()

None

## get_speed()

None
