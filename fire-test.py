from firebase import firebase

firebase = firebase.FirebaseApplication('https://iot-project-c1c1a.firebaseio.com/', None)
myUrl = 'https://iot-project-c1c1a.firebaseio.com/'
data = {"temp":50, "humidity":50}
firebase.patch('/sensor/dht/', data)

