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

        print("Checking now...")
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
            print("Error communicating with picarto, retrying in 60 seconds.")
            sleep(60)
            continue

        # Iterate over all servers
        for server in webhooks:
            if server["serverName"] not in creators_seen.keys():
                creators_seen[server["serverName"]] = []

            for creator in server["creators"]:
                # If a creator is online *and* has not already been announced to
                # the server, announce to the server.
                # Otherwise do nothing, if a previously seen creator returns
                # offline, flag them as offline so they'll be announced next
                # time they come online.
                if creator.lower() in online_creators:
                    if creator not in creators_seen[server["serverName"]]:
                        try:
                            if server["roleToMention"]:
                                requests.post(
                                    server["url"],
                                    {
                                        "content": f"@{server['roleToMention']} {creator} has gone live on Picarto\nhttps://picarto.tv/{creator}"
                                    },
                                    timeout=10,
                                )
                            else:
                                requests.post(
                                    server["url"],
                                    {
                                        "content": f"{creator} has gone live on Picarto\nhttps://picarto.tv/{creator}"
                                    },
                                    timeout=10,
                                )

                            creators_seen[server["serverName"]].append(creator)
                            print(f"{creator} now online.")
                        except:
                            error = True
                            print(
                                f"Couldn't reach Discord server {server['serverName']}. Retrying in 60 seconds."
                            )
                else:
                    if creator in creators_seen[server["serverName"]]:
                        creators_seen[server["serverName"]].remove(creator)
                        print("{creator} now offline.")

        if not error:
            print("Check complete.")
            sleep(180)
        else:
            sleep(60)


if __name__ == "__main__":
    main()
