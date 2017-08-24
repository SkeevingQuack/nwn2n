#!/bin/python3
import xml.etree.ElementTree as ET
from sys import argv
import re

#TODO: sanitize smsBackup xml
#TODO: sanitize messages
#TODO: Ensure sorted

class TagError(Exception):
    def __init__(self, tag):
        self.tag = tag

class Message:
    participants = ['Mitchell Budde', 'Michael Holmstrom', 'Jake Fred',
                    'Patsy Lamusga', 'Joshua Pope']

    conversationmap = {'Mitchell Budde':
                           'Budde',
                       'Mitchell Budde, Jake Fred, Patsy Lamusga, Joshua Pope':
                           'Party (old)',
                       'Mitchell Budde, Jake Fred, Patsy Lamusga, Joshua Pope, Michael Homstrom':
                           'Party'}
    
    def __init__(self, date, body, contacts, readable, sender):
        self.date = int(date)
        self.body = map(lambda x:x.replace('\r', ''), body)
        self.contacts = contacts
        self.readable_date = readable
        self.sender = sender

        if contacts in Message.conversationmap:
            self.conversation = Message.conversationmap[contacts]
        else:
            self.conversation = contacts

    def __str__(self):
        output = "{} **{}** ".format(self.readable_date, self.sender)
        output += ', '.join(self.body)
        return output

    def body2html(self):
        output = ""
        for part in self.body:
            part = '<p>' + part + '</p>'
            part = re.sub(r'\n+', '</p><p>', part)
            output += part
        return output

    def wanted_contacts(self):
        individuals = self.contacts.split(',')
        for name in individuals:
            if name.strip() not in Message.participants:
                return False
        return True
        
    @classmethod
    def from_sms(cls, element):
        date = element.attrib['date']
        body = [element.attrib['body']]
        contacts = element.attrib['contact_name']
        readable = element.attrib['readable_date']
        if element.attrib['type'] == '2':
            sender = "Brad"
        elif element.attrib['type'] == '1':
            sender = contacts
        else:
            print(element.attrib['type'])
            raise Exception()
        
        return cls(date, body, contacts, readable, sender)

    @classmethod
    def from_mms(cls, element):
        date = element.attrib['date']
        readable = element.attrib['readable_date']
        contacts = element.attrib['contact_name']
        body = []
        if element.attrib['msg_box'] == '2':
            sender = "Brad"
        else:
            sender = "Someone else"
        
        for part in element.iter('part'):
            if part.attrib['ct'] == 'text/plain':
                body.append(part.attrib['text'])
            else:
                body.append("Attachment: {}".format(part.attrib['ct']))
        return cls(date, body, contacts, readable, sender)

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

            outfile.write('<table>\n  <tr>\n    <th>Date</th>\n    ' +
                          '<th>Sender</th>\n    <th>Message</th>\n  ' +
                          '</tr>\n')
            for message in conversations[key]:
                outfile.write('  <tr>\n' +
                              '    <td>Text</td>\n' +
                              '    <td>' + message.readable_date + '</td>\n' +
                              '    <td>' + message.sender + '</td>\n' +
                              '    <td>' + message.body2html() + '</td>\n  </tr>\n')
            outfile.write('</table>\n')
            
            # outfile.write('| Date | Sender | Message |\n')
            # outfile.write('|------|--------|---------|\n')
            # for message in conversations[key]:
            #     outfile.write("| {} | {} | {} |\n".format(message.readable_date,
            #                                               message.sender,
            #                                               ', '.join(message.body)))
            # outfile.write('\n\n')
