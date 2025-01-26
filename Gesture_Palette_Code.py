import numpy as np
import cv2
from collections import deque
import ctypes
from tkinter import Tk
from tkinter.filedialog import asksaveasfilename

# Get screen resolution  
user32 = ctypes.windll.user32
screen_res = (user32.GetSystemMetrics(0), user32.GetSystemMetrics(1))

# Convert screen resolution to integers
screen_res = (int(screen_res[0]), int(screen_res[1]))

# Default called trackbar function 
def setValues(x):
    pass

# Creating the trackbars needed for adjusting the marker color
cv2.namedWindow("Color detectors")
cv2.createTrackbar("Upper Hue", "Color detectors", 153, 180, setValues)
cv2.createTrackbar("Upper Saturation", "Color detectors", 255, 255, setValues)
cv2.createTrackbar("Upper Value", "Color detectors", 255, 255, setValues)
cv2.createTrackbar("Lower Hue", "Color detectors", 64, 180, setValues)
cv2.createTrackbar("Lower Saturation", "Color detectors", 72, 255, setValues)
cv2.createTrackbar("Lower Value", "Color detectors", 49, 255, setValues)

# Lists to track points of different colors and the eraser
bpoints = [deque(maxlen=1024)]
gpoints = [deque(maxlen=1024)]
rpoints = [deque(maxlen=1024)]
ypoints = [deque(maxlen=1024)]
eraser_points = [deque(maxlen=1024)]

blue_index = 0
green_index = 0
red_index = 0
yellow_index = 0
eraser_index = 0

# Kernel for dilation
kernel = np.ones((5, 5), np.uint8)
# This creates a kernel of size 5x5 with all elements set to 1. It's used for dilation operations in image processing to grow white regions in a binary image.

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 255, 255)]
colorIndex = 0
eraserMode = False

# Setup canvas with full screen size
button_height = 50
button_width = 80
button_gap = 10
paintWindow = np.ones((screen_res[1], screen_res[0], 3), dtype=np.uint8) * 255
# paintWindow: A white canvas of the same size as the screen resolution.

# Draw buttons and text on canvas
paintWindow = cv2.rectangle(paintWindow, (30, 30), (30 + button_width, 30 + button_height), (0, 0, 0), 2)  # Clear Button
paintWindow = cv2.rectangle(paintWindow, (120, 30), (120 + button_width, 30 + button_height), colors[0], -1)  # Blue Button
paintWindow = cv2.rectangle(paintWindow, (210, 30), (210 + button_width, 30 + button_height), colors[1], -1)  # Green Button
paintWindow = cv2.rectangle(paintWindow, (300, 30), (300 + button_width, 30 + button_height), colors[2], -1)  # Red Button
paintWindow = cv2.rectangle(paintWindow, (390, 30), (390 + button_width, 30 + button_height), colors[3], -1)  # Yellow Button
paintWindow = cv2.rectangle(paintWindow, (480, 30), (480 + button_width, 30 + button_height), (255, 255, 255), -1)  # Eraser Button
paintWindow = cv2.rectangle(paintWindow, (570, 30), (570 + button_width, 30 + button_height), (200, 200, 200), -1)  # Save Button
# cv2.rectangle: Draws rectangles on the canvas to represent different buttons. The parameters specify the top-left and bottom-right corners of the rectangle, the color, and the thickness (or fill if negative).

