from tkinter import *
from PIL import ImageTk, Image
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

weather_url = 'https://api.openweathermap.org/data/2.5/weather'
forecast_url = 'https://api.openweathermap.org/data/2.5/forecast'
api_key = '3d8dd4dcab064924e82df504574d2852'
icon_url = 'https://openweathermap.org/img/wn/{}@2x.png'

user_email = None

def getWeather(city):
    params = {'q': city, 'appid': api_key, 'lang': 'tr'}
    data = requests.get(weather_url, params=params).json()
    if data and data.get('cod') == 200:
        city = data['name'].capitalize()
        country = data['sys']['country']
        temp = int(data['main']['temp'] - 273.15)
        icon = data['weather'][0]['icon']
        condition = data['weather'][0]['description'].capitalize()
        wind = data['wind']['speed']
        humidity = data['main']['humidity']
        return (city, country, temp, icon, condition, wind, humidity)
    else:
        return None

def getForecast(city):
    params = {'q': city, 'appid': api_key, 'lang': 'tr', 'cnt': 3}
    data = requests.get(forecast_url, params=params).json()
    if data and data.get('cod') == '200':
        forecast = []
        for item in data['list']:
            date = item['dt_txt'].split()[0]
            temp = int(item['main']['temp'] - 273.15)
            icon = item['weather'][0]['icon']
            condition = item['weather'][0]['description'].capitalize()
            forecast.append((date, temp, icon, condition))
        return forecast
    else:
        return None

def showForecast():
    city = cityEntry.get()
    forecast = getForecast(city)
    if forecast:
        clearLabels()
        forecastText = f"3-Day Forecast for {city.capitalize()}:\n"
        for day in forecast:
            forecastText += f"{day[0]}: {day[1]}\u00b0C, {day[3]}\n"
        locationLabel['text'] = forecastText
    else:
        locationLabel['text'] = "City not found or no forecast data available!"

def sendEmailNotification(subject, body, recipient_email):
    sender_email = "your_email@example.com"
    sender_password = "your_password"
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        server.send_message(msg)
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def setAlarm():
    global user_email
    email_popup = Toplevel(app)
    email_popup.geometry("300x150")
    email_popup.title("Set Email Alarm")
    email_popup.config(bg="#F3F3F3")

    Label(email_popup, text="Enter your email:", font=('Arial', 12), bg="#F3F3F3").pack(pady=10)
    emailEntry = Entry(email_popup, font=('Arial', 12), width=30)
    emailEntry.pack(pady=5)
    emailEntry.focus()

    def saveEmail():
        nonlocal emailEntry, email_popup
        global user_email
        user_email = emailEntry.get()
        if user_email:
            Label(email_popup, text="Email saved successfully!", fg="green", bg="#F3F3F3").pack(pady=10)
        else:
            Label(email_popup, text="Please enter a valid email.", fg="red", bg="#F3F3F3").pack(pady=10)

    Button(email_popup, text="Save", command=saveEmail, bg="#007ACC", fg="white", font=('Arial', 12)).pack(pady=10)

def checkDangerousWeather():
    if user_email:
        dangerous_conditions = ["thunderstorm", "tornado", "extreme rain", "hurricane"]
        city = cityEntry.get()
        weather = getWeather(city)
        if weather and any(cond in weather[4].lower() for cond in dangerous_conditions):
            subject = f"Dangerous Weather Alert: {weather[4]}"
            body = f"Severe weather conditions detected in {weather[0]}:\n\n" \
                   f"Condition: {weather[4]}\nTemperature: {weather[2]}\u00b0C\nWind Speed: {weather[5]} m/s\n" \
                   f"Humidity: {weather[6]}%\n\nStay safe!"
            sendEmailNotification(subject, body, user_email)

def main():
    city = cityEntry.get()
    weather = getWeather(city)
    if weather:
        locationLabel['text'] = '{}, {}'.format(weather[0], weather[1])
        tempLabel['text'] = '{}\u00b0C'.format(weather[2])
        conditionLabel['text'] = weather[4]
        windLabel['text'] = 'Wind: {} m/s'.format(weather[5])
        humidityLabel['text'] = 'Humidity: {}%'.format(weather[6])
        icon = ImageTk.PhotoImage(Image.open(requests.get(icon_url.format(weather[3]), stream=True).raw))
        iconLabel.configure(image=icon)
        iconLabel.image = icon
    else:
        locationLabel['text'] = "City not found!"
        tempLabel['text'] = ""
        conditionLabel['text'] = ""
        windLabel['text'] = ""
        humidityLabel['text'] = ""

def clearLabels():
    locationLabel['text'] = ""
    tempLabel['text'] = ""
    conditionLabel['text'] = ""
    windLabel['text'] = ""
    humidityLabel['text'] = ""
    iconLabel.configure(image='')

app = Tk()
app.geometry('400x700')
app.title('WeathERA')

# Background Color
app.config(bg="#A9D0F5")

# Application Title
titleLabel = Label(app, text="WEATHERA", font=('Helvetica Neue', 25, 'bold'), bg="#A9D0F5", fg="#003366")
titleLabel.pack(pady=10)

cityEntry = Entry(app, justify='center', font=('Arial', 14))
cityEntry.pack(fill=BOTH, ipady=10, ipadx=18, pady=10)
cityEntry.focus()

searchButton = Button(app, text='Get Current Weather', font=('Arial', 12), command=main, bg="#009C95", fg="white", relief=RAISED, bd=3)
searchButton.pack(fill=BOTH, ipady=10, padx=20, pady=5)

# Add "3-Day Forecast" Button
forecastButton = Button(app, text='Get 3-Day Forecast', font=('Arial', 12), command=showForecast, bg="#007ACC", fg="white", relief=RAISED, bd=3)
forecastButton.pack(fill=BOTH, ipady=10, padx=20, pady=5)

# Add Alarm Button
alarmButton = Button(app, text="\u23F0 Set Weather Alarm", font=('Arial', 12), command=setAlarm, bg="#FF4500", fg="white", relief=RAISED, bd=3)
alarmButton.pack(fill=BOTH, ipady=10, padx=20, pady=5)

# Icon Label with Orange Background
iconLabel = Label(app, bg="#FFA500")  # Set the background color to orange
iconLabel.pack(pady=10)
locationLabel = Label(app, font=('Arial', 20, 'bold'), bg="#A9D0F5")
locationLabel.pack()

tempLabel = Label(app, font=('Arial', 40, 'bold'), bg="#A9D0F5")
tempLabel.pack()

conditionLabel = Label(app, font=('Arial', 16), bg="#A9D0F5")
conditionLabel.pack()

windLabel = Label(app, font=('Arial', 10), bg="#A9D0F5")
windLabel.pack()

humidityLabel = Label(app, font=('Arial', 10), bg="#A9D0F5")
humidityLabel.pack()

# Footer with Icons
footerFrame = Frame(app, bg="#A9D0F5")
footerFrame.pack(side=BOTTOM, fill=X, pady=10)

sunIcon = Label(footerFrame, text="☀️", font=('Arial', 20), bg="#A9D0F5")
sunIcon.pack(side=LEFT, padx=20)

cloudIcon = Label(footerFrame, text="☁️", font=('Arial', 20), bg="#A9D0F5")
cloudIcon.pack(side=LEFT, padx=20)

rainIcon = Label(footerFrame, text="🌧️", font=('Arial', 20), bg="#A9D0F5")
rainIcon.pack(side=LEFT, padx=20)

windIcon = Label(footerFrame, text="💨", font=('Arial', 20), bg="#A9D0F5")
windIcon.pack(side=LEFT, padx=20)

app.mainloop()