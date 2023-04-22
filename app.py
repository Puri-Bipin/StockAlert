from flask import Flask, render_template, request, jsonify
import yfinance as yf
from apscheduler.schedulers.background import BackgroundScheduler
from flask_mail import Mail, Message
import requests

# Flask app instance
app = Flask(__name__)

# Configure the mail settings
app.config['MAIL_SERVER'] = 'smtp.mailgun.org'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'postmaster@sandbox77e12abc97b7474788242556346b5643.mailgun.org'
app.config['MAIL_PASSWORD'] = '62bba7b1ac196984a91a178d9f26ec72-181449aa-a8609ef2'

# Initialize the mail instance
mail = Mail(app)

# Set up the background scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')

# Route for handling form submission
@app.route('/submit', methods=['GET','POST'])
def submit():
    print(request.data)

    if request.method == 'POST':
        if request.content_type == 'application/json':
            # Handle JSON data
            data = request.json
            stock_ticker = data.get('stock_ticker')
            price_threshold = data.get('price_threshold')
            frequency = data.get('frequency')
            notification_type = data.get('notification_type')
            email = data.get('email')
        else:
            # Handle form data
            stock_ticker = request.form.get('stock_ticker')
            price_threshold = request.form.get('price_threshold')
            frequency = request.form.get('frequency')
            notification_type = request.form.get('notification_type')
            email = request.form.get('email')
      
        if not price_threshold:
            return jsonify({'status': 'error', 'message': 'Price threshold cannot be empty.'}), 400

        try:
            price_threshold = float(price_threshold)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Price threshold must be a valid number.'}), 400

        if frequency is None:
            return jsonify({'status': 'error', 'message': 'Frequency cannot be empty.'}), 400

        try:
            frequency = int(frequency)
        except ValueError:
            return jsonify({'status': 'error', 'message': 'Frequency must be a valid number.'}), 400

        # Get the stock ticker information
        ticker = yf.Ticker(stock_ticker)
        info = ticker.info
        history = ticker.history(period="1d")

        # Get the current price of the stock
        current_price = info.get('currentPrice', None)
        if current_price is None:
            return jsonify({'status': 'error', 'message': 'Unable to retrieve stock price.'}), 400

        # Set up the scheduler job based on notification type
        if notification_type == 'email':
            scheduler.add_job(send_email, 'interval', args=[email, stock_ticker, price_threshold],
                              minutes=frequency, id=stock_ticker)
        elif notification_type == 'sms':
            pass

        # Check if the current price exceeds the threshold price
        if current_price > price_threshold:
            if notification_type == 'email':
                send_email(email, stock_ticker, price_threshold)
            elif notification_type == 'sms':
                pass

        return jsonify({'status': 'success'})
    else:
        # Handle GET request
        return render_template('submit.html')


# Function to send email notification
def send_email(email_address, stock_ticker, price):
    with app.app_context():
        msg = Message('Stock Alert: ' + stock_ticker, sender='alerts@sandbox77e12abc97b7474788242556346b5643.mailgun.org',
                      recipients=[email_address])
        msg.body = 'The stock price of ' + stock_ticker + ' has exceeded the threshold price of ' + str(price) + '.'
        response = requests.post(
            'https://api.mailgun.net/v3/sandbox77e12abc97b7474788242556346b5643.mailgun.org/messages',
            auth=('api', '60db6c0ccc6cf949f54d2b0c48c3b40f-181449aa-08a5f114'),
            data={'from': 'alerts@sandbox77e12abc97b7474788242556346b5643.mailgun.org',
                  'to': email_address,
                  'subject': 'Stock Alert: ' + stock_ticker,
                  'text': 'The stock price of ' + stock_ticker + ' has exceeded the threshold price of ' + str(price) + '.'})
        print(response.text)

# Route for displaying scheduled jobs
@app.route('/jobs')
def jobs():
    jobs = scheduler.get_jobs()
    job_list = []
    for job in jobs:
        job_list.append({'id': job.id, 'next_run_time': job.next_run_time})
    return jsonify({'jobs': job_list})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
