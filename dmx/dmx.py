import yaml

class DmxOption:
  def __init__(self, name, val):
    self.name = name
    self.val = val

class DmxAttribute:
  options = {}
  state = ''
  channel = 0

  config = {
    "options": []
  }

  def get_current(self):
    return self.options[self.state]

  def set_current(self, value):
    self.state = value

  def publish_state(self):
    if self.mqttc: self.mqttc.publish(self.config['state_topic'], json.dumps(self.state), retain=True)
    else: print(self.state)

  def publish_config(self):
    self.mqttc.publish(self.config_topic, json.dumps(self.config), retain=True)

  def __init__(self, parent_uid, data, mqttc):
    name = data['name']
    self.name = name
    self.mqttc = mqttc
    self.uid = f'{parent_uid}-{name}'
    self.channel = data['channel']
    self.config_topic = f"homeassistant/select/dmx_{self.uid}/config"
    self.config['name'] = f'{parent_uid} {name}'
    self.config['unique_id'] = self.uid
    self.config['command_topic'] = f'dmx/{self.uid}/set'
    self.config['state_topic'] = f'dmx/{self.uid}/state'
    for option in data['options']:
      opt_name = option['name']
      self.options[opt_name] = DmxOption(opt_name, option['value'])
      self.config['options'].append(opt_name)
      if not self.state:
        self.state = opt_name

    if self.mqttc: self.publish_config()
    else: print(self.config)

class DmxLight:
  channels = {}
  attributes = {}

  state = {
    "state": "OFF",
  }

  config = {
    "schema": "json"
  }

  def set_state(self, on):
    self.state['state'] = "ON" if on else "OFF"

  def set_rgb(self, r, g, b):
    self.state['rgb_color'][0] = r
    self.state['rgb_color'][1] = g
    self.state['rgb_color'][2] = b
    self.writer(self.channels['red'], r)
    self.writer(self.channels['green'], g)
    self.writer(self.channels['blue'], b)

  def set_brightness(self, brightness):
    self.state['brightness'] = brightness
    self.set_state(brightness > 0)
    self.writer(self.channels['brightness'], brightness)

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
    self.mqttc.publish(self.config['state_topic'], json.dumps(self.state), retain=True)

  def publish_attributes(self):
    attrs = {}
    for key, attr in self.attributes.items():
      attrs[key] = attr.get_current().name
    if (self.mqttc): self.mqttc.publish(self.config['json_attributes_topic'], json.dumps(attrs), retain=True)

  def publish_config(self):
    self.mqttc.publish(self.config_topic, json.dumps(self.config), retain=True)

  def __init__(self, data, mqttc, writer):
    uid = data['name']
    self.uid = uid
    self.mqttc = mqttc
    self.writer = writer
    self.config_topic = f"homeassistant/light/dmx_{self.uid}/config"
    self.config['name'] = uid
    self.config['unique_id'] = uid
    self.config['command_topic'] = f'dmx/{uid}/set'
    self.config['state_topic'] = f'dmx/{uid}/state'
    self.config['json_attributes_topic'] = f'dmx/{uid}/attributes'

    self.channels['brightness'] = data['brightness']
    self.channels['red'] = data['red']
    self.channels['green'] = data['green']
    self.channels['blue'] = data['blue']
    if 'brightness' in data:
      self.config['brightness'] = True
      self.state['brightness'] = 0
    if 'red' in data or 'green' in data or 'blue' in data:
      self.config['color_mode'] = True
      self.config['supported_color_modes'] = ['rgb']
      self.state['color_mode'] = 'rgb'
      self.state['rgb_color'] = [255, 255, 255]

    for attr in data['attributes']:
      self.attributes[attr['name']] = DmxAttribute(uid, attr[name], mqttc)
      self.update_attribute(attr['name'])

    if mqttc: self.publish_config
    self.publish_attributes()

    # self.set_attribute('pattern', 'bar')
    # print(f'{uid}: {self.channels} {self.attributes}')

# with open('config.yaml', 'r') as file:
#     data = yaml.safe_load(file)

# def write_byte(num, val):
#   print(f'SET {num} = {val}')

# for key, data in data['options']['lights'].items():
#   light = DmxLight(key, data, False, write_byte)