import requests
from bs4 import BeautifulSoup
import re
import os
import random

def Scrape(URL):
    if not URL.startswith("https://whatsonzwift.com/workouts/"):
        return "Invalid URL"
    
    # extract workout name and description
    slug = URL.rstrip('/').split('/')[-1].split('?')[0]
    name = slug[:1].upper() + slug[1:] if slug else slug
    slug = URL.rstrip('/').split('/')[-2].split('?')[0]
    Description = slug[:1].upper() + slug[1:] if slug else slug
    Sport = "bike"

    # fetch HTML
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")

    def to_seconds(token):
        value = int(re.sub(r'\D', '', token))
        if "hour" in token:
            return value * 3600
        elif "min" in token:
            return value * 60
        elif "sec" in token:
            return value
        return 0

    def duration(parsed):
        durations = [parsed if re.search(r'(min|sec|hour)$', parsed) else '0' for parsed in parsed]
        totals = []
        current_total = 0

        for part in durations:
            if part != '0':  # only time tokens
                current_total += to_seconds(part)
            else:
                if current_total > 0:
                    totals.append(str(current_total))
                    current_total = 0

        # catch any leftover time accumulation
        if current_total > 0:
            totals.append(str(current_total))
        return totals

    def first_duration(parsed):
        duration_1 = duration(parsed)[0]
        return f'"{duration_1}"'

    def second_duration(parsed):
        duration_2 = duration(parsed)[-1]
        return f'"{duration_2}"'

    def cadence_value(parsed):
        cadence = ""
        for parsed in parsed:
            if "rpm" in parsed:
                cadence_text = re.sub(r"rpm", "", parsed, flags=re.I)
                cadence = re.sub(r"[^\d]", "", cadence_text)
        return cadence

    def power_values(parsed):
        power = [int(power) for power in parsed if power.isdigit()]
        return power

    def First_power_value(parsed):
        power = power_values(parsed)[0]/100
        return power

    def first_interval_power_value(parsed):
        power = power_values(parsed)[0]/100
        return power

    def Second_power_value(parsed):
        power = power_values(parsed)[-1]/100
        return power

    # find workout steps
    steps = []
    textbars = soup.find_all("div", class_="textbar")
    for div in textbars:
        step_text = div.get_text(separator=" ", strip=True)
        parsed = step_text.split()
        print(parsed) #prints scrapped date before being modified

        # sets if FTP lock if "W" is detected in parsed workout data
        Find_W = [parsed for parsed in parsed if re.search(r'\bW\b', parsed)]
        if Find_W:
            FTP_Lock = "<ftpOverride>100</ftpOverride>"
        else:
            FTP_Lock = ""

        #determine step type
        if "x" in parsed[0]:
            parsed.insert(0, "<IntervalsT Repeat=")
            parsed[1] = str(f'"{re.sub(r"[^\d]", "", parsed[1])}"') #number of repeats
            parsed[2] = str(f' OnDuration={first_duration(parsed)}')
            parsed[3] = str(f' OnPower="{first_interval_power_value(parsed)}"') #Power value
            parsed[4] = str(f' OffDuration={second_duration(parsed)}')
            parsed[5] = str(f' OffPower="{Second_power_value(parsed)}"') #Power value
            parsed.insert(6, '>\n    </IntervalsT>') #adds intervals tag
            parsed = parsed[:7]
            steps.append(parsed) #adds step to list
        elif any("free" in item.lower() for item in parsed):
            parsed.insert(0, "<Freeride Duration=")
            parsed[1] = str(first_duration(parsed))
            parsed[2] = str(f' FlatRoad="0"')
            parsed.insert(3, '>\n    </Freeride>') #adds freeride tag')
            parsed = parsed[:4]
            steps.append(parsed) #adds step to list
        elif any("@" in item.lower() for item in parsed):
            parsed.insert(0, "<SteadyState Duration=")
            parsed[1] = str(first_duration(parsed))
            parsed[2] = str(f' Power="{First_power_value(parsed)}"') #Power value
            if cadence_value(parsed)is not None: 
                parsed[3] = str(f' Cadence="{cadence_value(parsed)}"') #Cadence value
            else:
                parsed[3] = ''
            parsed.insert(4, '>\n    </SteadyState>') #adds steady state tag')
            parsed = parsed[:5]
            steps.append(parsed) #adds step to list
        elif First_power_value(parsed) <= Second_power_value(parsed):
            parsed.insert(0, "<Warmup Duration=") #determines if its a warmup
            parsed[1] = str(first_duration(parsed)) #modify duration to be in seconds and removes text
            parsed[2] = str(f' PowerLow="{First_power_value(parsed)}"') #Power low value
            parsed[3] = str(f' PowerHigh="{Second_power_value(parsed)}"') #Power high value
            if random.choice([True]*6 + [False]*3):
                parsed.insert(4, '>\n    </Warmup>') #adds warmup tag')
            else:
                parsed.insert(4, '>\n    <textevent timeoffset="69" message="YURT!!"/>n    </Warmup>') #adds warmup tag')
            parsed = parsed[:5]
            steps.append(parsed) #adds step to list
        elif First_power_value(parsed) > Second_power_value(parsed):
            parsed.insert(0, "<Cooldown Duration=") #otherwise its a cooldown
            parsed[1] = str(first_duration(parsed))
            parsed[2] = str(f' PowerLow="{First_power_value(parsed)}"') #Power high value
            parsed[3] = str(f' PowerHigh="{Second_power_value(parsed)}"') #Power low value
            parsed.insert(4, '>\n    </Cooldown>') #adds cooldown tag')
            parsed = parsed[:5]
            steps.append(parsed) #adds step to list
    #print(steps)

    # combines step lists into single string and puts seperat steps on new lines
    Workout_steps = ["".join(step) for step in steps if step] # combine each step list into a single string
    Workout_steps = "\n    ".join([f"{step}" for step in Workout_steps]) # creates a new line for each step and adds < > around each step
    #print(Workout_steps)

    # Get current user's home directory
    home = os.path.expanduser("~")

    # Build path to Downloads folder
    downloads_path = os.path.join(home, "Downloads", f"{name}.zwo")

    # create ZWO file
    with open(downloads_path, "w") as f:
        f.write(f"""<?xml version="1.0"?>
<workout_file>
  <author>Zwift</author>
  <name>{name}</name>
  <description>{Description}</description>
  <sportType>{Sport}</sportType>
  <tags>
    <tag>{Description}</tag>
  </tags>
    {FTP_Lock}
  <workout>
    {Workout_steps[0:]:}
  </workout>
</workout_file>
""")
    return f"{name} workout downloaded to downloads folder"

#.ZWO file format reference
#https://github.com/h4l/zwift-workout-file-reference/blob/master/zwift_workout_file_tag_reference.md

#Test URLS
#URL = "https://whatsonzwift.com/workouts/90plus-minutes-to-burn/melange"
#URL = "https://whatsonzwift.com/workouts/ftp-tests/ftp-test-standard"
#URL = "https://whatsonzwift.com/workouts/ftp-tests/ftp-ramp-test"
#URL = "https://whatsonzwift.com/workouts/zwift-academy-tri-2020/bike-1-endurance-strength-development"
#print(Scrape(URL))



