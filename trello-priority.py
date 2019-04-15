"""This script checks that tickets in the backlog have an appropriate priority label
It looks for:
- tickets with multiple priority labels
- tickets with no priority label
- tickets with a priority label that doesn't match their column
- tickets with a priority label that isn't one of the standard ones
If it finds a problem it corrects the label and sends a message to the person who made the ticket
It makes a comment on an admin ticket summarising the changes

"""

import requests
import json
import sys

# Key and token from Trello - both needed for authentication
# Once live
"""with open('/home/pi/GitRepos/digipi/creds/trello.env', 'r') as f:
    myKey = f.readline().rstrip('\n')
    myToken = f.readline().rstrip('\n')"""

#For local testing
with open('/Users/alec/Python/Trello/trello.env', 'r') as f:
    myKey = f.readline().rstrip('\n')
    myToken = f.readline().rstrip('\n')


# ID of the 'Maintenance backlog' board
board = '5541fead2c739608a8898ebe'

# IDs of the priority lists
low = '59afb8fed016a6e6416aa34d'
medium = '59ba4d02354c28ed20976905'
high = '57cfe53449efb84da1c2625b'
urgent = '59b00377db3253f74f06b79b'
prioritised = [low, medium, high, urgent]

# Dictionary matching priority columns to their IDs
priorityDict = {'priority: urgent': '59b00377db3253f74f06b79b', 'priority: high': '57cfe53449efb84da1c2625b',
              'priority: medium': '59ba4d02354c28ed20976905', 'priority: low': '59afb8fed016a6e6416aa34d'}

# Dictionary matching priority column IDs to the relevant priority label IDs
# eg the first entry's key is the urgent column ID and its value is the urgent label ID
labelDict = {'59b00377db3253f74f06b79b': '59ba50454ea0be4e74964ad0', '57cfe53449efb84da1c2625b': '565835b7ff1468f0e77d01f9',
              '59ba4d02354c28ed20976905': '59ba50660d7ac45898c20568', '59afb8fed016a6e6416aa34d': '59ba50755a0cafbfaa4248f3'}

# Sign the comment to make clear it's automated, not Alec being a busybody
signature = "\n\nYours inhumanly, Botty McBotFace \n\n (I'm not actually Alec, I just share his face)"

# Functions for doing things on Trello
def getCards(lst):
    """get json of cards from a specific list"""
    url = "https://api.trello.com/1/lists/" + lst + "/cards"
    payload = {'key': myKey, 'token': myToken, 'fields': ['name','labels', 'idList', 'url', 'due']}
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

def checkPriority(column, badCards):
    """Look through a column for priority label problems"""
    cards = getCards(column)
    for card in cards:
        # ignore the blank admin tickets
        if not card['name'].startswith(('Priority ', 'LEAVE THE ONES')):
            person = '@' + str(identifier(card))
            # Get just the pink labels, as they're the ones for marking priority
            labels = [label['name'] for label in card['labels'] if label['color'] == 'pink']

            # add a label to a card that doesn't have one
            if not labels:
                labeller(card, labelDict[card['idList']])
                commenter(card, person + " This had no priority label, so I've added one. Please can you check it's right? Thanks!" + signature)
                badCards.append(str("No priority label: " + card['url']))

            # remove labels if there are more than one, then add one matching column
            elif len(labels) > 1:
                unlabeller(card)
                labeller(card, labelDict[card['idList']])
                commenter(card, person + " This had more than one priority label. I've removed the one that didn't match the priority list, but please can you check? Thanks!" + signature)
                badCards.append(str("More than 1 priority label: " + card['url']))

            else:
                try:
                    # If the label doesn't match the column, remove it and add the right one
                    # Only works if the label matches one of the 4 standard priority ones
                    if priorityDict[labels[0]] != card['idList']:
                        unlabeller(card)
                        labeller(card, labelDict[card['idList']])
                        commenter(card, person + " This card's priority label didn't match the list it's in. I've changed the label to match the list, but please can you check this is right? Thanks!" + signature)
                        badCards.append(str("Priority label didn't match list: " + card['url']))

                # If the label is pink but not one of the 4 standard priority labels, fix it
                except KeyError:
                    unlabeller(card)
                    labeller(card, labelDict[card['idList']])
                    commenter(card, person + " The priority label on this card was weird. I've changed the label to a standard one, but please can you check? Thanks!" + signature)
                    badCards.append(str("Nonstandard priority label: " + card['url']))

def checkDates(column, badCards):
    """Look through a column for tickets missing a due date"""
    cards = getCards(column)
    for card in cards:
        # ignore the blank admin tickets
        if not card['name'].startswith(('Priority ', 'LEAVE THE ONES')):
            person = '@' + str(identifier(card))
            if card['due'] is None:
                #commenter(card, person + " Please could you add a due date to this card? Thanks!" + signature)
                badCards.append(str("No due date: " + card['url']))

def checkSize(column, badCards):
    """Look through a column for cards with no sizing"""
    url = "https://api.trello.com/1/lists/" + column + "/cards?pluginData=true"
    payload = {'key': myKey, 'token': myToken, 'fields': ['name', 'pluginData', 'url']}
    response = requests.get(url, params = payload)
    cards = response.json()
    for card in cards:
        # ignore the blank admin tickets
        if not card['name'].startswith(('Priority ', 'LEAVE THE ONES')):
            person = '@' + str(identifier(card))
            if not card['pluginData']:
                #commenter(card, person + " Please could you size this card? Thanks!" + signature)
                badCards.append(str("Not sized: " + card['url']))



"""REDO THIS SO IT JUST CHECKS IF IT'S MONDAY RATHER THAN USING ARGV"""
def begin():
    """Runs the checker and adds summary to admin ticket"""
    #run the check on each priority column, and add problem cards to a single list
    badCards = []
    try:
        if str(sys.argv[1]) == 'priority':
            for column in prioritised:
                checkPriority(column, badCards)
                
        elif str(sys.argv[1]) == 'date':
            for column in prioritised:
                checkDates(column, badCards)
                
        elif str(sys.argv[1]) == 'size':
            for column in prioritised:
                checkSize(column, badCards)
                
        else:
            print("Command line option not found - please use 'priority' or 'date'")
            
    except IndexError:
        print("Please include a command line parameter saying what to check for.")
        print("Currently takes 'priority' and 'date'")        

    # If problem cards found, write a summary of changes on the admin ticket
    # The admin ticket is at https://trello.com/c/BJSsaiRh/2712-automated-reports-on-cards-with-priority-label-errors
    if badCards:
        todo = len(badCards)
        start = 0
        finish = 30
        while todo > 30:
            report = "\n\n".join(badCards[start:finish])
            url = "https://api.trello.com/1/cards/5c66a8959e872641c7a6f5bc/actions/comments"
            payload = {"key": myKey, "token": myToken, "text": report}
            response = requests.request("POST", url, params=payload)
            start += 30
            finish += 30
            todo -= 30
            
        report = "\n\n".join(badCards[start:])
        url = "https://api.trello.com/1/cards/5c66a8959e872641c7a6f5bc/actions/comments"
        payload = {"key": myKey, "token": myToken, "text": report}
        response = requests.request("POST", url, params=payload)

    #print("\n\n".join(badCards))

if __name__ == "__main__":
    begin()
