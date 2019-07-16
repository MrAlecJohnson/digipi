"""This script checks that tickets in the backlog have appropriate priority labels
For priority labels, it looks for:
- tickets with multiple priority labels
- tickets with no priority label
- tickets with a priority label that doesn't match their column
- tickets with a priority label that isn't one of the standard ones
If it finds a problem it corrects the label and sends a message to the person who made the ticket
It makes a comment on an admin ticket summarising the changes

Once a week it also checks that tickets have sizes and due dates.
If they don't, it leaves a message for the ticket owner
It mentions this on the admin ticket as well

"""

import requests
import json
import datetime

# Key and token from Trello - both needed for authentication
# Once live
with open('/home/pi/GitRepos/digipi/creds/trello.env', 'r') as f:
    myKey = f.readline().rstrip('\n')
    myToken = f.readline().rstrip('\n')

#For local testing
"""with open('/Users/alec/Python/Trello/trello.env', 'r') as f:
    myKey = f.readline().rstrip('\n')
    myToken = f.readline().rstrip('\n')"""

# ID of the 'Maintenance backlog' board
board = '5541fead2c739608a8898ebe'

# IDs of the priority lists
low = '59afb8fed016a6e6416aa34d'
medium = '59ba4d02354c28ed20976905'
high = '57cfe53449efb84da1c2625b'
urgent = '59b00377db3253f74f06b79b'
prioritised = [low, medium, high, urgent]

# Dictionary matching priority columns to their IDs
priorityDict = {'priority: urgent': urgent, 'priority: high': high,
              'priority: medium': medium, 'priority: low': low}

# Dictionary matching priority column IDs to the relevant priority label IDs
# eg the first entry's key is the urgent column ID and its value is the urgent label ID
labelDict = {urgent: '59ba50454ea0be4e74964ad0', high: '565835b7ff1468f0e77d01f9',
              medium: '5d2db44542adf6416ccb10a4', low: '5d2db44b1535fb1cc9c3a06d'}

# Sign the comment to make clear it's automated, not Alec being a busybody
signature = "\n\nYours inhumanly, Botty McBotFace \n\n (I'm not actually Alec, I just share his face)"

# Functions for doing things on Trello
def getCards(lst):
    """get json of cards from a specific list"""
    url = "https://api.trello.com/1/lists/" + lst + "/cards?pluginData=true"
    payload = {'key': myKey, 'token': myToken, 'fields': ['name','labels', 'idList', 'url', 'due', 'pluginData']}
    response = requests.get(url, params = payload)
    return response.json()

def labeller(card, priority):
    """apply a label to a card"""
    url = "https://api.trello.com/1/cards/" + card['id'] + "/idLabels"
    payload = {"key": myKey, "token": myToken, "value": priority}
    response = requests.request("POST", url, params=payload)

def unlabeller(card):
    """remove priority-coloured labels from a card
    use in conjunction with labeller to remove wronguns then add the right one"""
    for label in card['labels']:
        if label['color'] == 'pink':
            url = "https://api.trello.com/1/cards/" + card['id'] + "/idLabels/" + label['id']
            payload = {"key": myKey, "token": myToken}
            response = requests.request("DELETE", url, params=payload)

def commenter(card, text):
    """add a comment to a card"""
    url = "https://api.trello.com/1/cards/" + card['id'] + "/actions/comments"
    payload = {"key": myKey, "token": myToken, "text": text}
    response = requests.request("POST", url, params=payload)

def identifier(card):
    """find the first person to work on the card and return their username
    lets me write an @ message to them in a comment"""
    url = "https://api.trello.com/1/cards/" + card['id'] + "/actions"
    payload = {"key": myKey, "token": myToken, "filter": "all"}
    response = requests.request("GET", url, params=payload)
    return json.loads(response.text)[-1]['memberCreator']['username']

