import requests
from datetime import datetime, timedelta

# API Information
API_KEY = 'secret'
BASE_URL = 'http://api.aviationstack.com/v1'


def get_flight_data():
    """Get flight data and print summary"""
    url = f"{BASE_URL}/flights"
    params = {
        'access_key': API_KEY,
        'limit': 100  # Maximum allowed for free tier
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        all_flights = data.get('data', [])
        print(f"Total flights fetched: {len(all_flights)}")

        delayed_flights = [
            flight for flight in all_flights
            if flight.get('departure', {}).get('delay') is not None
               and int(flight['departure']['delay']) > 0
        ]

        print(f"Flights with any delay: {len(delayed_flights)}")

        significant_delays = [
            flight for flight in all_flights
            if flight.get('departure', {}).get('delay') is not None
               and int(flight['departure']['delay']) >= 180
        ]

        print(f"Flights delayed by 3 hours or more: {len(significant_delays)}")

        return all_flights, delayed_flights, significant_delays
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
    return [], [], []


def get_next_flight(aircraft_id):
    """Fetch the next flight for a given aircraft ID"""
    url = f"{BASE_URL}/flights"
    params = {
        'access_key': API_KEY,
        'aircraft_icao': aircraft_id,
        'limit': 1,
        'flight_status': 'scheduled'
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        next_flight = data.get('data', [])
        if next_flight:
            return next_flight[0]
    return None


def calculate_delay(departure_time_str, arrival_delay, next_departure_time_str):
    """Calculate the delay between the arrival of the delayed flight and the departure of the next flight"""
    departure_time = datetime.strptime(departure_time_str, "%Y-%m-%dT%H:%M:%S%z")
    arrival_time = departure_time + timedelta(minutes=arrival_delay)
    next_departure_time = datetime.strptime(next_departure_time_str, "%Y-%m-%dT%H:%M:%S%z")

    if arrival_time > next_departure_time:
        delay = arrival_time - next_departure_time
        return delay
    return None


def main():
    all_flights, delayed_flights, significant_delays = get_flight_data()

    if not all_flights:
        print("No flight data retrieved.")
        return

    print("\nExample of a flight record:")
    print(all_flights[0])

    if significant_delays:
        print("\nFlights delayed by 3 hours or more:")
        for flight in significant_delays:
            aircraft_id = flight.get('aircraft', {}).get('icao')
            departure_time = flight['departure']['estimated']
            arrival_delay = int(flight['departure']['delay'])

            print(f"Flight: {flight['flight']['iata']}, Delay: {arrival_delay} minutes, Aircraft ID: {aircraft_id}")

            if aircraft_id and departure_time and arrival_delay:
                next_flight = get_next_flight(aircraft_id)
                if next_flight:
                    next_departure_time = next_flight['departure']['estimated']
                    delay = calculate_delay(departure_time, arrival_delay, next_departure_time)
                    if delay:
                        print(f"Suggested delay for next flight {next_flight['flight']['iata']}: {delay}")
                    else:
                        print(f"No delay for next flight {next_flight['flight']['iata']}")
                else:
                    print(f"No next flight found for aircraft {aircraft_id}")
    else:
        print("\nNo flights delayed by 3 hours or more found in this dataset.")


if __name__ == "__main__":
    main()
