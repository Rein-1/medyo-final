import numpy as np
import cv2
import time
import threading
import pyttsx3
import geocoder
import openrouteservice

class CaptureDevice(threading.Thread):
    def __init__(self, camera):
        self.camera = camera
        self.frame = None
        super().__init__()
        # Start thread
        self.start()

    def read(self):
        return self.frame
    
    def run(self):
        while True:
            ret, self.frame = self.camera.read()

def get_directions(destination):
    # Replace 'YOUR_API_KEY' with your actual OpenRouteService API key
    api_key = '5b3ce3597851110001cf6248d6ada387de9045e6b8141dafd8018619'

    client = openrouteservice.Client(key=api_key)

    try:
        # Get current location coordinates
        current_location = geocoder.ip('me')
        current_location_coords = [current_location.latlng[1], current_location.latlng[0]]

        # Get the coordinates for the destination (geocoding)
        coords = client.pelias_search(destination)
        if coords and 'features' in coords and coords['features']:
            destination_coords = coords['features'][0]['geometry']['coordinates']

            directions = client.directions(
                coordinates=[current_location_coords, destination_coords],
                profile='foot-walking'
            )
            if directions:
                steps = directions['routes'][0]['segments'][0]['steps']
                engine = pyttsx3.init()
                engine.say("Here are the walking directions to your destination:")
                for step in steps:
                    engine.say(step['instruction'])
                engine.runAndWait()
            else:
                print("Sorry, couldn't find walking directions for that location.")
        else:
            print("Could not find coordinates for the destination.")
    except openrouteservice.exceptions.ApiError as e:
        print("Error occurred:", e)

if __name__ == "__main__":
    destination = input("Enter the destination: ")

    # Object detection code...
    prototxt_path = 'MobileNetSSD_deploy.prototxt.txt'
    model_path = 'MobileNetSSD_deploy.caffemodel'
    min_confidence = 0.2

    classes = ('background', 'aeroplane', 'bicycle', 'bird', 'boat',
               'bottle', 'bus', 'car', 'cat', 'chair',
               'cow', 'diningtable', 'dog', 'horse',
               'motorbike', 'person', 'pottedplant',
               'sheep', 'sofa', 'train', 'tvmonitor')

    np.random.seed(543210)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))

    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)
    cv2cap = cv2.VideoCapture('rtsp://192.168.42.1:8554/stream0')
    cap = CaptureDevice(cv2cap)
    time.sleep(1)

    while True:
        image = cap.read()
        height, width = image.shape[0], image.shape[1]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (960, 540)), 0.007, (300, 300), 130)

        net.setInput(blob)
        detected_objects = net.forward()

        for i in range(detected_objects.shape[2]):
            confidence = detected_objects[0][0][i][2]
            if confidence > min_confidence:
                class_index = int(detected_objects[0, 0, i, 1])
                upper_left_x = int(detected_objects[0, 0, i, 3] * width)
                upper_left_y = int(detected_objects[0, 0, i, 4] * height)
                lower_right_x = int(detected_objects[0, 0, i, 5] * width)
                lower_right_y = int(detected_objects[0, 0, i, 6] * height)
                prediction_text = f"{classes[class_index]}: {confidence:.2f}"
                cv2.rectangle(image, (upper_left_x, upper_left_y), (lower_right_x, lower_right_y), colors[class_index], 3)
                cv2.putText(image, prediction_text, (upper_left_x, upper_left_y - 15 if upper_left_y > 30 else upper_left_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, colors[class_index], 2)
        
        cv2.imshow("Detected Objects", cv2.resize(image, (960, 540)))
        cv2.waitKey(30)

        # Integration point for navigation
        if destination:
            get_directions(destination)

    cv2.destroyAllWindows()
    cap.release()
