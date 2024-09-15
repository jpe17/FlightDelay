import requests
from datetime import datetime, timedelta

# API Information
API_KEY = 'secret'
BASE_URL = 'http://api.aviationstack.com/v1'

def get_delayed_flights():
    """Find flights that are delayed"""
    url = f"{BASE_URL}/flights"
    params = {
        'access_key': API_KEY,
        'flight_status': 'active',
        'limit': 100  # Increase this if needed
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        delayed_flights = [
            flight for flight in data.get('data', [])
            if flight.get('departure', {}).get('delay') is not None
            and int(flight['departure']['delay']) > 0
        ]
        return delayed_flights
    return []

def get_next_flight(flight_iata):
    """Find the next flight for a given aircraft"""
    url = f"{BASE_URL}/flights"
    params = {
        'access_key': API_KEY,
        'flight_iata': flight_iata,
        'limit': 2
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if len(data['data']) > 1:
            return data['data'][1]  # Return the second flight (assuming it's the next one)
    return None

def calculate_potential_delay(delayed_flight, next_flight):
    """Calculate potential delay for the next flight"""
    delayed_arrival = datetime.fromisoformat(delayed_flight['arrival']['estimated'])
    next_departure = datetime.fromisoformat(next_flight['departure']['scheduled'])

    if delayed_arrival > next_departure:
        potential_delay = delayed_arrival - next_departure
        return potential_delay
    return timedelta(0)

def main():
    # Step 1: Find delayed flights
    delayed_flights = get_delayed_flights()
    if not delayed_flights:
        print("No delayed flights found.")
        return

    # Print information about all delayed flights
    for flight in delayed_flights:
        print(f"Delayed flight found: {flight['flight']['iata']}")
        print(f"Delay: {flight['departure']['delay']} minutes")
        print(f"From: {flight['departure']['airport']} To: {flight['arrival']['airport']}")
        print("---")

    # Choose the first delayed flight for further processing
    delayed_flight = delayed_flights[0]

    # Step 2: Find the next flight for that aircraft
    next_flight = get_next_flight(delayed_flight['flight']['iata'])
    if not next_flight:
        print("No next flight found for this aircraft.")
        return


    print(f"Next flight: {next_flight['flight']['iata']}")

    # Step 3: Calculate and output potential delay
    potential_delay = calculate_potential_delay(delayed_flight, next_flight)
    if potential_delay > timedelta(0):
        print(f"Potential delay for next flight: {potential_delay}")
    else:
        print("No potential delay for the next flight.")

if __name__ == "__main__":
    main()