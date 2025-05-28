import yaml
import json

class DmxOption:
  def __init__(self, name, val):
    self.name = name
    self.val = val

class DmxAttribute:
  def get_current(self):
    return self.options[self.state]

  def set_current(self, value):
    if value in self.options:
      self.state = value
    else:
      print(f'{value} is not an option in {self.options}')

  def publish_state(self):
    self.mqttc.publish(self.config['state_topic'], json.dumps(self.state), retain=True)
    print(self.state)

  def publish_config(self):
    self.mqttc.publish(self.config_topic, json.dumps(self.config), retain=True)

  def __init__(self, parent_uid, data, mqttc):
    name = data['name']
    self.options = {}
    self.state = ''
    self.channel = 0
    self.config = {
      "options": []
    }
    self.name = name
    self.mqttc = mqttc
    self.uid = f'{parent_uid}-{name}'
    print(f'[{self.uid}] {data}')
    self.channel = data['channel']
    self.config_topic = f"homeassistant/select/dmx_{self.uid}/config"
    self.config['name'] = f'{parent_uid} {name}'
    self.config['unique_id'] = self.uid
    self.config['command_topic'] = f'dmx/{parent_uid}/attribute/{name}/set'
    self.config['state_topic'] = f'dmx/{parent_uid}/attribute/{name}/state'
    for option in data['options']:
      opt_name = option['name']
      self.options[opt_name] = DmxOption(opt_name, option['value'])
      self.config['options'].append(opt_name)
      if not self.default_state:
        self.default_state = opt_name
      if not self.state:
        self.state = opt_name

    self.publish_config()

class DmxLight:
  def set_state(self, on):
    self.state['state'] = "ON" if on else "OFF"

  def set_rgb(self, r, g, b):
    if 'red' in self.channels or 'green' in self.channels or 'blue' in self.channels:
      self.state['color']['r'] = r
      self.state['color']['g'] = g
      self.state['color']['b'] = b
      self.writer(self.channels['red'], r)
      self.writer(self.channels['green'], g)
      self.writer(self.channels['blue'], b)
    else:
      print(f'RGB is not supported for {self.uid}')

  def set_brightness(self, brightness):
    if 'brightness' in self.channels:
      self.state['brightness'] = brightness
      self.set_state(brightness > 0)
      self.writer(self.channels['brightness'], brightness)
    else:
      print(f'Brightness not supported for {self.uid}')

    if 'red' in self.channels or 'green' in self.channels or 'blue' in self.channels:
      if brightness > 0 and self.state['color']['r'] == 0 and self.state['color']['g'] == 0 and self.state['color']['b'] == 0:
        self.set_rgb(255, 255, 255)

  def update_attribute(self, name):
    cur = self.attributes[name].get_current()
    # self.attributes[name] = cur.name
    self.writer(self.attributes[name].channel, cur.val)

  def set_attribute(self, name, val):
    self.attributes[name].set_current(val)
    self.update_attribute(name)
    self.attributes[name].publish_state()
    self.publish_attributes()

  def publish_state(self):
    topic = self.config['state_topic']
    self.mqttc.publish(topic, json.dumps(self.state), retain=True)
    print(f'[{topic}] {self.state}')

  def publish_attributes(self):
    attrs = {}
    for key, attr in self.attributes.items():
      attrs[key] = attr.get_current().name
    topic = self.config['json_attributes_topic']
    self.mqttc.publish(topic, json.dumps(attrs), retain=True)
    print(f'[{topic}] {attrs}')

  def publish_config(self):
    self.mqttc.publish(self.config_topic, json.dumps(self.config), retain=True)
    print(f'[{self.config_topic}] {self.config}')

  def __init__(self, data, mqttc, writer):
    self.uid = data['name']
    self.mqttc = mqttc
    self.writer = writer
    self.config_topic = f"homeassistant/light/dmx_{self.uid}/config"
    self.config = {
      "schema": "json"
    }
    self.config['name'] = self.uid
    self.config['unique_id'] = self.uid
    self.config['command_topic'] = f'dmx/{self.uid}/set'
    self.config['state_topic'] = f'dmx/{self.uid}/state'
    self.config['json_attributes_topic'] = f'dmx/{self.uid}/attributes'

    self.state = {
      "state": "OFF",
    }

    self.channels = {}
    if 'brightness' in data:
      self.channels['brightness'] = data['brightness']
    if 'red' in data:
      self.channels['red'] = data['red']
    if 'green' in data:
      self.channels['green'] = data['green']
    if 'blue' in data:
      self.channels['blue'] = data['blue']
    if 'brightness' in data:
      self.config['brightness'] = True
      self.state['brightness'] = 0
    if 'red' in data or 'green' in data or 'blue' in data:
      self.config['color_mode'] = True
      self.config['supported_color_modes'] = ['rgb']
      self.state['color_mode'] = 'rgb'
      self.state['color'] = {'r': 255, 'g': 255, 'b': 255}

    self.attributes = {}
    attributes = json.loads(data['attributes'] if 'attributes' in data else '[]')
    for attr in attributes:
      self.attributes[attr['name']] = DmxAttribute(self.uid, attr, mqttc)
      self.update_attribute(attr['name'])

    self.publish_config()
    self.publish_attributes()
    self.publish_state()

    # self.set_attribute('pattern', 'bar')
    # print(f'{uid}: {self.channels} {self.attributes}')

# with open('config.yaml', 'r') as file:
#     data = yaml.safe_load(file)

# def write_byte(num, val):
#   print(f'SET {num} = {val}')

# for key, data in data['options']['lights'].items():
#   light = DmxLight(key, data, False, write_byte)