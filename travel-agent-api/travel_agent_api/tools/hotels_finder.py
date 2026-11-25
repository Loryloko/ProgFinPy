from travel_agent_api.config import SERPAPI_API_KEY
from langchain_core.tools import tool
from serpapi import GoogleSearch
from pydantic import BaseModel , Field
from typing import Optional
from enum import IntEnum

class HotelClassEnum(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

class HotelsInput(BaseModel):
    q: str = Field(description="Location of the hotel.")
    check_in_date: str = Field(description="The outbound date (YYYY-MM-DD) e.g. 2024-12-13.")
    check_out_date: str = Field(description="The return date (YYYY-MM-DD) e.g. 2024-12-19.")
    adults: Optional[int] = Field(1, description="The number of adults. Defaults to 1.")
    children: Optional[int] = Field(0, description="The number of children. Defaults to 0.")
    hotel_class: Optional[int] = Field(2, description="The hotel class avaible from 2 to 5 . Defaults to 2.")

class HoltesInputSchema(BaseModel):
    params : HotelsInput

@tool(args_schema=HoltesInputSchema)
def hotels_finder(params: HotelsInput):
    """
    This tool uses the SerpApi Google Hotels API to retrieve hotels info.
    Parameters:
        q (str): Location of the hotel.
        check_in_date (str): The outbound date (YYYY-MM-DD) e.g. 2024-12-13.
        check_out_date (str): The return date (YYYY-MM-DD) e.g. 2024-12-19.
        adults (int): The number of adults. Defaults to 1.
        children (int): The number of children. Defaults to 0.
        hotel_class (int): The hotel class available from 2 to 5. Defaults to 2.
    Returns:
        dict: A dictionary containing the hotels info. If the API call fails, it returns the error message as a string.
    """
    params = {
        "api_key": SERPAPI_API_KEY,
        "engine": "google_hotels",
        "hl": "it",
        "gl": "it",
        "currency": "EUR",
        "q": params.q,
        "check_in_date": params.check_in_date,
        "check_out_date": params.check_out_date,
        "adults": params.adults,
        "children": params.children,
        "hotel_class": params.hotel_class,
        "num": 5
    }
    
    try:
        search = GoogleSearch(params)
        data = search.get_dict()
    except Exception as e:
        print(f"[HOTELS] ERRORE: {e}")
        return str(e)

    if "properties" not in data:
        print(f"[HOTELS] nessun risultato: {data.get('error')}")
        return data.get("error", "Nessun hotel trovato")

    results = []
    for h in data["properties"][:5]:
        results.append({
            "name": h.get("name"),
            "description": h.get("description"),
            "rate_per_night": h.get("rate_per_night", {}).get("lowest"),
            "total_rate": h.get("total_rate", {}).get("lowest"),
            "rating": h.get("overall_rating"),
            "hotel_class": h.get("hotel_class"),
            "check_in": h.get("check_in_time"),
            "check_out": h.get("check_out_time"),
            "amenities": h.get("amenities", [])[:6],
            "image": (h.get("images") or [{}])[0].get("thumbnail"),
            "link": h.get("link"),
        })

    print("*" * 80)
    print(f"[HOTELS] trovati {len(results)} hotel")
    print("*" * 80)
    return results