import re
import requests

import satnogs_webscraper as sw
import numpy as np

def fetch_satnogs(satnogs_id):
    os = sw.observation_scraper.ObservationScraper()
    results = os.scrape_observation(f"https://network.satnogs.org/observations/{satnogs_id}/")

    # store the original waterfall as a bytes array
    waterfall_location = results['Downloads']['waterfall']
    res = requests.get(waterfall_location)
    if res.staus_code == 200:
        original_waterfall = res.content

    # read in the cropped waterfall and create the thresholded waterfall.
    cropped_waterfall_location = results['Downloads']['waterfall_hash_name']
    cropped_waterfall_shape = results['Downloads']['waterfall_shape']

    numpy_image = np.fromfile(cropped_waterfall_location, dtype=np.uint8).reshape(cropped_waterfall_shape)

    threshold = numpy_image.mean() + numpy_image.std() * 1.5
    thresholded_image = numpy_image > threshold

    # clean up the transmitter:
    transmitter = results['Transmitter'].split()
    transmitter = " ".join(transmitter)

    # clean up the frequency:


    return {
        'satnogs_id': results['Observation_id'],
        'satellite_name': results['Satellite'],
        'station_name': results['Station'],
        'status': results['Status'],
        'status_code': results['Status_Message'],
        'transmitter': results[],
        'frequency': results[],
        'original_waterfall': results[],
        'greyscaled_waterfall': results[],
        'thresholded_waterfall': results[],
        'waterfall_length': results[],
        'waterfall_width': results[],

    }