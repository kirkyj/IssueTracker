from pymongo import MongoClient

def db_connect():

    myClient = MongoClient('localhost', 27017)
    db = myClient.tracker
    issue_db = db.issues

    return issue_db


def main():

    db = db_connect()

    test_entry = {}
    comment1 = {}
    comment2 = {}

    test_entry['name'] = 'Issue1'
    test_entry['id'] = 1
    test_entry['description'] = 'My description of the issues and why it is so bad'
    test_entry['submitter'] = 'marjacks'
    test_entry['date'] = 'today'
    test_entry['state'] = 'new'
    test_entry['severity'] = 'Minor'
    test_entry['prop_res'] = 'Fix the type please!'

    comment1['comment'] = 'This is my first comment'
    comment1['date'] = 'Today'
    comment1['private'] = True

    comment2['comment'] = 'This is my second comment'
    comment2['date'] = 'Today'
    comment2['private'] = False

    test_entry['comments'] = [comment1, comment2]

    test_entry['owner'] = 'marjacks'
    test_entry['impact'] = 'NDcPP v2'
    test_entry['fixed_in'] = 'Version 3'
    test_entry['related'] = 'None'

    db.insert_one(test_entry)

main()

