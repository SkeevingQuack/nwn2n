#!/bin/python3
import xml.etree.ElementTree as ET
from sys import argv

class TagError(Exception):
    def __init__(self, tag):
        self.tag = tag



class Message:
    participants = ['Mitchell Budde', 'Michael Holmstrom', 'Jake Fred',
                    'Patsy Lamusga', 'Joshua Pope']

    conversationmap = {'Mitchell Budde':'Budde'}
   
    
    def __init__(self, date, body, contacts, readable):
        self.date = int(date)
        self.body = body
        self.contacts = contacts
        self.readable_date = readable
        self.sender = r"¯\_(ツ)_/¯"

        if contacts in conversationmap:
            self.conversation = conversationmap[contacts]
        else:
            self.conversation = contacts

    def __str__(self):
        output = "{} **{}** ".format(self.readable_date, self.sender)
        if len(body) > 1:
            combined = ', '.join(self.body)
            output += combined
        elif len(body) == 1:
            output += combined
        else:
            raise Exception()
        return output

    def wanted_contacts(self):
        individuals = self.contacts.split(',')
        for name in individuals:
            if name.strip() not in participants:
                return False
        return True
        
    @classmethod
    def from_sms(cls, element):
        date = element.attrib['date']
        body = [element.attrib['body']]
        contacts = element.attrib['contact_name']
        readable = element.attrib['readable_date']
        return cls(date, body, contacts, readable)

    @classmethod
    def from_mms(cls, element):
        date = element.attrib['date']
        readable = element.attrib['readable_date']
        contacts = element.attrib['contact_name']
        body = []
        for part in element.iter('part'):
            if part.attrib['ct'] == 'text/plain':
                body.append(part.attrib['text'])
            else:
                body.append("Attachment: {}".format(part.attrib['ct']))
        return cls(date, body, contacts, readable)

if __name__ == "__main__":
    tree = ET.parse(argv[1])
    root = tree.getroot()

    conversations = {}
    for node in root:
        if node.tag == 'mms':
            message = Message.from_mms(node)
        elif node.tag == 'sms':
            message = Message.from_sms(node)
        else:
            raise TagError(node.tag)

        if not message.wanted_contacts():
            continue
        
        try:
            conversations[message.conversation].append(message)
        except KeyError:
            conversations[message.conversation] = [message]

    with open(argv[2], 'w') as outfile:
        outfile.write("# Converted sms file\n\n")
        for key in conversations:
            outfile.write("## {}\n\n".format(key))
            for message in conversations[key]:
                outfile.write("{}\n\n".format(str(message)))
