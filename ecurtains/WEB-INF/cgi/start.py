
#!/usr/bin/env python3

import cgi

def header(title):
    print ("Content-type: text/html\n")
    print ("<HTML>\n<HEAD>\n<TITLE>%s</TITLE>\n</HEAD>\n<BODY>\n" % (title))

def footer():
    print ("</BODY></HTML>")

form = cgi.FieldStorage()
password = "python"

if not form:
    header("ERROR")
    print("<div id=google_translate_element</div>")
    print("<script type='text/javascript'>")
    print("function googleTranslateElementInit() {")
    print("  new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');")
    print("}")
    print("</script>")
    print("")
    print("<script type='text/javascript' src='//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit'></script>")
    print("<h1><hr><center>ERROR</center></hr></h1>")
    print("<hr></hr>")
    print("<h3><center>Please go to the <a href='login.py'>login page</a></center></h3>")
elif form.getvalue('login') != '' and form.getvalue('password') == password:
    header("Ready ...")
    print("<div id='google_translate_element'></div>")
    print("<script type='text/javascript'>")
    print("function googleTranslateElementInit() {")
    print("  new google.translate.TranslateElement({pageLanguage: 'en'}, 'google_translate_element');")
    print("}")
    print("</script>")
    print("")
    print("<script type='text/javascript' src='//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit'></script>")
    print ("<center><hr><H3>Welcome back</H3><hr></center>")
    print (r"""<form><input type="hidden" name="session" value="%s"></form>""" % (form["login"].value))
    print ("<H3><center><a href=cookiesAccept1987.py>continue</a></center></H3>")
    print ("<h6><center><hr><a href='login.py'>Cancel</a></hr></center></h6>")

else:
    header("PASSWORD incorrect")
    print("<h1><hr><center>ERROR</center></hr></h1>")
    print("<hr></hr>")
    print ("<H3><center>Please go <a href='login.py'>back</a> and enter a valid login.</center></H3>")
    print("<p><center>reason: Password incorrect</center></p>")
footer()
