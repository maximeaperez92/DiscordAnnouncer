# Picarto Alerts webhooker

import requests
import json
from time import sleep


def main():
    with open("webhooks.json") as f:
        webhooks = json.load(f)["webhooks"]

    creators_seen = {}
    while True:
        error = False
        online_creators = []

        print("Checking Picarto now...")
        try:
            online_creators = [
                creator["name"].lower()
                for creator in json.loads(
                    requests.get(
                        "http://api.picarto.tv/v1/online?adult=true&gaming=true",
                        timeout=10,
                    ).text
                )
            ]
        except:
            print("Error communicating with Picarto, retrying in 60 seconds.")
            sleep(60)
            continue

        # Iterate over all servers
        for server in webhooks:
            server_name = server["serverName"]
            role_id = server["roleIdToMention"]

            if server_name not in creators_seen.keys():
                creators_seen[server_name] = []

            for creator in server["creators"]:

                creator_is_online = creator.lower() in online_creators
                creator_has_been_announced = creator in creators_seen[server_name]

                if creator_is_online:
                    if not creator_has_been_announced:
                        message = f"{creator} has gone live on Picarto\nhttps://picarto.tv/{creator}"
                        try:
                            if role_id:
                                message = f"<@&{role_id}> " + message

                            requests.post(
                                server["url"], {"content": message}, timeout=10
                            )

                            creators_seen[server_name].append(creator)
                            print(f"{creator} now online.")
                        except:
                            error = True
                            print(
                                f"Couldn't reach Discord server {server['serverName']}. Retrying in 60 seconds."
                            )
                else:
                    if creator_has_been_announced:
                        creators_seen[server_name].remove(creator)
                        print("{creator} now offline.")

        if not error:
            print("Check complete.")
            sleep(180)
        else:
            sleep(60)


if __name__ == "__main__":
    main()
