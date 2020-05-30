import csv

from flask import Flask, render_template, request, redirect

app = Flask(__name__)
print(__name__)


@app.route('/')
def my_home():
    return render_template('./index.html')  # domyślny folder dla render_template to static


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


def write_to_csv(data):
    with open('database.csv', newline='', mode='a') as database:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email,subject,message])


@app.route('/submit_form', methods=['POST', 'GET'])  # wysyłanie wiadomości z poziomu strony
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            return redirect('/thanks.html')
        except:
            return 'Did not save to database'
    else:
        return 'something went wrong'
