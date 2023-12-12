import pyttsx3
import geocoder
import openrouteservice

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

    if destination:
        get_directions(destination)