def checkAll(column, badCards):
    """Look through a column for problems with cards. Always checks for
    priority labels and fixes them if wrong or missing. On Mondays, also
    checks that cards are sized and have due dates."""
    cards = getCards(column)
    day = datetime.datetime.today().weekday() # day of week as integer

    for card in cards:
        # ignore the blank admin tickets
        if not card['name'].startswith(('Priority ', 'LEAVE THE ONES')):
            person = '@' + str(identifier(card)) # card owner to @ when replying

            # This is the part that checks due dates and sizes
            if day == 0: # if it's Monday - otherwise doesn't run
                #CHECK DATES
                if card['due'] is None:
                    commenter(card, person + " Please could you add a due date to this card? Thanks!" + signature)
                    badCards['date'].append(str("No due date: " + card['url']))

                #CHECK SIZE
                if not card['pluginData']: # This is where the sizing data lives
                    commenter(card, person + " Please could you size this card? Thanks!" + signature)
                    badCards['size'].append(str("Not sized: " + card['url']))

            #CHECK PRIORITY
            # Get just the pink labels, as they're the ones for marking priority
            labels = [label['name'] for label in card['labels'] if label['color'] == 'pink']

            # add a label to a card that doesn't have one
            if not labels:
                labeller(card, labelDict[card['idList']])
                commenter(card, person + " This had no priority label, so I've added one. Please can you check it's right? Thanks!" + signature)
                badCards['priority'].append(str("No priority label: " + card['url']))

            # remove labels if there are more than one, then add one matching column
            elif len(labels) > 1:
                unlabeller(card)
                labeller(card, labelDict[card['idList']])
                commenter(card, person + " This had more than one priority label. I've removed the one that didn't match the priority list, but please can you check? Thanks!" + signature)
                badCards['priority'].append(str("More than 1 priority label: " + card['url']))

            else:
                try:
                    # If the label doesn't match the column, remove it and add the right one
                    # Only works if the label matches one of the 4 standard priority ones
                    if priorityDict[labels[0]] != card['idList']:
                        unlabeller(card)
                        labeller(card, labelDict[card['idList']])
                        commenter(card, person + " This card's priority label didn't match the list it's in. I've changed the label to match the list, but please can you check this is right? Thanks!" + signature)
                        badCards['priority'].append(str("Priority label didn't match list: " + card['url']))

                # If the label is pink but not one of the 4 standard priority labels, fix it
                except KeyError:
                    unlabeller(card)
                    labeller(card, labelDict[card['idList']])
                    commenter(card, person + " The priority label on this card was weird. I've changed the label to a standard one, but please can you check? Thanks!" + signature)
                    badCards['priority'].append(str("Nonstandard priority label: " + card['url']))

def begin():
    """Runs the checker and adds summary to admin ticket"""
    #make dictionary of problems, then run checks on each column
    badCards = {'date': [], 'priority': [], 'size': []}
    for column in prioritised:
        checkAll(column, badCards)

    # If problem cards found, write a summary of changes on the admin ticket
    # The admin ticket is at https://trello.com/c/BJSsaiRh/2712-automated-reports-on-cards-with-priority-label-errors
    # Split into batches of 25 as there's a length limit on Trello comments
    for lst in badCards.values():
        todo = len(lst)
        start = 0
        finish = 25
        while todo > 25:
            report = "\n\n".join(lst[start:finish])
            url = "https://api.trello.com/1/cards/5c66a8959e872641c7a6f5bc/actions/comments"
            payload = {"key": myKey, "token": myToken, "text": report}
            response = requests.request("POST", url, params=payload)
            start += 25
            finish += 25
            todo -= 25

        # Final comment for any left over after the batches of 30
        report = "\n\n".join(lst[start:])
        url = "https://api.trello.com/1/cards/5c66a8959e872641c7a6f5bc/actions/comments"
        payload = {"key": myKey, "token": myToken, "text": report}
        response = requests.request("POST", url, params=payload)

    # For testing - prints to terminal instead of Trello
    """for item in badCards.items():
        print(f'{item[0]}:')
        print()
        print("\n\n".join(item[1]))"""

if __name__ == "__main__":
    begin()