cv2.putText(paintWindow, "CLEAR", (30 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
cv2.putText(paintWindow, "BLUE", (120 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
cv2.putText(paintWindow, "GREEN", (210 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
cv2.putText(paintWindow, "RED", (300 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
cv2.putText(paintWindow, "YELLOW", (390 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
cv2.putText(paintWindow, "ERASER", (480 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
cv2.putText(paintWindow, "SAVE", (570 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
# cv2.putText: Adds text labels to the buttons. The parameters specify the canvas, text, position, font, font scale, color, thickness, and line type.

cv2.namedWindow('Paint', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Paint', screen_res[0], screen_res[1])
cv2.namedWindow('Tracking', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Tracking', screen_res[0], screen_res[1])
cv2.namedWindow('mask', cv2.WINDOW_NORMAL)
cv2.resizeWindow('mask', screen_res[0], screen_res[1])

# Load the default webcam of PC
cap = cv2.VideoCapture(0)
# gave 0 argument beacause want to capture from camera for infinite amount of time till key is pressed

def remove_points_from_deques(center, radius):
    """ Removes points from all deques that fall within the eraser circle. """
    global bpoints, gpoints, rpoints, ypoints
    
    def is_point_in_circle(point, center, radius):
        return (point[0] - center[0])*2 + (point[1] - center[1])*2 <= radius*2
    
    def remove_points(deques):
        for deq in deques:
            for point in list(deq):
                if is_point_in_circle(point, center, radius):
                    deq.remove(point)
#     This function iterates through each deque in the provided list of deques.
# For each deque, it checks each point to see if it lies within the eraser circle using is_point_in_circle.
# If the point is inside the circle, it removes the point from the deque.
# The list(deq) construct is used to create a copy of the deque's points, allowing modification (removal) of points from the original deque without causing iteration issues.
    remove_points([bpoints[i] for i in range(len(bpoints))])
    remove_points([gpoints[i] for i in range(len(gpoints))])
    remove_points([rpoints[i] for i in range(len(rpoints))])
    remove_points([ypoints[i] for i in range(len(ypoints))])

def save_image(image):
    """ Save the image with a filename prompt. """
    Tk().withdraw()  # Hide the root Tk window
    # This hides the root Tkinter window that would otherwise appear. This is done to ensure that only the file dialog is shown without any additional Tkinter window.
    filename = asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if filename:
        cv2.imwrite(filename, image)
# Tkinter is a standard GUI (Graphical User Interface) library in Python used to create desktop applications. It provides tools and widgets to build graphical interfaces for Python programs. Here’s a breakdown of its main uses and features:
while True:
    # Read frame from camera
    ret, frame = cap.read()
    if not ret:
        break
#     cap.read(): This function reads a frame from the video capture object (cap), which is typically created using cv2.VideoCapture(). It returns two values:
# ret: A boolean indicating whether the frame was successfully read. If ret is False, it means the frame could not be read, and you might be at the end of the video or there could be an issue with the camera.
# frame: The actual frame captured from the video stream. It is a 3D NumPy array representing the image in BGR (Blue, Green, Red) color space.

    # Flip frame horizontally for mirror view
    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Trackbar values
    u_hue = cv2.getTrackbarPos("Upper Hue", "Color detectors")
    u_saturation = cv2.getTrackbarPos("Upper Saturation", "Color detectors")
    u_value = cv2.getTrackbarPos("Upper Value", "Color detectors")
    l_hue = cv2.getTrackbarPos("Lower Hue", "Color detectors")
    l_saturation = cv2.getTrackbarPos("Lower Saturation", "Color detectors")
    l_value = cv2.getTrackbarPos("Lower Value", "Color detectors")
    Upper_hsv = np.array([u_hue, u_saturation, u_value])
    Lower_hsv = np.array([l_hue, l_saturation, l_value])

    # Adding color buttons to live frame
    frame = cv2.rectangle(frame, (30, 30), (30 + button_width, 30 + button_height), (0, 0, 0), 2)  # Clear Button
    frame = cv2.rectangle(frame, (120, 30), (120 + button_width, 30 + button_height), colors[0], -1)  # Blue Button
    frame = cv2.rectangle(frame, (210, 30), (210 + button_width, 30 + button_height), colors[1], -1)  # Green Button
    frame = cv2.rectangle(frame, (300, 30), (300 + button_width, 30 + button_height), colors[2], -1)  # Red Button
    frame = cv2.rectangle(frame, (390, 30), (390 + button_width, 30 + button_height), colors[3], -1)  # Yellow Button
    frame = cv2.rectangle(frame, (480, 30), (480 + button_width, 30 + button_height), (255, 255, 255), -1)  # Eraser Button
        # Continue adding buttons to the live frame
    frame = cv2.rectangle(frame, (570, 30), (570 + button_width, 30 + button_height), (200, 200, 200), -1)  # Save Button

    cv2.putText(frame, "CLEAR", (30 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "BLUE", (120 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "GREEN", (210 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "RED", (300 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "YELLOW", (390 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1, cv2.LINE_AA)
    cv2.putText(frame, "ERASER", (480 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(frame, "SAVE", (570 + 5, 30 + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1, cv2.LINE_AA)

    # Create mask for detecting the pointer
    Mask = cv2.inRange(hsv, Lower_hsv, Upper_hsv)
    Mask = cv2.erode(Mask, kernel, iterations=1)
    Mask = cv2.morphologyEx(Mask, cv2.MORPH_OPEN, kernel)
    Mask = cv2.dilate(Mask, kernel, iterations=1)
    # cv2.inRange(hsv, Lower_hsv, Upper_hsv) creates a binary mask where the pixels within the specified HSV range are set to 255 (white) and all other pixels are set to 0 (black).
    # hsv is the input frame in HSV color space.
    # Lower_hsv and Upper_hsv are the lower and upper bounds of the HSV range for detecting the pointer color.
    # Erosion removes noise by shrinking the white regions in the binary mask.
    # Dilation increases the white regions in the binary mask, making the detected regions more prominent.



    # Find contours in the mask
    cnts, _ = cv2.findContours(Mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None
    # cv2.findContours is used to find the contours in the mask. cv2.RETR_EXTERNAL retrieves only the extreme outer contours, and cv2.CHAIN_APPROX_SIMPLE compresses horizontal, vertical, and diagonal segments to keep only their endpoints.
    if len(cnts) > 0:
        cnt = sorted(cnts, key=cv2.contourArea, reverse=True)[0]
        ((x, y), radius) = cv2.minEnclosingCircle(cnt)
#         Checks if any contours were found.
# Sorts the contours by area in descending order and takes the largest one.
# Finds the minimum enclosing circle for the largest contour and draws it on the frame.
# Calculates the moments of the contour to find its center.
        cv2.circle(frame, (int(x), int(y)), int(radius), (0, 255, 255), 2)
        M = cv2.moments(cnt)
        center = (int(M['m10'] / M['m00']), int(M['m01'] / M['m00']))

        if center[1] <= 80:
            if 30 <= center[0] <= 110:  # Clear Button
                bpoints = [deque(maxlen=1024)]
                gpoints = [deque(maxlen=1024)]
                rpoints = [deque(maxlen=1024)]
                ypoints = [deque(maxlen=1024)]
                eraser_points = [deque(maxlen=1024)]

                blue_index = 0
                green_index = 0
                red_index = 0
                yellow_index = 0
                eraser_index = 0

                paintWindow[:,:,:] = 255
            elif 120 <= center[0] <= 200:
                colorIndex = 0  # Blue
                eraserMode = False
            elif 210 <= center[0] <= 290:
                colorIndex = 1  # Green
                eraserMode = False
            elif 300 <= center[0] <= 380:
                colorIndex = 2  # Red
                eraserMode = False
            elif 390 <= center[0] <= 470:
                colorIndex = 3  # Yellow
                eraserMode = False
            elif 480 <= center[0] <= 560:
                eraserMode = True  # Enable Eraser Mode
            elif 570 <= center[0] <= 650:  # Save Button
                save_image(paintWindow)
        else:
            if eraserMode:
                eraser_points[eraser_index].appendleft(center)
                # Remove points covered by the eraser
                remove_points_from_deques(center, 10)
            elif colorIndex == 0:
                bpoints[blue_index].appendleft(center)
            elif colorIndex == 1:
                gpoints[green_index].appendleft(center)
            elif colorIndex == 2:
                rpoints[red_index].appendleft(center)
            elif colorIndex == 3:
                ypoints[yellow_index].appendleft(center)

    # Append the next deques when nothing is detected to avoid messing up
    else:
        bpoints.append(deque(maxlen=1024))
        blue_index += 1
        gpoints.append(deque(maxlen=1024))
        green_index += 1
        rpoints.append(deque(maxlen=1024))
        red_index += 1
        ypoints.append(deque(maxlen=1024))
        yellow_index += 1
        eraser_points.append(deque(maxlen=1024))
        eraser_index += 1

    # Draw lines of all the colors on the canvas and frame
    points = [bpoints, gpoints, rpoints, ypoints]
    for i in range(len(points)):
        for j in range(len(points[i])):
            for k in range(1, len(points[i][j])):
                if points[i][j][k - 1] is None or points[i][j][k] is None:
                    continue
                cv2.line(frame, points[i][j][k - 1], points[i][j][k], colors[i], 2)
                cv2.line(paintWindow, points[i][j][k - 1], points[i][j][k], colors[i], 2)

    # Draw the eraser on the canvas
    if eraserMode:
        for i in range(len(eraser_points)):
            for j in range(1, len(eraser_points[i])):
                if eraser_points[i][j - 1] is None or eraser_points[i][j] is None:
                    continue
                cv2.circle(paintWindow, eraser_points[i][j], 10, (255, 255, 255), -1)  # Eraser will be a white circle

    # Show all the windows
    cv2.imshow("Tracking", frame)
    cv2.imshow("Paint", paintWindow)
    cv2.imshow("mask", Mask)

    # If the 'q' key is pressed, stop the application 
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and all resources
cap.release()
cv2.destroyAllWindows()
