import smtplib
import config
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
 

def send_diff_update(differences):
    fromaddr = config.email.FROM
    toaddr = config.email.TO
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "You have a wishlist price change."
     
    body = "<h2>Hey " + config.info.NAME + ".</h2><h3>Item(s) on your Amazon Wishlist had a price drop!</h3><ul>"
    
    for difference in differences:
        body += "<li><a href=\"http://amazon.com/dp/" + difference[1] + "\" target=\"_blank\">" + difference[0] + "</a>. Changed -$" + difference[2] + " to " + difference[3] + ".</li>"
      
    body += "</ul>"
    
    msg.attach(MIMEText(body, 'html'))
     
    server = smtplib.SMTP(config.email.SERVER, config.email.PORT)
    server.starttls()
    server.login(fromaddr, config.email.PASSWD)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
