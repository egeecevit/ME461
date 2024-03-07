import cv2
import numpy as np
import pygame
import sys
import math

class ObstacleDetector:
    def __init__(self, image_path, resize_dimensions=(800, 600), min_contour_area=400, max_distance_from_center=100):
        self.image = cv2.imread(image_path)
        self.image = cv2.resize(self.image, resize_dimensions)
        self.edges = None
        self.contours = None
        self.obstacle_rectangles = []
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
        return self.obstacle_shapes

    def filter_obstacles(self, min_contour_area=300, max_obstacle_width=150, max_obstacle_height=150,
                         min_centroid_x=100, max_centroid_x=700, min_centroid_y=100, max_centroid_y=500):
        middle_x = (max_centroid_x + min_centroid_x) // 2
        middle_y = (max_centroid_y + min_centroid_y) // 2

        for contour in self.contours:
            # Calculate the area of the contour
            area = cv2.contourArea(contour)

            # If the area is greater than the threshold, consider it as a valid obstacle
            if area > min_contour_area:
                # Calculate the centroid of the contour
                M = cv2.moments(contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = 0, 0

                # Check if the centroid is within the specified range
                if min_centroid_x <= cX <= max_centroid_x and min_centroid_y <= cY <= max_centroid_y:
                    # Get the minimum area rectangle for the contour
                    rect = cv2.minAreaRect(contour)

                    # Extract width and height from the rotated rectangle
                    width, height = rect[1]

                    # Check if the width and height are within specified limits
                    if width <= max_obstacle_width and height <= max_obstacle_height:
                        # Calculate the distance from the centroid to the middle of the screen
                        distance = np.sqrt((cX - middle_x) ** 2 + (cY - middle_y) ** 2)

                        # Calculate the normal vector of the contour
                        normal_vector = self.calculate_contour_normal(contour)

                        # Append the specifications of the rotated rectangle along with the distance
                        self.obstacle_rectangles.append((rect, distance, normal_vector))

        # Append the specifications of the rotated rectangle along with the distance and normal vector
        self.obstacle_rectangles.append((rect, distance, normal_vector))

        # Sort the rectangles based on the distance from the middle of the screen
        self.obstacle_rectangles.sort(key=lambda r: r[1])

        # Identify the lowest rectangle as the goal
        if self.obstacle_rectangles:
            self.goal_rectangle = self.obstacle_rectangles[0][0]
            del self.obstacle_rectangles[0]
        return self.obstacle_rectangles

    def calculate_contour_normal(self, contour):
        # Reshape contour points for SVD
        points = contour.reshape(-1, 2).astype(np.float32)

        # Calculate centroid of the contour
        centroid = np.mean(points, axis=0)

        # Subtract centroid to center the points
        centered_points = points - centroid

        # Perform SVD on the centered points
        _, _, vh = np.linalg.svd(centered_points, full_matrices=False)

        # The normal vector is the last row of the V matrix
        normal_vector = vh[-1]

        return normal_vector

    def create_arena(self, window_name='Arena with Obstacles, Goal, and Puck'):
        pygame.init()

        # Set up the display
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption(window_name)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Create a puck with its center at the left middle of the screen (blue circle)
            puck_radius = 20
            puck_color = (255, 0, 0)
            puck_position = (self.puck_center[0] - puck_radius, self.puck_center[1] - puck_radius)
            pygame.draw.circle(screen, puck_color, self.puck_center, puck_radius)

            # Draw the goal rectangle in red
            if self.goal_rectangle:
                goal_box = np.intp(cv2.boxPoints(self.goal_rectangle))
                pygame.draw.polygon(screen, (0, 0, 255), goal_box)

            # Draw filled green rectangles for obstacles
            for rect, _, _ in self.obstacle_rectangles:
                box = np.intp(cv2.boxPoints(rect))
                pygame.draw.polygon(screen, (0, 255, 0), box)

            pygame.display.flip()

        pygame.quit()

    def shoot_puck(self, initial_angle, initial_speed):
        pygame.init()

        # Set up the display
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('Puck Animation')

        # Initial puck state
        puck_radius = 20
        puck_color = (255, 0, 0)
        puck_position = [self.puck_center[0] - puck_radius, self.puck_center[1] - puck_radius]
        puck_velocity = [initial_speed * math.cos(math.radians(initial_angle)),
                        -initial_speed * math.sin(math.radians(initial_angle))]

        clock = pygame.time.Clock()
        dt = 0.1  # Time step for simulation
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Update puck position based on velocity
            puck_position[0] += puck_velocity[0] * dt
            puck_position[1] += puck_velocity[1] * dt

            # Reflect the puck if it hits the walls
            if puck_position[0] < 0 or puck_position[0] + 2 * puck_radius > 800:
                puck_velocity[0] = -puck_velocity[0]

            if puck_position[1] < 0 or puck_position[1] + 2 * puck_radius > 600:
                puck_velocity[1] = -puck_velocity[1]

            # Check for collisions with obstacles
            for rect, _, normal_vector in self.obstacle_rectangles:  # Unpack the normal_vector
                rect_points = cv2.boxPoints(rect)
                rect_points = np.array(rect_points, dtype=np.int32)
                rect_points = rect_points.reshape((-1, 1, 2))
                collision = cv2.pointPolygonTest(rect_points, (puck_position[0] + puck_radius, puck_position[1] + puck_radius), True)

                if collision == 0:  # Collision detected
                    # Calculate the reflection angle using the normal vector
                    incident_angle = np.arctan2(puck_velocity[1], puck_velocity[0])
                    angle_of_normal = np.arctan2(normal_vector[1], normal_vector[0])
                    angle_diff = incident_angle - angle_of_normal
                    reflection_angle = incident_angle + 2 * angle_diff  # Calculate reflection angle

                    # Update puck velocity using the reflection angle
                    puck_velocity = [initial_speed * math.cos(reflection_angle),
                                    initial_speed * math.sin(reflection_angle)]

            # Draw the arena
            screen.fill((0, 0, 0))  # Clear the screen
            pygame.draw.circle(screen, puck_color, (int(puck_position[0] + puck_radius),
                                                int(puck_position[1] + puck_radius)), puck_radius)

            # Draw the goal rectangle in red
            if self.goal_rectangle:
                goal_box = np.intp(cv2.boxPoints(self.goal_rectangle))
                pygame.draw.polygon(screen, (0, 0, 255), goal_box)

            # Draw filled green rectangles for obstacles
            for rect, _, _ in self.obstacle_rectangles:
                box = np.intp(cv2.boxPoints(rect))
                pygame.draw.polygon(screen, (0, 255, 0), box)

            pygame.display.flip()
            clock.tick(30)  # Set the frame rate

        pygame.quit()




# Example usage:
if __name__ == "__main__":
    detector = ObstacleDetector('img2.jpg')
    detector.preprocess_image()
    detector.find_contours()
    detector.filter_obstacles()
    detector.create_arena()
    detector.show_processed_image()

    # Shoot the puck with an initial angle of 45 degrees and initial speed of 100
    detector.shoot_puck(initial_angle=5, initial_speed=100)