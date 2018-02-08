# Polar beer

Demo app for exploring the [Polar Accesslink API](https://www.polar.com/accesslink-api/).
If you have an activity/heartrate/GPS monitor from Polar, their API allows
access to tons of useful information (listed below).

The plan is to somehow export this data to a real time-series database
(InfluxDB) so that we can do proper queries of the entire time series, to
compute statistics such as: TSS, CTL (chronic training load) and more, and
eventually create a Grafana dashboard with training data (geek overload).

# Usage

1. Create an app on Polar Flow
2. Create files CLIENT_ID, CLIENT_SECRET
3. Run "get_access_token.py", put result in files USER_ID and ACCESS_TOKEN
4. That's as far as we go for now. Stay tuned...

# Modes of operation

* Export a single time series?
* Export EVERYTHING?
* Only download changes?
* API Explorer. FUSE?

## Basic information
* User ID
* Member ID
* Registration date
* First name
* Last name
* Birthdate
* Gender
* Weight
* Height

## Meta information on training

* List of exercises
* Heart rate zones for user

## Exercise data

* Upload time
* Device name
* Start time
* Duration
* Calories estimate
* Distance
* Heart rate average
* Heart rate maximum
* "Training load"
* Sport
* GPS track
* Detailed sport info
* Heart rate zones summary for session
* Raw heartrate samples

## Daily activity

* Summary
* TDEE (total daily energy expenditure)
* Active calories (calories burnt from activities)
* Duration of activities
* Number of steps
* Step samples (count throughout the day)
* Zone samples 
* Sleep

## Physical info

* Weight
* Height
* Maximum heart rate
* Resting heart rate
* Aerobic threshold
* Anaerobic threshold
* VO2 max
