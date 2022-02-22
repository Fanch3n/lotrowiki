import itemhelper, iconhelper
import xml.etree.ElementTree as ET

stats = ET.parse('../../LotRO Companion/app/data/lore/stats.xml')

stats_names = {}

for s in stats.findall('.//stat'):
  lkey = s.get('legacyKey')
  key = s.get('key')
  name = s.get('name')
  isPercentage = s.get('isPercentage')
  stats_names[lkey] = {'name': name, 'isPercentage': isPercentage}
  stats_names[key] = {'name': name, 'isPercentage': isPercentage}

def get_icon(icon_identifier):
    d = {
        "1092541028-1090519045": "Light_Armour_47_(epic)",
        "1091723034-1090519044": "Necklace_16_(incomparable_1)",
        "1092525606-1090519044": "Light Leggings 52 (incomparable)",
        "1092541025-1090519045": "Medium Armour 86 (epic)",
        "1091625556-1090519044": "Necklace_94_(incomparable)",
        "1092593774-1090519043": "Necklace_110_(rare)",
        "1092591435-1090519044": "Medium_Shoulders_79_(incomparable)",
        "1091804422-1090519044": "Medium_Armour_1_(incomparable)",
        "1091662208-1090519044": "Earring 46 (incomparable 1)",
        "1091804511-1090519044": "Earring 52 (incomparable 1)",
        "1092556610-1090519043": "Medium Gloves 81 (rare)",
        "1092556605-1090519043": "Medium Shoulders 77 (rare)",
        "1092556600-1090519043": "Medium Armour 87 (rare)",
        "1092556608-1090519043": "Medium Helm 78 (rare)",
        "1092556611-1090519043": "Light Head 84 (rare)",
        "1092556609-1090519043": "Heavy Helm 74 (rare)",
        "1092556607-1090519043": "Heavy Gloves 85 (rare)",
        "1092556596-1090519043": "Heavy Shoulders 75 (rare)",
        "1092556601-1090519043": "Light Shoulders 74 (rare)",
        "1092556604-1090519043": "Light Gloves 75 (rare)",
        "1092525606-1090519043": "Medium Leggings 49 (rare)",
        "1092556602-1090519043": "Heavy Armour 81 (rare)",
        "1092556606-1090519043": "Heavy Boots 74 (rare)",
        "1092556598-1090519043": "Heavy Boots 74 (rare)",
        "1092556603-1090519043": "Light Shoes 74 (rare)",
        "1092556599-1090519043": "Light Armour 48 (rare)",
        "1092556597-1090519043": "Cloak 77 (rare)",
        "1091474195-1090519043": "Bracelet 40 (rare 1)",
        "1091662204-1090519043": "Ring 47 (rare 1)",
        "1091699351-1090519043": "Bracelet 70 (rare 1)",
        "1091564975-1090519043": "Bracelet 23 (rare 2)",
        "1091662208-1090519043": "Earring 46 (rare 1)",
        "1091699342-1090519043": "Ring 70 (rare 1)",
        "1091474207-1090519043": "Ring 20 (rare 1)",
        "1091751174-1090519043": "Bracelet 76 (rare 1)",
        "1091666956-1090519043": "Necklace 70 (rare 1)",
        "1091804509-1090519043": "Bracelet 18 (rare 1)",
        "1091567253-1090519043": "Earring 29 (rare 1)",
        "1091804511-1090519043": "Earring 52 (rare 1)",
        "1091957997-1090519043": "Ring 60 (rare)",
        "1092433515-1090519043": "Earring 81 (rare)",
        "1091751190-1090519043": "Ring 28 (rare 1)",
        "1091633566-1090519043": "Ring 92 (rare 1)",
        "1091662214-1090519043": "Necklace 67 (rare 1)",
        "1091696699-1090519043": "Necklace 59 (rare)",
        "1091633581-1090519043": "Earring 37 (rare 1)",
        "1091405233-1090519043": "Earring 30 (rare)",
        "1091581782-1090519043": "Earring 24 (rare 1)",
        "1091662202-1090519043": "Bracelet 41 (rare 1)",
        "1091723023-1090519043": "Earring 11 (rare 1)",
        "1091400683-1090519043": "Pocket 204 (rare)",
        "1091723001-1090519043": "Pocket 22 (rare 1)",
        "1091722999-1090519043": "Pocket 43 (rare 1)",
        "1092556600-1090519044": "Medium Armour 87 (incomparable)",
        "1092556602-1090519044": "Heavy Armour 81 (incomparable)",
        "1092556599-1090519044": "Light Armour 48 (incomparable)",
        "1091957997-1090519044": "Ring 60 (incomparable 1)",
        "1091633566-1090519044": "Ring 92 (incomparable 1)",
        "1091662204-1090519044": "Ring 47 (incomparable 1)",
        "1091699342-1090519044": "Ring 70 (incomparable 1)",
        "1091751190-1090519044": "Ring 28 (incomparable 1)",
        "1091474207-1090519044": "Ring 20 (incomparable 1)"
    }
    return d.get(icon_identifier, "")

def get_binding(binding):
  b = {
    "BIND_ON_EQUIP": "BoE",
    "BOUND_TO_ACCOUNT_ON_ACQUIRE": "BtAoA",
    "BIND_ON_ACQUIRE": "BoA"
  }
  return b.get(binding)

