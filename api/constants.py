# -*- coding: utf-8 -*-
# author: Jakub Skałecki (jakub.skalecki@gmail.com)
import csv


def load_nationalities():
    with open('api/country_codes.csv', 'rb') as country_csv:
        reader = csv.reader(country_csv, delimiter=';')
        for row in reader:
            yield unicode(row[1], encoding='utf-8'), unicode(row[0], encoding='utf-8').capitalize()


class NATIONALITIES(object):
    """
    pairs of (CODE, NAME)
    :type CODES: list[(str, str)]
    """
    CODES = list(load_nationalities())
    CODE_TO_NATIONALITY = {code: name for code, name in CODES}


class RELATION_TO_CURRENT_USER(object):
    SEND_INVITE = 'SENT_FRIENDSHIP_INVITE'
    RECEIVED_INVITE = 'RECEIVED_FRIENDSHIP_INVITE'
    FRIEND = 'FRIEND'
    STRANGER = 'STRANGER'


class TEAM_RELATION_TO_CURRENT_USER(object):
    FOUNDER = 'FOUNDER'
    CAPTAIN = 'CAPTAIN'
    INVITED = 'USER_INVITED'
    PROPOSED = 'USER_PROPOSED'
    MEMBER = 'MEMBER'
    STRANGER = 'STRANGER'
