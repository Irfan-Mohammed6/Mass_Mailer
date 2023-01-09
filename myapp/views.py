from asyncio.windows_events import NULL
import email
from http import server
import imp
from tokenize import Number
from urllib import request
from urllib.request import Request
from django.shortcuts import redirect, render
from email.message import EmailMessage
import ssl
import smtplib
import pandas as p
import os
from django.core.files.storage import FileSystemStorage
import re   
from django.contrib import messages

# from django.views.generic import TemplateView
# Create your views here.

def index(request):
    return render(request, 'myapp/index.html')

def verified(request):
    
    context= {}

    #check for the POST method

    if request.method == 'POST':

        #check whether the button to verify is pressed

        if request.POST.get("submittoverify"):

            # recieving and saving the csv file into media folder

            uploaded_file= request.FILES['csv']
            # fs=FileSystemStorage()
            # name= fs.save(uploaded_file.name,uploaded_file)
            # url = fs.url(name)
            # final=os.path.join(os.getcwd(), 'media', name)

            # reading the csv file using pandas and returning error if not a csv

            try:
                # data = p.read_csv(final)
                data = p.read_csv(uploaded_file)
            except:
                messages.info(request, 'Wrong File Type/Not a CSV')
                return redirect ('myapp/index')

            #reading the column "email from the csv file and returning error if no such column is found"
            
            email_col=data.get("email")
            list_of_emails=[]
            try:
                list_of_emails =list(email_col)
            except:
                messages.info(request, 'Incorrect file format, make sure the first coloumn is named ``email``')
                return redirect ('myapp/index')

            #checking if list is empty, if yes then go back to index page
            if not len(list_of_emails):
                messages.info(request, 'File is empty no emails found')
                return redirect ('myapp/index')


            #validating valid and invalid emails using regex and for loop
            #if the email matches the regex pattern the it is appended into valid_mail else its appended to invalid_mail

            valid_mail = []
            invalid_mail = []
            pattern='([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
            for list_ in list_of_emails:
                if re.search(pattern, list_):
                    valid_mail.append(list_)
                else:
                    invalid_mail.append(list_)

            #return the validated emails to the verified page 
            
            return render(request, 'myapp/verified.html', {'valid': valid_mail, 'invalid': invalid_mail})

            #check whether the button to verify is pressed

        elif request.POST.get("submittosend"):

            #get all the values from the form into variables

            sender=request.POST['sender']
            password=request.POST['password']
            subject=request.POST['subject']
            text=request.POST['text']
            validstr=request.POST['validstr']
            invalidstr=request.POST['invalidstr']
            invalid_mail= []
            valid_mail= []

            '''  MULTILINE COMMENT

            So, the list of valid emails and invalid emails is passed 
            to the backend in the form of a string like 
            "['akeelabbas29@gmail.com','mirzariyazahmedbaig@gmail.com']"
            now if the valid or invalid list was empty the string that
            was passed to the backend would look like "[]"


            First, check if the invalid string is not empty (The length of the string would be 2 if empty i.e "[]" )
            then, example, the string is "['akeelabbas29gmail.com','mirzariyazahmedbaig@gmail']"
            we will replace the commas, [, ] and the ' so that we get something like akeelabbas29gmail.com mirzariyazahmedbaig@gmail
            then we split this string and loop through each one of them, to obtain a list like ['akeelabbas29gmail.com','mirzariyazahmedbaig@gmail']
            
            ''' 

            if not(len(invalidstr) == 2):
                invalidstr = invalidstr.replace(',','')
                invalidstr = invalidstr.replace('[','')
                invalidstr = invalidstr.replace(']','')
                invalidstr = invalidstr.replace("'",'')
                for i in invalidstr.split():
                    invalid_mail.append(i)


            #set up the obtained values into context so that we can send them back to the same page with the request when error occurs

            context['sender']=sender
            context['password']=password
            context['subject']=subject
            context['text']=text
            context['invalid']=invalid_mail
            
            #check if the valid str is empty if so set an error and sent back to the same page

            if(len(validstr) == 2):
                context['novalidemailserror']="set"
                return render(request, 'myapp/verified.html', context)
            else:

                '''

                if the valid str is not empty then, 
                example, the string is "['akeelabbas29@gmail.com','mirzariyazahmedbaig@gmail.com']"
                we will replace the commas, [, ] and the ' so that we get something like 
                akeelabbas29@gmail.com mirzariyazahmedbaig@gmail.com
                then we split this string and loop through each one of them and append them to valid_mail, to obtain a list like 
                ['akeelabbas29@gmail.com','mirzariyazahmedbaig@gmail.com']
                
                '''

                validstr = validstr.replace(',','')
                validstr = validstr.replace('[','')
                validstr = validstr.replace(']','')
                validstr = validstr.replace("'",'')
                for j in validstr.split():
                    valid_mail.append(j)

                #setting up valid_mails into context to send back to the front end when error occurs

                context['valid']=valid_mail

                #using EmailMessage() object and then set up from to subject and the body of the email

                em =EmailMessage()
                em["from"]= sender
                em["to"]= valid_mail
                em["subject"]= subject
                em.set_content(text)

                context1 = ssl.create_default_context()
                try:
                    #try to connect with the smtp server if failed set context['nointerneterror']
                    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context1) as smtp:
                        try:
                            #loging in to the server if failed set context['emailloginfail']
                            smtp.login(sender,password)
                        except:
                            context['emailloginfail']="set"
                            return render(request, 'myapp/verified.html', context)
                        try:
                            #send mails using smtp.sendmail() if failed set context['emailsendfail']
                            smtp.sendmail(sender,valid_mail,em.as_string())
                            messages.info(request, 'Emails sent successfully')
                            return redirect ('myapp/index')
                        except:
                            context['emailsendfail']="set"
                            return render(request, 'myapp/verified.html', context)
                except:
                    context['nointerneterror']="set"
                    return render(request, 'myapp/verified.html', context)

    elif request.method == 'GET':

        messages.info(request, 'Upload file to go to validate or send emails')
        return redirect ('myapp/index')