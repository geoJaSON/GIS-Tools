##Jason Jordan
##jason.j.jordan@usace.army.mil
##v1.0

from subprocess import check_call
def copy2clip(txt):
    cmd='echo "'+txt+'"|clip'
    return check_call(cmd, shell=True)

print('Enter the following information to generate a Survey123 edit URL. Optional extra parameters can be skipped by pressing <enter>.')
print('*******************************************************************\n')
while True:
    portal = input("Enter number for portal: 1, - NWD, 2- Corpsnet, 3- AGOL, 4 - Partners: ")
    if portal == "1" or portal == "2" or portal == "3" or portal == "4":
        #do some
        break 
    else:
        print('Incorrect input, please try again!')
        

while True:
    item = input("Form Item ID: ")
    if len(item) == 32:
        #do some
        break 
    else:
        print(f'Incorrect input, please try again! (must be 32 characters, input had {len(item)} characters)')
        

while True:
    gidf = input("Global ID field format: 1 -'globalid', 2- 'GLOBALID', 3- 'GlobalID', 4- Other, 5- I'm not Sure: ")
    if gidf == "1" or gidf == "2" or gidf == "3":
        #do some
        break 
    else if:
        gidf == "4":
        gid = input("Enter Global ID field name: ")
        break        
    else:
        print('Incorrect input, please try again!')
        

extra = input("Add extra options to URL? Y- Yes: ")

if extra == "Y" or extra == "y":
    headers =input("Select elements to hide (Can enter multiple numbers): 1- 'Header', 2- 'Footer', 3- 'Nav Bar', 4- 'Leave Warning Box': ")
    w = input("Form width in pixels: ")
    rf = input("Auto re-load form after submit?  Y- Yes: ")
    pp = input("Field to pre-populate (separate field to pre-populate and default value with comma): ")



else:
    headers = ""
    w = ''
    rf = ''
    pp = ''

if gidf == "1":
    gid = '{globalid}'
elif gidf == "2":
    gid = '{GLOBALID}'
elif gidf == "3":
    gid = '{GlobalID}'

 
if portal == '1':
    link = f'https://survey123.arcgis.com/share/{item}?portalUrl=https://geoportal.nwd.usace.army.mil/g0portal&mode=edit&globalId={gid}'
elif portal == '2':
    link = f'https://survey123.arcgis.com/share/{item}?portalUrl=https://arcportal-ucop-corps.usace.army.mil/s0portal&mode=edit&globalId={gid}'
elif portal == '3':
    link = f'https://survey123.arcgis.com/share/{item}?globalId={gid}'
elif portal == '4':
    link = f'https://survey123.arcgis.com/share/{item}?portalUrl=https://arcportal-ucop-partners.usace.army.mil/usaceportal&mode=edit&globalId={gid}'

h = []
if '1' in headers:
    h.append('header')
if '2' in headers:
    h.append('footer')
if '3' in headers:
    h.append('navbar')
if '4' in headers:
    h.append('leaveDialog')
if h:
    h = '&hide=' + ','.join(h)
    link = link + h

if w:
    w = '&width=' + w
    link = link + w

if rf == "Y" or rf == "y":
    rf = '&autoRefresh=true'
    link = link + rf

if pp:
    pp = '&field:' + pp.split(',')[0] + '=' + pp.split(',')[1].lstrip(' ')
    link = link + pp





print('\nLINK TO OPEN SURVEY123 IN EDIT MODE: \n'+link)



 
route = input("\n Press <enter> to copy to clipboard and exit. Press any other key to exit")

if route == '':
    copy2clip(link)
