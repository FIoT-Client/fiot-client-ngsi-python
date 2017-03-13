var mqtt = require('mqtt')
var client = mqtt.connect('mqtt://192.168.99.100')

client.on('connect', function() {
  topic = '/4jggokgpepnvsb2uv4s40d59ov/UL_LED/cmd'
  client.subscribe(topic)
  console.log('Subscribed on topic: ' + topic)
})

client.on('message', function(topic, message) {
  // console.log('Topic: ' + topic.toString())
  console.log('Incoming message: ' + message.toString())

  command_split = message.toString().split("|")
  device_id_cmd = command_split[0]

  ans_topic = topic + 'exe'
  ans_message = device_id_cmd + "|Done"

  console.log('Publishing on topic: ' + ans_topic)
  console.log('Message: ' + ans_message)
  console.log('')

  client.publish(ans_topic, ans_message)
});
