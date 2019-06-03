import re
import sys
import base64


def parse(msg, additionals):

    try:
        from_email = re.findall(r'From: (.)*<(.+)*>', msg)[0][1]
    except:
        sys.exit("Failed to parse the sender's name")

    try:
        to_email = re.findall(r'To: [\S]* <([\S]+)*>', msg)[0]
    except:
        sys.exit("Failed to parse the recipient's name")

    try:
        date = re.findall(r'Date: \w*.*2019', msg)[0]
    except:
        sys.exit("Failed to parse the date")

    try:
        boundary = re.findall(r'boundary="(.+)"', msg)[0]
    except IndexError:
        boundary = ''

    add_reg = re.compile(r"=\?UTF-8\?([BQ])\?(\S+)\?=", re.IGNORECASE)
    add = add_reg.findall(msg)
    res = '\n'
    for i in range(2, len(add) - 1):
        res += base64.b64decode(add[i][1]).decode()
       
    if res == '\n':
        res = '*No theme*'

    subject = res

    if boundary:
        part = msg.split(r'Content-Type: text/plain;')[1]
        text = part.split('\n')[3]
    else:
        mes_parts = msg.split('\r\n\r\n')
        text = mes_parts[1][:-5]

    files = dict()
    names = re.findall(r"filename=[\S]+", msg)
    if boundary:
        if names != []:
            for element in names:
                files[element.split('?')[3]] = base64.b64decode(element.split('?')[3]).decode()

    if files:
        if 'a' in additionals:
            mes_parts = msg.split(boundary)
            for part in mes_parts:
                name = re.findall(r'attachment; filename="(.*)"', part)
                if name:
                    parts = part.split('\r\n')
                    file = ''
                    for i in range(5, len(parts)):
                        if parts[i] != '--':
                            file = file + parts[i]
                    with open(files[name[0].split('?')[3]], "wb") as f:
                        f.write(base64.decodebytes(file.encode()))
    if 's' in additionals:
        print('-' * 35)
        print("From: %s" % str(from_email))
    if 'r' in additionals:
        print('-'*35)
        print("To: %s" % str(to_email))
    if 't' in additionals:
        print('-' * 35)
        print("Letter Theme: %s" % str(subject))
    if 'd' in additionals:
        print('-' * 35)
        print(str(date))
    if 'm' in additionals:
        print('-' * 35)
        if text != '':
            print("Letter text:\n" + base64.b64decode(text).decode())

        else:
            print("Letter text: \n*The text is missing*")
        print('-' * 35)
