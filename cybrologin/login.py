"""
CYBERROAM 'CLI'ENT
Login client and password manager for cyberroam
"""

import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from getpass import getpass
from base64 import b64encode, b64decode
from random import randint


def checkNet(browser):

    trutitle = "Gateway to your web experience!"
    if browser.title == trutitle:
        print(browser.title)
        return True
    return False


def loginPrompt(usernames, passwords, browser):

    option = loginOptions()
    if option == '1':
        username, password = inputCredentials()
    elif option == '2':
        username, password = selectCredentials(usernames, passwords)
    else:
        username, password = randomCredentials(usernames, passwords)

    login(username, password, browser)

    return username, password


def loginOptions():

    print("Select login option:")
    print("  1. input credentials")
    print("  2. select from saved credentials")
    print("  3. random login")
    option = input("option number: ")
    if option > '0' and option < '4':
        return option
    else:
        print("Invalid input ...")
        loginOptions()


def inputCredentials():

    username = input("username: ")
    password = getpass("password: ")

    return username, password


def selectCredentials(usernames, passwords):

    i = 1
    for username in usernames:
        print('  ' + str(i) + '. ' + username)
        i += 1
    unum = input("user number: ")
    if unum > '0' and unum <= str(len(usernames)):
        return usernames[int(unum)-1], passwords[int(unum)-1]
    else:
        print("Invalid input ...")
        selectCredentials(usernames, passwords)


def randomCredentials(usernames, passwords):

    unum = randint(0, len(usernames))
    print("logging in as " + usernames[unum] + "...")
    return usernames[unum], passwords[unum]


def login(username, password, browser):

    userid = browser.find_element_by_name('username')
    userid.clear()
    userid.send_keys(username)

    pwd = browser.find_element_by_name('password')
    pwd.clear()
    pwd.send_keys(password)

    form = browser.find_element_by_name('frmHTTPClientLogin')
    form.submit()


def loginFail(browser):

    errormsgs = [
            "The system could not log you on. Make sure your password is correct",
            "Your data transfer has been exceeded, Please contact the administrator"
            ]

    msg = browser.find_element_by_id('msgDiv')

    if msg.text in errormsgs:
        print(msg.text)
        return True

    return False


def saveCredentials(username, password):

    userenc = (b64encode(username.encode("utf-8"))).decode("utf-8")
    passenc = (b64encode(password.encode("utf-8"))).decode("utf-8")
    credsfile = open('local/cybrologincreds.txt', 'a')
    credsfile.write(userenc + '!' + passenc + '\n')
    credsfile.close()


if __name__ == '__main__':

    options = Options()
    options.add_argument("--headless")
    browser = webdriver.Firefox(firefox_options=options)
    browser.get('http://172.16.0.30:8090')

    if checkNet(browser):

        usernames = []
        passwords = []

        try:
            with open('local/cybrologincreds.txt', 'r+') as credsfile:
                for line in credsfile:
                    uname, pword = line.split('!')
                    uname = (b64decode(uname.encode("utf-8"))).decode("utf-8")
                    pword = (b64decode(pword[:-1].encode("utf-8"))).decode("utf-8")
                    usernames.append(uname)
                    passwords.append(pword)
                credsfile.close()
        except IOError:
            if not os.path.exists('local'):
                os.mkdir('local')
            credsfile = open('local/cybrologincreds.txt', 'w')
            credsfile.close()

        username, password = loginPrompt(usernames, passwords, browser)
        while loginFail(browser):
            username, password = loginPrompt(usernames, passwords, browser)
        print("Successfully logged in.")
        if username not in usernames:
            saveCredentials(username, password)
    else:
        print("Check network connection.")

    browser.quit()
