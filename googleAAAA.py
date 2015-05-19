__author__ = 'hwatson'

""" Check if a DNS server for your AS is Blacklisted for google AAAA records.
Google may stop sending AAAA queries to a DNS server if it detects client performance difference between IPv4 and IPv6
This performance difference can be delay, packet loss etc.
This should eventually clear, but it does indicate a possible issue within the AS that could require investigation
"""

import urllib2, re, socket, smtplib
from email.mime.text import MIMEText


class checkBlacklist(object):


    def __new__(self,AS,email=False,me="",you="",smtpserver=""):
        """
        :param AS: Autonomous System e.g. "AS109"
        :param email: set True to send email if issues found
        :param me:  Sender's Email address
        :param you: Recipients' Email address
        :param smtpserver: SMTP Server to send the Email to
        :return: Results returned as a string
        """
        response = urllib2.urlopen('http://www.google.com/intl/en_ALL/ipv6/statistics/data/no_aaaa.txt')
        html = response.read()

        results = []
        list = re.findall(r'.+\s%s\s.+'%AS,html)
        if list:
            results.append ("""Following DNS servers within %s are listed as blackholing AAAA entries for google
http://www.google.com/intl/en_ALL/ipv6/statistics/data/no_aaaa.txt
                  """%AS)
            for item in list:
                # get the IP Address
                itemList = re.split("/", item)
                # Try DNS Lookup
                try:
                    result = "%s %s"%(itemList[0],socket.gethostbyaddr(itemList[0])[0])
                    results.append(result)
                except:
                    result = "%s"%itemList[0]
                    results.append(result)

            # Send email if requested
            if email:
                try:
                    msg = MIMEText("\n".join(results))
                    msg['Subject'] = 'Google AAAA DNS Blacklist'
                    msg['From'] = me
                    msg['To'] = you
                    s = smtplib.SMTP(smtpserver)
                    s.sendmail(me, [you], msg.as_string())
                    s.quit()
                except:
                    results.append("\nEmail Failed to send")

            return "\n".join(results)


# Example entries:
# checkBlacklist(AS='AS6713',email=True,me='sentFromMe@somemailplace.com',you='sentToYou@somemailplace.com',smtpserver='mailserver.someplace.com')
# print checkBlacklist(AS='AS109')

