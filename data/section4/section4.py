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
import json

STATE_FILE = 'loop_state.json'

# save place in for loops
def save_state(loop1_iter, loop2_iter, loop3_iter, loop4_iter, loop5_iter):
    state = {
        'download_loop': {
            'loop1_iter': loop1_iter,
            'loop2_iter': loop2_iter,
            'loop3_iter': loop3_iter,
            'loop4_iter': loop4_iter,
            'loop5_iter': loop5_iter,
        }
    }
    with open(STATE_FILE, 'w') as state_file:
        json.dump(state, state_file)

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

data_4 = pd.DataFrame(columns=col_names)

# resume location if needed
# open file for resume location
with open('loop_state.json', 'r') as file:
    content = file.read()

# Parse the JSON content
state_data = json.loads(content)

# Access the values for loop iterations
l1_res = state_data['download_loop']['loop1_iter']
l2_res = state_data['download_loop']['loop2_iter']
l3_res = state_data['download_loop']['loop3_iter']
l4_res = state_data['download_loop']['loop4_iter']
l5_res = state_data['download_loop']['loop5_iter']

print("starting at: ")
print(f"Last iteration on first loop: {l1_res}")
print(f"Last iteration on first loop: {l2_res}")
print(f"Last iteration on first loop: {l3_res}")
print(f"Last iteration on first loop: {l4_res}")
print(f"Last iteration on first loop: {l5_res}")

"""
Scraping the data from HMSS website for section 4 (4.1-4.5) 
"""

base_url = 'https://www.ultrasoundcases.info/'
INIT_URL = "https://www.ultrasoundcases.info/cases/head-and-neck/"
init_soup = request_data(INIT_URL)
first_level = init_soup.find_all("div", {"class": "candidate-filter"})
tgt_path = 'imgs/'
# make sure file directory exists
if not os.path.exists(tgt_path):
    os.makedirs(tgt_path)

# loop counts
l1_i = 0
l2_i = 0
l3_i = 0
l4_i = 0
l5_i = 0

l1_resume = True
l2_resume = True
l3_resume = True
l4_resume = True
l5_resume = True

# go through all first level categories (first level = body system (EX. 4 Head and Neck))
for item_l1 in first_level:
    if (l1_resume == True):
        if (l1_i != l1_res): # not the same place left off, so loop again
            print(f"on loop {l1_i}, looping again until loop {l1_res}")
            l2_i = 0
            l1_i += 1
            continue
        else:
            l1_resume = False
            # get the title from h4>a
            item_l1_title = item_l1.find("h4").find("a").text
            # only fetch section 4 items
            if (item_l1_title != 'Head and Neck'):
                continue
            print('Fetching', item_l1_title)
            
            # get the second level categories
            second_level = item_l1.find("ul").find_all("li")
            l2_i = 0
            l1_i += 1
    else:
        # get the title from h4>a
        item_l1_title = item_l1.find("h4").find("a").text
        # only fetch section 4 items
        if (item_l1_title != 'Head and Neck'):
            continue
        print('Fetching', item_l1_title)
        
        # get the second level categories
        second_level = item_l1.find("ul").find_all("li")
    
    # iterate through each item in the second level (second level = group of body system (EX. 4.1 Thyroid Gland))
    for item_l2 in second_level:
        if (l2_resume == True):
            if (l2_i != l2_res): # not the same place left off, so loop again
                print(f"on loop {l2_i}, looping again until loop {l2_res}")
                l3_i = 0
                l2_i += 1
                continue
            else:
                l2_resume = False
                item_l2_title = item_l2.find("a").text
                item_l2_url_title = item_l2.find("a")['href']
                item_l2_id = item_l2.find("a")["data-id"] 

                print("Fetching", item_l2_title, item_l2_id)

                third_level = requests.get(
                    "https://www.ultrasoundcases.info/api/cases/list/" + str(item_l2_id)
                ).json()
                l3_i = 0
                l2_i += 1
        else:
            item_l2_title = item_l2.find("a").text
            item_l2_url_title = item_l2.find("a")['href']
            item_l2_id = item_l2.find("a")["data-id"] 

            print("Fetching", item_l2_title, item_l2_id)

            third_level = requests.get(
                "https://www.ultrasoundcases.info/api/cases/list/" + str(item_l2_id)
            ).json()
        
        # iterate through each item in the third level (third level = subgroup of group (EX. 4.1.1 Thyroid Congenital Abnormalities))
        for item_l3 in third_level: 
            if (l3_resume == True):
                if (l3_i != l3_res): # not the same place left off, so loop again
                    print(f"on loop {l3_i}, looping again until loop {l3_res}")
                    l4_i = 0
                    l3_i += 1
                    continue
                else:
                    l3_resume = False
                    item_l3_title = item_l3["title"]
                    item_l3_urltitle = item_l3["urltitle"]
                    item_l3_id = item_l3["id"]

                    print("Fetching", item_l3_title, item_l3_id)

                    fourth_level = requests.post(
                        "https://www.ultrasoundcases.info/api/cases/list/" +  str(item_l3_id) + '/',
                        data={"type": "subsubcat"}
                    ).json()
                    l4_i =0
                    l3_i += 1
            else:
                item_l3_title = item_l3["title"]
                item_l3_urltitle = item_l3["urltitle"]
                item_l3_id = item_l3["id"]

                print("Fetching", item_l3_title, item_l3_id)

                fourth_level = requests.post(
                    "https://www.ultrasoundcases.info/api/cases/list/" +  str(item_l3_id) + '/',
                    data={"type": "subsubcat"}
                ).json()

            # iterate through each item in the fourth level (fourth level = specific cases of subgroup (EX. Hypoplasia of the left thyroid lobe))
            for item_l4 in fourth_level:
                if(l4_resume == True):
                    if (l4_i != l4_res): # not the same place left off, so loop again
                        print(f"on loop {l4_i}, looping again until loop {l4_res}")
                        l5_i = 0
                        l4_i += 1
                        continue
                    else:
                        l4_resume = False
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
                        l5_i = 0
                        l4_i += 1
                else:
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
                    if (l5_resume == True):
                        if (l5_i != l5_res): # not the same place left off, so loop again
                            print(f"on loop {l5_i}, looping again until loop {l5_res}")
                            l5_i += 1
                            continue
                        else:
                            l5_resume = False
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
                                data_4.loc[len(data_4.index)] = [item_l2_title, item_l3_title, item_l3_url, item_l4_subtitle, item_l5_img_url, item_l5_img_name, l5_sex, l5_age, l5_body_part]
                            
                                save_state(l1_i, l2_i, l3_i, l4_i, l5_i)
                            l5_i += 1
                    else:
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
                            data_4.loc[len(data_4.index)] = [item_l2_title, item_l3_title, item_l3_url, item_l4_subtitle, item_l5_img_url, item_l5_img_name, l5_sex, l5_age, l5_body_part]
                            
                            save_state(l1_i, l2_i, l3_i, l4_i, l5_i)
                        # at the end of the 2nd else in loop 5
                        l5_i += 1
                l5_i = 0
                l4_i += 1
            l4_i = 0
            l3_i += 1
        l3_i = 0
        l2_i += 1 
    l2_i = 0
    l1_i += 1
print("-------------------FINISHED SECTION 4 DOWNLOAD----------------------")

# write dataframe to csv file
data_4.to_csv('section4/section4.csv', index=False)
