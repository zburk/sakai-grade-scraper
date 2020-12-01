from SakaiPy import SakaiPy

import time
import smtplib
import os
import json
from dotenv import load_dotenv
load_dotenv()

def main():
    info = {
        'username': os.getenv("SAKAI_USERNAME"),
        'password': os.getenv("SAKAI_PASSSWORD"),
        'baseurl': 'https://sakai.unc.edu'
    }

    sak = SakaiPy.SakaiPy(info)

    all_sites = sak.session.executeRequest(
        type='GET',
        url='/site.json',
        params={
            '_limit': 100
        }
    )

    fall_sites = []
    for site in all_sites['site_collection']:
        if ('props' in site):
            if ('term' in site['props']):
                if (site['props']['term'] == 'Fall 2020'):
                    fall_sites.append(site)

    previous_assignments = {}

    while True:
        sak = SakaiPy.SakaiPy(info)
        for site in fall_sites:
            gradebook = sak.session.executeRequest(
                type='GET',
                url='/gradebook/site/' + site['id'] + '.json'
            )

            if (site['id'] in previous_assignments and previous_assignments[site['id']] != len(gradebook['assignments'])):
                gmail_user = os.getenv("GMAIL_USERNAME")
                gmail_password = os.getenv("GMAIL_PASSWORD")

                sent_from = gmail_user
                to = [os.getenv("GMAIL_USERNAME")]
                subject = 'Grade Posted'
                body = "<pre>" + json.dumps(gradebook['assignments'], indent=4, sort_keys=True) + "</pre>"

                email_text = """\
                From: %s
                To: %s
                Subject: %s

                %s
                """ % (sent_from, ", ".join(to), subject, body)

                try:
                    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                    server.ehlo()
                    server.login(gmail_user, gmail_password)
                    server.sendmail(sent_from, to, email_text)
                    server.close()

                    print('Email sent!')
                except:
                    print('Something went wrong...')

            previous_assignments[site['id']] = len(gradebook['assignments'])

            print(len(gradebook['assignments']))

        time.sleep(60)


if __name__ == "__main__":
    main()