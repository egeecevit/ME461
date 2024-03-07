import cv2
import numpy as np

class ObstacleDetector:

    def __init__(self, image_path, resize_dimensions=(800, 600), min_contour_area=400, max_distance_from_center=100):
        self.image = cv2.imread(image_path)
        self.image = cv2.resize(self.image, resize_dimensions)
        self.edges = None
        self.contours = None
        self.obstacle_shapes = []
        self.goal_rectangle = None
        self.puck_center = (50, resize_dimensions[1] // 2)  # Initial puck center
        self.min_contour_area = min_contour_area
        self.max_distance_from_center = max_distance_from_center

    def show_processed_image(self, window_name='Processed Image'):
        processed_image = self.image.copy()

        for shape, obstacle_info in self.obstacle_shapes:
            if shape == "rectangle":
                rect, _ = obstacle_info
                box = cv2.boxPoints(rect)
                box = np.int_(box)
                cv2.drawContours(processed_image, [box], 0, (0, 255, 0), cv2.FILLED)
            elif shape == "circle":
                (x, y), radius = obstacle_info
                center = (int(x), int(y))
                radius = int(radius)
                if radius > 20:  # Adjust this threshold for big circles
                    cv2.circle(processed_image, center, radius, (0, 0, 255), cv2.FILLED)  # Fill big circles with red
                else:
                    cv2.circle(processed_image, center, radius, (255, 0, 0), cv2.FILLED)  # Fill small circles with blue

        cv2.imshow(window_name, processed_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def preprocess_image(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        self.edges = cv2.Canny(blurred, 50, 150)

    def find_contours(self):
        contours, _ = cv2.findContours(self.edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter contours based on area and distance from the center
        self.contours = [contour for contour in contours if
                        cv2.contourArea(contour) >= self.min_contour_area and
                        self.is_contour_near_center(contour)]

        # Approximate contours with rectangles or circles
        self.obstacle_shapes = []
        for contour in self.contours:
            # Calculate the bounding box of the contour
            x, y, w, h = cv2.boundingRect(contour)

            # Calculate the aspect ratio of the bounding box
            aspect_ratio = float(w) / h

            # If the aspect ratio is close to 1, consider it as a circle
            if 0.7 <= aspect_ratio <= 1.2:
                (x, y), radius = cv2.minEnclosingCircle(contour)
                self.obstacle_shapes.append(("circle", ((x, y), radius)))
            else:
                # Otherwise, consider it as a rectangle
                rect = cv2.minAreaRect(contour)
                print(rect)
                self.obstacle_shapes.append(("rectangle", (rect, 0)))

    def print_obstacles(self):
        print(self.obstacle_shapes)

    def is_contour_near_center(self, contour):
        # Calculate the centroid of the contour
        M = cv2.moments(contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0

        # Calculate the distance from the centroid to the middle of the screen
        middle_x = self.image.shape[1] // 2
        middle_y = self.image.shape[0] // 2
        distance = np.sqrt((cX - middle_x) ** 2 + (cY - middle_y) ** 2)

        # Adjust the distance threshold as needed
        return distance < self.max_distance_from_center

# Example usage:
if __name__ == "__main__":
    detector = ObstacleDetector('imgNew.jpg', max_distance_from_center=500, min_contour_area=100)  # Adjust max_distance_from_center as needed
    detector.preprocess_image()
    detector.find_contours()
    detector.show_processed_image()
    detector.print_obstacles()