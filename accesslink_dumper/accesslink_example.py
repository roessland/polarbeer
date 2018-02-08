#!/usr/bin/env python

from __future__ import print_function

from utils import load_config, save_config, pretty_print_json
from accesslink import AccessLink

import requests
from pymongo import MongoClient


try:
    input = raw_input
except NameError:
    pass


CONFIG_FILENAME = "config.yml"


class PolarAccessLinkExample(object):
    """Example application for Polar Open AccessLink v3."""

    def __init__(self):
        self.config = load_config(CONFIG_FILENAME)

        if "access_token" not in self.config:
            print("Authorization is required. Run authorization.py first.")
            return

        self.accesslink = AccessLink(client_id=self.config["client_id"],
                                     client_secret=self.config["client_secret"])

        mongoclient = MongoClient(self.config["mongo_uri"])
        self.db = mongoclient.polarbeer

        self.running = True
        #self.show_menu()
        self.check_available_data()

    def show_menu(self):
        while self.running:
            print("\nChoose an option:\n" +
                  "-----------------------\n" +
                  "1) Get user information\n" +
                  "2) Check available data\n" +
                  "3) Revoke access token\n" +
                  "4) Exit\n" +
                  "5) Register user\n" +
                  "-----------------------")
            self.get_menu_choice()

    def get_menu_choice(self):
        choice = input("> ")
        {
            "1": self.get_user_information,
            "2": self.check_available_data,
            "3": self.revoke_access_token,
            "4": self.exit,
            "5": self.register_user,
        }.get(choice, self.get_menu_choice)()

    def get_user_information(self):
        user_info = self.accesslink.users.get_information(user_id=self.config["user_id"],
                                                          access_token=self.config["access_token"])
        if len(user_info) < 20:
            print("User is probably not registered yet, go do that")

        pretty_print_json(user_info)

    def check_available_data(self):
        """
        Polar uses a transactional model for their API.
        The pull-notifications API endpoint returns a list of items that have
        not yet been retrieved. A maximum of 50 items will be returned.

        These items can then be pulled individually.
        After pulling an item, committing the transaction will permanently
        remove it from the list of pull notifications.
        """
        available_data = self.accesslink.pull_notifications.list()

        if not available_data:
            print("No new data available.")
            return

        for item in available_data["available-user-data"]:
            if item["data-type"] == "EXERCISE":
                self.get_exercises()
            elif item["data-type"] == "ACTIVITY_LOG":
                print("Skipped available data of type ACTIVITY_LOG")
            elif item["data-type"] == "ACTIVITY_SUMMARY":
                self.get_daily_activity()
            elif item["data-type"] == "PHYSICAL_INFORMATION":
                self.get_physical_info()
            else:
                print("Unknown data-type for available data item:", item["data-type"])

    def revoke_access_token(self):
        input("Are you sure you want to revoke the access token?")
        input("REALLY? Press Ctrl+C to exit")
        input("press enter to DO IT")
        self.accesslink.users.delete(user_id=self.config["user_id"],
                                     access_token=self.config["access_token"])

        del self.config["access_token"]
        del self.config["user_id"]
        save_config(self.config, CONFIG_FILENAME)

        print("Access token was successfully revoked.")

        self.exit()

    def exit(self):
        self.running = False

    def register_user(self):
        """
        After getting a valid access token, the client must register itself to
        the user. No data will be returned until this has been done, and no data
        from before the registration will be made available.
        """
        try:
            self.accesslink.users.register(access_token=self.config["access_token"])
        except requests.exceptions.HTTPError as err:
            if err.response.status_code != 409:
                raise err
        print("Client authorized (or already authorized)!")

    def get_exercises(self):
        transaction = self.accesslink.training_data.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])
        if not transaction:
            print("No new exercises available.")
            return

        resource_urls = transaction.list_exercises()["exercises"]

        for url in resource_urls:
            exercise_summary = transaction.get_exercise_summary(url)
            exercise_summary["_id"] = exercise_summary["id"]
            exercise_id = self.db.exercise.save(exercise_summary)

            gpx_data = transaction.get_gpx(url)
            gpx = {"_id": exercise_id, "data": gpx_data}
            self.db.exercise_gpx.save(gpx)

            tcx_data = transaction.get_tcx(url)
            tcx = {"_id": exercise_id, "data": tcx_data}
            self.db.exercise_tcx.save(tcx)

            fit_data = transaction.get_fit(url)
            fit = {"_id": exercise_id, "data": fit_data}
            self.db.exercise_fit.save(fit)

            heart_rate_zones = transaction.get_heart_rate_zones(url)
            heart_rate_zones["_id"] = exercise_id
            self.db.exercise_heart_rate_zones.save(heart_rate_zones)

            available_samples = transaction.get_available_samples(url)
            for samples_url in available_samples["samples"]:
                try:
                    samples_data = transaction.get_samples(samples_url)
                except Exception as e:
                    print(samples_url)
                    print(e)
                    print(samples_data)
                    1/0
                samples_data["_id"] = exercise_id
                self.db.exercise_samples.save(samples_data)

            print("Downloaded exercise id", exercise_id)

        # Temporarily removed all commits to ensure we have a steady
        # flow of items to use for testing
        transaction.commit()

    def get_daily_activity(self):
        transaction = self.accesslink.daily_activity.create_transaction(user_id=self.config["user_id"],
                                                                        access_token=self.config["access_token"])
        if not transaction:
            print("No new daily activity available.")
            return

        resource_urls = transaction.list_activities()["activity-log"]

        for url in resource_urls:
            activity_summary = transaction.get_activity_summary(url)
            activity_summary["_id"] = activity_summary["id"]
            activity_id = self.db.activity.save(activity_summary)

            step_samples = transaction.get_step_samples(url)
            step_samples["_id"] = activity_id
            self.db.activity_step_samples.save(step_samples)

            try:
                zone_samples = transaction.get_zone_samples(url)
            except requests.exceptions.HTTPError as e:
                print(zone_samples)
                print(e)
                print(url)
                print("shit went down")
                1/0

            zone_samples["_id"] = activity_id
            self.db.activity_zone_samples.save(zone_samples)

            print("Downloaded activity data with id", activity_id)

        transaction.commit()

    def get_physical_info(self):
        transaction = self.accesslink.physical_info.create_transaction(user_id=self.config["user_id"],
                                                                       access_token=self.config["access_token"])
        if not transaction:
            print("No new physical information available.")
            return

        resource_urls = transaction.list_physical_infos()["physical-informations"]

        for url in resource_urls:
            physical_info = transaction.get_physical_info(url)
            physical_info["_id"] = physical_info["id"]
            self.db.physical_information.save(physical_info)
            print("Downloaded physical info with id", physical_info["id"])

        transaction.commit()

if __name__ == "__main__":
    PolarAccessLinkExample()