# incomplete
params_ordered_list = ["icon", "disambigpage", "quality", "item_level", "scaled", "containsitems", "unique_use", "unique", "indestructible", "consumed", "cosmetic", "bind", "slot", "type", "armour", "essences",
                         "attrib", "durability", "dur_class", "level", "class", "set", "sell"]

def add_item_param(param, data):
  return '\n| {:<16}= {}'.format(param, data)

def make_wiki_representation(data, item_id):
  data['disambigpage'] = "{{subst:FULLPAGENAME}}"
  if data['quality'] == 'Legendary':
    data['quality'] = 'Epic'
  statslist = []
  for stat in data.get('stats'):
    value = stat.get('value')
    name = stat.get('name')
    perc = stat.get('isPercentage')
    if name is None:
      print(f"Stat not found for item {item_id}, add to attrib_naming")
    if name in ["Agility", "Might", "Vitality", "Fate", "Will"]:
      value = f'{int(value):,}'
    if name == "Armour":
      data['armour'] = f'{int(value):,}'
      continue
    statslist.append(f'+{value}{"%" if perc else ""} {name}')
  data['attrib'] = " <br> ".join(statslist)

  if 'Armour' in data:
    data['armour'] = f"{data['Armour']:,}"
  

  # set to True if icon ids should be used, False to attempt to use wiki names for icons
  use_icon_id = True
  if use_icon_id:
    data['icon'] = data['icon'] + '-icon'
  else:
    icon = get_icon(data['icon']) + '-icon'
    if icon == '-icon':
      icon = iconhelper.get_wiki_icon(data['icon'])
    data['icon'] = icon
    if icon is None:
      return None

  text = f"""
<onlyinclude>{{{{Item Tooltip
| mode            = {{{{{{mode|}}}}}}
| arg             = {{{{{{arg|}}}}}}
| amount          = {{{{{{amount|}}}}}}
| name            = {{{{subst:PAGENAME}}}}"""
  for key in params_ordered_list:
    if key in data and data[key] is not None:
      text += add_item_param(key, data[key])
  return text + "\n}}</onlyinclude>__NOTOC__"
# TODO add param for item id

def get_item(key, item_file, set_name=None):
  e = item_file.find('item[@key="'+str(key)+'"]')
  i_stats = item_file.findall('item[@key="'+str(key)+'"]/stats/stat')
  
  wiki_entry = {}  
  wiki_entry['quality'] = e.get('quality').capitalize() 
  wiki_entry['level'] = e.get('minLevel')
  wiki_entry['bind'] = get_binding(e.get('binding'))
  wiki_entry['item_level'] = e.get('level') + '{{Color|lightgreen|+}}' # TODO change at some point
  sturdiness = e.get('sturdiness')
  if (sturdiness):
    wiki_entry['dur_class'] = e.get('sturdiness').capitalize()
  durability = e.get('durability')
  if (durability):
    wiki_entry['durability'] = durability
  required_class = e.get('requiredClass')
  if (required_class):
    wiki_entry['class'] = required_class
  slot = e.get('slot', "").capitalize()
  wiki_entry['slot'] = slot if slot != 'Hand' else 'Gloves'
  armour_type = e.get('armourType')
  if (armour_type):
    wiki_entry['type'] = armour_type.capitalize() + ' Armour'
  wiki_entry['essences'] = e.get('slots')
  wiki_entry['icon'] = e.get('icon')
  if set_name:
    wiki_entry['set'] = set_name
  value = itemhelper.get_item_value(e.get('valueTableId'), e.get('level'), e.get('quality'))
  wiki_entry['sell'] = f'{{{{worth|g={int(value / 100000) or ""}|s={int(value / 100) % 1000 or ""}|c={int(value % 100) or ""}|dp=}}}}'

  if i_stats:
    wiki_entry['stats'] = []
    for stat in i_stats:
      stat_info = stats_names.get(stat.get('name'))
      c = stat.get('constant')
      stat_value = c if c else stat.get('value')[:-2]
      wiki_entry['stats'].append({'name': stat_info.get('name'), 'value': stat_value, 'isPercentage': stat_info.get('isPercentage')})

  return (e.get('name'), make_wiki_representation(wiki_entry, key))


def lootboxify(lootbox_label, item_names, additional_label=''):
  sorted_items = sorted(list(item_names))
  if additional_label != '':
    additional_label = ' - ' + additional_label
  result = '{{Lootbox|'+lootbox_label+additional_label+'\n'
  for item in sorted_items:
    result+="|Item:"+item+'\n'
  return result+'}}\n'

def tablify(table_label, item_names, additional_label=''):
  sorted_items = sorted(list(item_names))
  if additional_label != '':
    additional_label = ' - ' + additional_label
  result = '{| class="altRowsMed collapsible collapsed" width="600"\n! ' + table_label + additional_label + '\n|-\n'
  for item in sorted_items:
    result+="| {{Reward|"+item+"}}\n|-\n"
  return result+'|}\n'

def construct_drop_information(chests, instance_name):
  chests = sorted(chests)
  dropinfo = ""
  if len(chests) == 1:
    dropinfo = chests[0]
  else:
    dropinfo = ", ".join(chests[:-1]) + " and " + chests[-1]
  item_information = """
== Item Information ==
This item is a possible drop in the [[{}]] instance from {}.""".format(instance_name, dropinfo)
  return item_information