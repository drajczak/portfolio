import base64
import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import io
import sys

# Ustawienia
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

# Jeśli nie ma autoryzacji, poprosić o nią
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('TenderResults\credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

# Data poszukiwanego raportu
raportDate = "2024-09-30"

# raportDate = input("Podaj datę w formacie RRRR-MM-DD: ")

# ustawienie parametrów wyszukiwania
query = f"subject:'Raport dobowy pełny z dnia {raportDate} - profil Wyniki przetargów'"
userId = 'me'

# łączenie z API Gmail
creds = Credentials.from_authorized_user_file('token.json')
service = build('gmail', 'v1', credentials=creds)

# Inicjalizacja pustego DataFrame
raportmln = pd.DataFrame()

try:
    messages = service.users().messages().list(userId=userId, q=query).execute()
    if 'messages' in messages and messages['messages']:
        message_id = messages['messages'][0]['id']  # pobranie id pierwszej wiadomości
        message = service.users().messages().get(userId=userId, id=message_id).execute()
    else:
        print(f'No messages found for query: {query}')
        message = None
        sys.exit("Stopping script, no reports found for the given date.")
except HttpError as error:
    print(f'An error occurred: {error}')
    message = None
    sys.exit("Stopping script, no reports found for the given date.")

# pobranie załączników
if message and 'payload' in message:
    for part in message['payload'].get('parts', []):
        if part['filename']:
            data = part['body'].get('data')
            if data:
                data = data.encode('utf-8')
                attachment = base64.urlsafe_b64decode(data)
            else:
                att_id = part['body'].get('attachmentId')
                if att_id:
                    attachment = service.users().messages().attachments().get(
                        userId=userId, messageId=message_id, id=att_id).execute()
                    attachment = base64.urlsafe_b64decode(attachment['data'])
                if 'application/vnd.ms-excel' not in part['mimeType']: continue

                # zapisanie załącznika jako DataFrame, z interesującymi mnie kolumnami i nagłówkiem od 8go wiersza
                raport = pd.read_excel(attachment, usecols=["Data dodania", "Przedmiot", "Organizator", "Wartość przetargu", "Wynik"], header=8)

                # tworzę kolumnę z samymi kodami
                raport['ZIP'] = raport['Wynik'].str.extract('(\d\d-\d\d\d)')

                # tworzę kolumnę z samymi NIP
                raport['Wynik'] = raport['Wynik'].str.replace('Krajowy numer identyfikacyjny',
                                                              'Krajowy Numer Identyfikacyjny')

                raport['NIP'] = raport['Wynik'].str.extract('(Krajowy Numer Identyfikacyjny: .+)')
                raport.NIP = raport.NIP.str.extract('(\d{3}.\d{3}.\d{2}.\d{2}|\d+)')

                # tworę kolumnę z województwami
                raport['WZ'] = raport['Wynik'].str.extract('(Województwo: .+)')
                raport['Wojewodztwo_Zwyciezcy'] = raport['WZ'].str.replace('Województwo: ', '')

                # tworzę kolumnę Miasto-Zwyciezcy:

                raport['MZ'] = raport['Wynik'].str.extract('(Miejscowość: .+)')
                raport['Miasto_Zwyciezcy'] = raport['MZ'].str.replace('Miejscowość: ', '')

                # tworzę kolumnę z nazwą zwycięzcy

                raport['Wynik'] = raport['Wynik'].str.replace(
                    '7\.3\.1\) Nazwa \(firma\) wykonawcy, któremu udzielono zamówienia:', 'Oficjalna nazwa:', regex=True)
                raport['Wynik'] = raport['Wynik'].str.replace(
                    '7\.3\.1\) Nazwa \(firma\) wykonawcy, któremu udzielono zamówienie \(dotyczy pełnomocnika\, o którym mowa w art\. 58 ust\. 2 ustawy\): ',
                    'Oficjalna nazwa:', regex=True)
                raport['NZ'] = raport['Wynik'].str.extract('(Oficjalna nazwa:.+)')
                raport['Nazwa_Zwyciezcy'] = raport['NZ'].str.replace('Oficjalna nazwa: ', '', regex=True)

                # #Odfiltrowanie wygranych powyżej 1mln:
                ponadMln = raport[raport['Wartość przetargu'] > 1000000]
                powMln = raport['>Wartość przetargu'] = ponadMln['Wartość przetargu']
                raportmln = raport[['Przedmiot', 'Organizator', '>Wartość przetargu', 'NIP', 'ZIP', 'Wojewodztwo_Zwyciezcy', 'Miasto_Zwyciezcy',
                     'Nazwa_Zwyciezcy', 'Wynik']]

else:
    print("No message found with attachments.")



# Ustawienia wiadomości wychodzącej
to = 'p.klupa@amago.pl, p.kuczborska@amago.pl, k.ochel@amago.pl, a.kubasiak@amago.pl, p.kowalczyk@amago.pl, n.kwiatkowska@amago.pl'
# to = "d.rajczak@amago.pl"
# to = input("Podaj adres e-mail: "
subject = f'Raport wygranych przetargów budowlanych z dnia {raportDate}'

# Tworzenie maila
message = MIMEMultipart()
message['to'] = to
message['subject'] = subject
body = """
<!DOCTYPE html>
<html>
<body>
	<p>Cześć,</p>
	<br>
	<p>Przesyłam raport.</p>
	<br>
	<p>Pozdrawiam,</p>
	<p>--</p>
	<table cellspacing="2" cellpadding="2">
    <tbody>
    <tr>
    <td rowspan="2">
    <p><img src="http://www.amago.pl/wp-content/themes/amago/images/logo.png" width="87" height="106" name="grafika1" align="BOTTOM" border="0" /></p>
    </td>
    <td rowspan="2">
    <p><span>Dominik Rajczak<br /></span>
    <span style="color: gray;">KIEROWNIK DZIAŁU WSPARCIA SPRZEDAŻY /<BR> SALES SUPPORT MANAGER</span></p>
    tel. +48 662 179 004<br />
    e-mail: d.rajczak@amago.pl
    </tr>
    </tbody>
    </table>
    <p style="margin-bottom: 0cm;"><span style="color: #800000;">Cholerzyn 383, 32-060 Liszki;<br /></span>
    <span style="color: #000000;"><font size="2.5">tel. +48 12 687 54 00</span></font></br>
    <span style="color: #000000;"><font size="2">Zarejestrowana w Sądzie Rejonowym dla miasta Kraków-Śródmieście w Krakowie<br /></span><span style="color: #000000;">| KRS 0000110786 | NIP 6792119150 | Regon 351171698 |<br /></span><span style="color: #000000;">Kapitał zakładowy 2 000 000,00 PLN, opłacony w całości</font></span></p>
    <h4 class="western"><span style="color: #000000;">Bądź z nami na bieżąco! </span><a href="http://www.amago.pl" target="_blank" rel="noopener"><span style="color: #800000;">www.amago.pl</span></a></h4>
    <h6 class="western"><span style="color: #000000;">Ta wiadomość i jej treść są zastrzeżone w szczegółowym zakresie dostępnym na </span><a href="http://www.amago.pl/stopka" target="_blank" rel="noopener">http://www.amago.pl/stopka</a>
    <p><span style="color: #000000;">This e-mail and its contents are subject to a DISCLAIMER with important RESERVATIONS: see </span><a href="http://www.amago.pl/stopka" target="_blank" rel="noopener">http://www.amago.pl/stopka</a></h6></p>
</body>
</html>
"""

body = MIMEText(body, 'html')
message.attach(body)

# Tworzenie załącznika
file_name = f'Przefiltrowany raport przetargów z dnia {raportDate}.xlsx'
df_bytes = None

# Tworzenie pliku Excel w pamięci
with io.BytesIO() as output:
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        raportmln.to_excel(writer, index=False)
    # Odczytanie zawartości pliku Excel z obiektu BytesIO
    df_bytes = output.getvalue()

# Ustawianie załącznika w mailu
attachment = MIMEApplication(df_bytes, Name=file_name)
attachment['Content-Disposition'] = f'attachment; filename="{file_name}"'
message.attach(attachment)

try:
    # Wysyłanie maila
    service = build('gmail', 'v1', credentials=creds)
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    send_message = (service.users().messages().send(userId="me", body=create_message).execute())
    print(F'Raport z dnia {raportDate} został wysłany na adres {to}; email Id: {send_message["id"]}')
except HttpError as error:
    print(F'An error occurred: {error}')
    send_message = None
