#!/bin/python

import os
import pandas as pd
import urllib.request
import numpy as np 
#import matplotlib.pyplot as plt
#import cv2 as cv
import requests
from bs4 import BeautifulSoup
import urllib.request
from urllib.error import HTTPError

# handle request and return as parsed HTML
def request_data(url):
    """
    Request data from HMSS website and parse with beautifulsoup.
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup

# download one image at a time
def download_imgs(urllink, tgt_path, filename):
    try: 
        # full path: tgt_path + filename
        full_tgt_path = os.path.join(tgt_path, filename)
        # download image to the folder path
        urllib.request.urlretrieve(urllink, full_tgt_path)
        print('{} saved to {}.'.format(filename, full_tgt_path))
        return True
    except HTTPError as e: # exception for the http error (404 not found page)
        print(f"Error downloading image from {urllink}: {e}") 
        return False
    
#col_names = ['group', 'subgroup', 'subgroup url', 'case description', 'img url', 'img name', 'case id/cover img id', 'crop r1', 'crop r2', 'crop col1', 'crop col2', 'tumor type', 'Notes']
col_names = ['group', 'subgroup', 'subgroup url', 'case description', 'img url', 'img name', 'sex', 'age', 'body part']

data_7 = pd.DataFrame(columns=col_names)

"""
Scraping the data from HMSS website for section 7 (7.2-7.5)
"""

base_url = 'https://www.ultrasoundcases.info/'
INIT_URL = "https://www.ultrasoundcases.info/cases/musculo-skeletal-bone-muscle-nerves-and-other-soft-tissues/"
init_soup = request_data(INIT_URL)
first_level = init_soup.find_all("div", {"class": "candidate-filter"})
tgt_path = 'imgs/'
# make sure file directory exists
if not os.path.exists(tgt_path):
    os.makedirs(tgt_path)

# go through all first level categories (first level = body system (EX. 7 Musculoskeletal, bone, muscle, nerves and other soft tissues))
for item_l1 in first_level:
    # get the title from h4>a
    item_l1_title = item_l1.find("h4").find("a").text
    # only fetch section 4 items
    if (item_l1_title != 'Musculoskeletal, bone, muscle, nerves and other soft tissues'):
        continue
    print('Fetching', item_l1_title)
    
    # get the second level categories
    second_level = item_l1.find("ul").find_all("li")
    
    # iterate through each item in the second level (second level = group of body system (EX. 7.2 Muscle))
    for item_l2 in second_level:
        item_l2_title = item_l2.find("a").text
        item_l2_url_title = item_l2.find("a")['href']
        item_l2_id = item_l2.find("a")["data-id"] 
        
        # skip section 7.1
        if item_l2_title == '7.1 Bone':
            continue

        print("Fetching", item_l2_title, item_l2_id)

        third_level = requests.get(
            "https://www.ultrasoundcases.info/api/cases/list/" + str(item_l2_id)
        ).json()
        
        # iterate through each item in the third level (third level = subgroup of group (EX. 7.2.1 Muscle ruptures lower extremity upper leg))
        for item_l3 in third_level: 
            item_l3_title = item_l3["title"]
            item_l3_urltitle = item_l3["urltitle"]
            item_l3_id = item_l3["id"]

            print("Fetching", item_l3_title, item_l3_id)

            fourth_level = requests.post(
                "https://www.ultrasoundcases.info/api/cases/list/" +  str(item_l3_id) + '/',
                data={"type": "subsubcat"}
            ).json()

            # iterate through each item in the fourth level (fourth level = specific cases of subgroup (EX. Lower extremety: upper leg))
            for item_l4 in fourth_level:
                item_l4_id = item_l4['id']
                item_l4_title = item_l4['title']
                item_l4_subtitle = item_l4['subtitle']
                item_l4_thumb = item_l4['thumb']
                item_l4_urltitle = item_l4['urltitle']

                print("Fetching", item_l4_title, item_l4_id, item_l4_urltitle)

                item_l5_soup = request_data(
                    "https://www.ultrasoundcases.info/{}/".format(item_l4_urltitle)
                )

                # img information
                fifth_level = item_l5_soup.find("div", {"class": "portfolio"})
                fifth_level = fifth_level.find_all("img")

                # patient details
                l5_details = item_l5_soup.find("div", {"class": "information"})
                l5_h4 = l5_details.find("h4")

                # check if details about case exist
                if(l5_h4.text == 'Details'):
                    l5_patient_info = l5_details.find_all("li")
                    for i, li in enumerate(l5_patient_info):
                        details = ''.join(li.find_all(string=True, recursive=False)).strip()
                        if i == 0:
                            l5_sex = details
                        if i == 1:
                            l5_age = details
                        if i == 2:
                            l5_body_part = details
                else:
                    l5_sex = np.nan
                    l5_age = np.nan
                    l5_body_part = np.nan
                    

                # iterate through each item in the case level (fifth level = image details for the specific case)
                for item_l5 in fifth_level:  # case level
                    item_l5_img_url_src = item_l5["src"]
                    item_l5_img_url = "https://www.ultrasoundcases.info" + item_l5_img_url_src

                    img_soup = request_data(
                        item_l5_img_url
                    )

                    print("Fetching", item_l5_img_url)

                    # prep data for dataframe
                    item_l3_url = base_url + item_l2_url_title + item_l3_urltitle
                    img_name = item_l5_img_url.split('/')
                    item_l5_img_name = img_name[-1]

                    if not (item_l5_img_name.endswith(".jpg")):
                        # not a jpg image, so do not add it, go to the next image
                        continue

                    # download images here
                    if (download_imgs(item_l5_img_url, tgt_path, item_l5_img_name)):
                        # if an image is downloaded
                        # create row for dataframe
                        data_7.loc[len(data_7.index)] = [item_l2_title, item_l3_title, item_l3_url, item_l4_subtitle, item_l5_img_url, item_l5_img_name, l5_sex, l5_age, l5_body_part]


# write dataframe to csv file
data_7.to_csv('section7/section7.csv', index=False)