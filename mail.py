import smtplib
import config
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.header import Header
from email.utils import formataddr
 

def send_diff_update(differences):
    fromaddr = config.email.FROM
    toaddr = config.email.TO
    msg = MIMEMultipart()
    msg['From'] = formataddr((str(Header(config.email.FROMNAME, "utf-8")), fromaddr))
    msg['To'] = toaddr
    msg['Subject'] = ("Items" if len(differences) > 1 else "An item") + " on your Amazon Wishlist dropped in price."
     
    body = "<html style=\"color:#656565\"><head><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"</head><body style=\"text-align:center;font-family: Sans-Serif;color:#656565;\"><br><div style=\"font-size:20pt;\">Hey, " + config.info.NAME + "</div><div style=\"font-size:15pt;\">" + ("Items" if len(differences) > 1 else "An item")  + " on your wishlist had a price drop.</div><br><table style=\"border-collapse:collapse;border-radius:5px;-moz-border-radius:5px;-webkit-border-radius:5px;background-color:#ececec;font-size:10pt;\" cellpadding=\"10\" width=\"100%\"><tbody>"
    
    i = 1

    for difference in differences:
        if len(differences) == i:
            body += "<tr>"
        else:
            body += "<tr style=\"border-bottom:1px solid #d2d2d2;\">"

        body += "<td align=\"center\" width=\"50%\">" + difference[0] + "</td>"
        body += "<td align=\"center\" style=\"color: red;\">-" + difference[2] + "</td>"
        body += "<td><a href=\"http://amazon.com/dp/" + difference[1] + "\" target=\"_blank\" style=\"text-decoration:none;color:black;padding:4px 10px 4px 10px;background:linear-gradient(#f5dca5, #efc158);border-radius:5px;border:1px solid #a7863b;border-bottom:1px solid #83692f\">" + difference[3] + "</a></td>"
        body += "</tr>"

        i += 1

    body += "</tbody></table></body></html>"
    
    msg.attach(MIMEText(body, 'html'))
     
    server = smtplib.SMTP(config.email.SERVER, config.email.PORT)
    server.starttls()
    server.login(fromaddr, config.email.PASSWD)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
