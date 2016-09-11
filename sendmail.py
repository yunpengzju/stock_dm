#!/usr/bin/env python
# coding: utf-8

import urllib
import urllib2
import smtplib,sys
from email.mime.text import MIMEText
import datetime

reload(sys)
sys.setdefaultencoding( "utf-8" )

def send_mail(to_list,sub,content):
    # 设置服务器，用户名，口令以及邮箱的后缀
    mail_host="smtp.126.com"
    mail_user="testinglife@126.com"
    mail_pass="jianchi000"
    msg = MIMEText(content,_subtype='plain',_charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = mail_user
    msg['To'] = ";".join(to_list)
    try:
        s = smtplib.SMTP()
        s.connect(mail_host)
        s.login(mail_user,mail_pass)
        s.sendmail(mail_user, to_list, msg.as_string())
        s.close()
        return True
    except Exception, e:
        print str(e)
        return False
if __name__ == '__main__':
    #date = sys.argv[1]
    content = sys.argv[1]
    option = sys.argv[2]
    #produceMsg()
    mailto_list=["iamchenyp@126.com"]
    mail_content = ""
    with open(content, 'r') as f:
        mail_content = f.read()
    #send_mail(mailto_list, sub, content)
    if option == '1':
        send_mail(mailto_list, u'每日回顾'+str(datetime.datetime.now().date()), mail_content)
    else:
        send_mail(mailto_list, u'每日预测'+str(datetime.datetime.now().date()), mail_content)
