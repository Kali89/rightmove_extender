import requests
from bs4 import BeautifulSoup
import json
import numpy as np
import re
import time

jumpsize = 24
base = "https://www.rightmove.co.uk"


def parse_results(result):
    t = requests.get(base + result)

    l = BeautifulSoup(t.content, "html.parser")

    images = [e["content"] for e in l.find_all("meta", attrs={"property": "og:image"})]

    property_id = result.split("-")[-1].split(".")[0]
    school_url = base + "/ajax/schools/property/{0}?ageGroupType=primary".format(
        property_id
    )

    z = requests.get(school_url)

    school_json = json.loads(z.content)

    nearest_school = school_json["schools"][0]["distance"]

    location = school_json["propertyLocation"]

    try:
        price_text = l.find("small", attrs={"class": "property-header-qualifier"}).text
    except:
        price_text = ""
    price = re.sub(
        r"\D", "", l.find("p", attrs={"id": "propertyHeaderPrice"}).find("strong").text
    )

    description = l.find("p", attrs={"itemprop": "description"}).text.strip()

    listingHistory = l.find("div", attrs={"class": "listing-history"}).text.strip()

    trains = [
        (
            a.text.strip().split("\n")[0],
            re.findall("\d+\.\d+", a.text.strip().split("\n")[1])[0],
        )
        for a in l.find("ul", attrs={"class": "stations-list"}).find_all("li")
    ]
    results_dict[property_id] = {
        "images": images,
        "school_distance": nearest_school,
        "location": location,
        "price_text": price_text,
        "price": price,
        "description": description,
        "history": listingHistory,
        "trains": trains,
    }
    time.sleep(2)
    return (
        property_id,
        {
            "images": images,
            "school_distance": nearest_school,
            "location": location,
            "price_text": price_text,
            "price": price,
            "description": description,
            "history": listingHistory,
            "trains": trains,
        },
    )


r = requests.get(
    "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=STATION%5E10400&maxBedrooms=6&minBedrooms=3&maxPrice=700000&minPrice=475000&radius=40.0&propertyTypes=detached&secondaryDisplayPropertyType=detachedshouses&mustHave=garden&dontShow=newHome&furnishTypes=&keywords="
)


results_dict = {}

i = 0
while i < 48:
    r = requests.get(
        "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=STATION%5E10400&maxBedrooms=6&minBedrooms=3&maxPrice=700000&minPrice=475000&radius=40.0&propertyTypes=detached&secondaryDisplayPropertyType=detachedshouses&mustHave=garden&dontShow=newHome&furnishTypes=&index={0}&keywords=".format(
            i
        )
    )

    b = BeautifulSoup(r.content, "html.parser")
    results = [
        e["href"]
        for e in b.find_all("a", attrs={"class": "propertyCard-link"}, href=True)
    ]
    parsed_results = dict([parse_results(e) for e in results])
    results_dict.update(parsed_results)
    i += jumpsize
    print("Done {0} many".format(i))
    time.sleep(5)
