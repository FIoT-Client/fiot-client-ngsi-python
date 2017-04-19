var MQTT_HOST = '192.168.99.100'
var API_KEY = '4jggokgpepnvsb2uv4s40d59ov'
var DEVICE_ID = 'UL_LED'

var mqtt = require('mqtt')
var client = mqtt.connect('mqtt://' + MQTT_HOST)

client.on('connect', function() {
  // Subscribes on topic: <apiKey>/<deviceId>/cmd
  topic = '/'+ API_KEY + '/' + DEVICE_ID + '/cmd'
  client.subscribe(topic)
  console.log('Subscribed on topic: ' + topic)
})

client.on('message', function(topic, message) {
  console.log('Incoming message: ' + message.toString())

  command_split = message.toString().split("|")
  device_id_cmd = command_split[0]

  // Answers to topic: <apiKey>/<deviceId>/cmdexe
  ans_topic = topic + 'exe'
  ans_message = device_id_cmd + "|Done"

  console.log('Publishing on topic: ' + ans_topic)
  console.log('Message: ' + ans_message)
  console.log('')

  client.publish(ans_topic, ans_message)
});
