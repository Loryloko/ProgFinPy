from travel_agent_api.config import SERPAPI_API_KEY
from langchain_core.tools import tool
from serpapi import GoogleSearch
from pydantic import BaseModel, Field
from typing import Optional

class FlightsInput(BaseModel):

    departure_airport: str = Field(description="The departure airport code (IATA).")
    arrival_airport: str = Field(description="The arrival airport code (IATA).")
    outbound_date: str = Field(description="The outbound date (YYYY-MM-DD) e.g. 2024-12-13.")
    return_date: str = Field(description="The return date (YYYY-MM-DD) e.g. 2024-12-19.")
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(0, description="The number of children. Defaults to 0.")

class FlightsInputSchema(BaseModel):
    params : FlightsInput

@tool(args_schema=FlightsInputSchema)
def flights_finder(params: FlightsInput):

    """
    This tool uses the SerpApi Google Flights API to retrieve flights info.
    Parameters
        departure_airport (str): The departure airport code (IATA).
        arrival_airport (str): The arrival airport code (IATA).
        outbound_date (str): The outbound date (YYYY-MM-DD) e.g. 2024-12-13.
        return_date (str): The return date (YYYY-MM-DD) e.g. 2024-12-19.
        adults (int): The number of adults. Defaults to 1.
        children (int): The number of children. Defaults to 0.
    Returns:
        dict: A dictionary containing the flights info. If the API call fails, it returns the 
    error message as a string.
    """

    try:
        params = {
            "api_key": SERPAPI_API_KEY,
            "engine": "google_flights",
            "hl": "it",
            "gl": "it",
            "currency": "EUR",
            "stops": "1",
            "departure_id": params.departure_airport,
            "arrival_id": params.arrival_airport,
            "outbound_date": params.outbound_date,
            "return_date": params.return_date,
            "adults" : params.adults,
            "children": params.children
        }

        search = GoogleSearch(params)

        print("*" * 80)
        print("flights_finder")
        print("*" * 80)
        data = search.get_dict()

        # Teniamo solo i campi utili di ogni opzione di volo
        def compatta(opzione):
            return {
                "price": opzione.get("price"),
                "total_duration": opzione.get("total_duration"),
                "flights": [{
                    "airline": f.get("airline"),
                    "flight_number": f.get("flight_number"),
                    "departure": f.get("departure_airport", {}).get("time"),
                    "arrival": f.get("arrival_airport", {}).get("time"),
                    "duration": f.get("duration"),
                } for f in opzione.get("flights", [])],
            }

        risultato = {
            "google_flights_url": data.get("search_metadata", {}).get("google_flights_url"),
            "best_flights": [compatta(o) for o in data.get("best_flights", [])[:3]],
            "other_flights": [compatta(o) for o in data.get("other_flights", [])[:3]],
            "error": data.get("error"),
        }
        print(f"[FLIGHTS] {len(risultato['best_flights'])} migliori + {len(risultato['other_flights'])} altre opzioni")
        return risultato
    except Exception as e:
        print(f"[FLIGHTS] ERRORE: {e}")

        return str(e)