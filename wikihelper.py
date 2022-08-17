import itemhelper, iconhelper
import xml.etree.ElementTree as ET
# from lxml import etree

stats = ET.parse('../../LotRO Companion/app/data/lore/stats.xml')
sets = ET.parse('../../LotRO Companion/app/data/lore/sets.xml')
items = ET.parse('../../LotRO Companion/app/data/lore/items.xml')
# etree_items = etree.parse('..\..\LotRO Companion\\app\data\lore\items.xml')

stats_names = {}

for s in stats.findall('.//stat'):
  lkey = s.get('legacyKey')
  key = s.get('key')
  name = s.get('name')
  isPercentage = s.get('isPercentage')
  stats_names[lkey] = {'name': name, 'isPercentage': isPercentage}
  stats_names[key] = {'name': name, 'isPercentage': isPercentage}

def get_binding(binding):
  b = {
    "BIND_ON_EQUIP": "BoE",
    "BOUND_TO_ACCOUNT_ON_ACQUIRE": "BtAoA",
    "BIND_ON_ACQUIRE": "BoA"
  }
  return b.get(binding)

# incomplete
params_ordered_list = ["disambigpage", "icon", "item_id", "quality", "item_level", "scaled", "containsitems",
 "unique_use", "unique", "indestructible", "consumed", "cosmetic", "bind", "type", "slot", "essences", 
 "armour", "dmg", "dmgtype", "dps", "attrib", "durability", "dur_class", "level", "flavor", "class", "set", "sell"]

wtype_list = {'axe', 'battle-gauntlets', 'bow', 'club', 'crossbow', 'javelin', 'dagger', 'halberd',
'hammer', 'mace', 'spear', 'sword'}

def add_item_param(param, data):
  return '\n| {:<16}= {}'.format(param, data)

def construct_disambig_page(item_name):
  items_ = items.findall(f'item[@name="{item_name}"]')

  item_names = []
  its = get_item(items_[0].get('key'), items, name_only=True)
  if its:
    item_names = [a.get('disambig_name') for a in its.values()]
  else:
    return None

  # for item in [x.get('key') for x in items_]:
  #   item_names.append(get_item(item, items, name_only=True))
  page_text = "== Item Information ==\nThere are different versions of this item:\n\n{{Item:"
  page_text += "}}\n{{Item:".join(item_names)
  page_text += "}}\n\n<noinclude>\n[[Category:Disambiguation Pages]]\n</noinclude>"
  return page_text

background_categories = {
  "1090519041": 'Common',
  "1090519042": "Uncommon",
  "1090519043": "Rare",
  "1090519044": "Incomparable",
  "1090519045": "Epic",
  "1091424691": 'Cosmetic',
  "1091711664": "Incomparable_Audacity",
  "1091398978": "Rare_Reputation",
  "1091399834": "Incomparable_Reputation",
  "1091398977": "Unknown?",
  "1091399841": "Unknown?",
  "1091398974": "Unknown?",
  "1091398976": "Unknown?",
  "1091398975": "Unknown?",
  "1091398973": "Unknown?",
  "1091472970": "Unknown?",
  "1091472985": "Unknown?",
  "1091472984": "Unknown?",
  "1091591349": "Lotro Store",
}

# attempts to find matching categories for given icon ID like armour type or slot.
# As some icons are not unique in those categories, this does not always work.
# requires items.xml parsed by etree
def categorize_icon(icon_id):
  icon_ids = icon_id.split("-")
  xpath_string = ''
  bg_cat = [a for a in icon_ids if a in background_categories][0]
  if (len(icon_ids)==1):
    return background_categories[bg_cat]
  for s in icon_ids:
    xpath_string += 'contains(@icon,%s) and ' %s
  xpath_string = xpath_string[:-5]
  res = etree_items.xpath('item[%s]' %xpath_string)
  item_attributes = {}
  failed = False
  for item in res:
    slot = item.get('slot')
    category = item.get('category')
    armour_type = item.get('armourType') 
    if "slot" not in item_attributes:
      item_attributes["slot"] = slot
      item_attributes["category"] = category
      item_attributes["armour_type"] = armour_type
    else:
      if False in {
        item_attributes["slot"] == slot,
        item_attributes["category"] == category,
        item_attributes["armour_type"] == armour_type,
      }:
        print("Cannot categorize icon:")
        print(item.attrib)
        print(str(slot)+str(category)+str(armour_type))
        failed = True
  if not failed:
    item_attributes['quality'] = background_categories[bg_cat]
    item_attributes['icon_id'] = icon_id
    return item_attributes


def make_wiki_representation(data):
  data['disambigpage'] = "{{subst:FULLPAGENAME}}"
  if data['quality'] == 'Legendary':
    data['quality'] = 'Epic'
  statslist = []
  stats = data.get('stats')
  if stats:
    for stat in data.get('stats'):
      value = stat.get('value')
      name = stat.get('name')
      perc = stat.get('isPercentage')
      if name is None:
        print(f"Stat not found for item {data.get('item_id')}")
      if name in ["Agility", "Might", "Vitality", "Fate", "Will"]:
        value = f'{int(value):,}'
      if name == "Armour":
        data['armour'] = f'{int(value):,}'
        continue
      if name == "Parry Chance": #added by WEffect for swords but maybe some items have it anyway?
        continue
      if name == 'Incoming Ranged Damage':
        name = 'Ranged Defence'
      if value[-2:] == '.0':
        value = value[:-2]
      if value[:1] == '-':
        if name == 'Ranged Defence':
          statslist.insert(0,f'{value}{"%" if perc else ""} {name}')  
        else:
          statslist.append(f'{value}{"%" if perc else ""} {name}')
      else:
        if name == 'Critical Defence' and statslist[0][5:] == 'Ranged Defence':
          statslist.insert(1,f'{value}{"%" if perc else ""} {name}')
        else:
          statslist.append(f'+{value}{"%" if perc else ""} {name}')
    if 'type' in data:
      w_type = data['type']
      for t in wtype_list:
        if t.capitalize() in w_type:
          w_type = t
          break
      if w_type in ['sword', 'bow', 'crossbow', 'dagger']:
        statslist.insert(0,f'{{{{WEffect|{w_type}}}}}')        
      elif w_type in ['axe']: # TODO two-handed
        with open('axe.txt', 'r', encoding='utf8') as axefile:
          vals = axefile.read()
          line = [line for line in vals.split('\n') if f'#{data["item_level"].split("{")[0]}' in line]
          axe, twohand_axe = line[0], line[1]
          armour_val = round(float(axe.split('-')[1]))
        statslist.append(f'{{{{WEffect|{w_type}|amount={armour_val}}}}}')
      elif w_type not in ["Heavy Shield", "Shield","Warden's Shield", "Heavy Armour", "Medium Armour", "Light Armour"]:
        statslist.append(f'{{{{WEffect|{w_type}}}}}')
    data['attrib'] = " <br> ".join(statslist)
    
  if 'Armour' in data:
    data['armour'] = f"{data['Armour']:,}"
  
  # set to True if icon ids should be used, False to attempt to use wiki names for icons
  use_icon_id = True
  if use_icon_id:
    pass
  else:
    icon = iconhelper.get_wiki_icon(data['icon'])
    data['icon'] = icon
    if icon is None:
      return None

  text = f"""
<onlyinclude>{{{{Item Tooltip
| mode            = {{{{{{mode|}}}}}}
| arg             = {{{{{{arg|}}}}}}
| amount          = {{{{{{amount|}}}}}}
| name            = {data.get('name')}"""
  for key in params_ordered_list:
    if key in data and data[key] is not None:
      text += add_item_param(key, data[key])
  return text + "\n}}</onlyinclude>__NOTOC__"

slot_to_wiki = {"Hand": "Gloves", "Main_hand": "Main-hand", "Off_hand": "Off-hand", "Neck": "Neck",
"Pocket": "Pocket", "Ranged_item": "Ranged", "Finger": "Finger", "Feet": "Feet", "Ear": "Ear",
"Chest": "Chest", "Legs": "Legs", "Head": "Head", "Back": "Back", "Shoulder": "Shoulder", "Wrist": "Wrist"}
armour_type_to_wiki = {"HEAVY_SHIELD": "Heavy Shield", "SHIELD": "Shield", "WARDEN_SHIELD": "Warden's Shield",
"HEAVY": "Heavy Armour", "MEDIUM": "Medium Armour", "LIGHT": "Light Armour"}
weapon_type_to_wiki = {"BOW": "Bow", "CROSSBOW": "Crossbow", "ONE_HANDED_SWORD": "One-handed Sword",
"ONE_HANDED_AXE": "One-handed Axe", "DAGGER": "Dagger", "ONE_HANDED_MACE": "One-handed Mace",
"ONE_HANDED_HAMMER": "One-handed Hammer", "ONE_HANDED_CLUB": "One-handed Club"}
dmg_type_to_wiki = {"ANCIENT_DWARF": "Ancient Dwarf-make", "COMMON": "Common"}


def get_items_with_name(item_name, item_file):
  return item_file.findall(f'item[@name="{item_name}"]')

def get_item_stats(key, item_file):
  it = item_file.find('item[@key="'+str(key)+'"]')
  item_stats = item_file.findall('item[@key="'+str(key)+'"]/stats/stat')
  if not item_stats:
    return None
  stat_list = []
  for stat in item_stats:
    stat_info = stats_names.get(stat.get('name'))
    c = stat.get('constant')
    v = stat.get('value')
    stat_value = c if c else v[:-2] if v else itemhelper.get_item_stat(stat.get('scaling'), int(it.get('level')))
    stat_list.append({'name': stat_info.get('name'), 'value': stat_value, 'isPercentage': stat_info.get('isPercentage')})
  return stat_list

def get_item_helper(key, item_file, scales_up=True, override_name=None):
  set_name = None
  if set_ := sets.find(f'.//set/item[@id="{key}"]..'):
    set_name = set_.get('name').split('\n')[0]
  plus_string = "{{Color|lightgreen|+}}"
  e = item_file.find(f'item[@key="{key}"]')
  item_name = e.get('name')
  wiki_entry = {}
  wiki_entry['name'] = item_name
  wiki_entry['item_id'] = key
  wiki_entry['quality'] = e.get('quality').capitalize() 
  wiki_entry['level'] = e.get('minLevel')
  wiki_entry['bind'] = get_binding(e.get('binding'))
  wiki_entry['item_level'] = f"{e.get('level')}{plus_string if scales_up else ''}"
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
  if slot:
    wiki_entry['slot'] = slot_to_wiki[slot]
  armour_type = e.get('armourType')
  if (armour_type):
    wiki_entry['type'] = armour_type_to_wiki[armour_type]
  weapon_type = e.get('weaponType')
  if (weapon_type):
    wiki_entry['type'] = weapon_type_to_wiki[weapon_type]
  dmgtype = e.get('damageType')
  if dmgtype:
    wiki_entry['dmgtype'] = dmg_type_to_wiki[dmgtype]
  dps = e.get('dps')
  if dps:
    wiki_entry['dps'] = '{:,.1f}'.format(float(dps))
    min_dmg = float(dps) * 0.75
    max_dmg = float(dps) * 1.25
    wiki_entry['dmg'] = f'{round(min_dmg):,} - {round(max_dmg):,}'
  wiki_entry['essences'] = e.get('slots')
  wiki_entry['icon'] = e.get('icon')
  description = e.get('description')
  if description:
    wiki_entry['flavor'] = description.replace('\n', '<br>')
  if set_name:
    wiki_entry['set'] = set_name
  if e.get('valueTableId'):
    value = int(itemhelper.get_item_value(e.get('valueTableId'), e.get('level'), e.get('quality')))
    if value:
      wiki_entry['sell'] = f'{{{{worth|g={int(value / 100000) or ""}|s={int(value / 100) % 1000 or ""}|c={int(value % 100) or ""}|dp=}}}}'

  if (item_stats := get_item_stats(key, item_file)):
    wiki_entry['stats'] = item_stats

  return {"wiki_page": make_wiki_representation(wiki_entry), "disambig_name": override_name or item_name}


# Stats will be used to change items' names in their listed order
disambiguation_priority_list = ["Parry Rating", "Evade Rating", "Block Rating", "Critical Defence", "Resistance Rating",
"Incoming Healing Rating", "Physical Mitigation", "Tactical Mitigation", "non-Combat Morale Regen", "non-Combat Power Regen",
"Maximum Power", "Maximum Morale", "Outgoing Healing Rating", "Finesse Rating", "Tactical Mastery Rating",
"Physical Mastery Rating", "Critical Rating", "Vitality", "Fate", "Will", "Might", "Agility"]

# Call this with an item key to get a dict containing the disambiguated item name
# and the content for the wiki Item Tooltip template
def get_item(key, item_file, scales_up=True, disambiguate=True, name_only=False):
  to_return = {}
  if key.startswith("Random level-adjusted Tracery"):
    return (key, None)
  if not disambiguate:
    return get_item_helper(key, item_file, scales_up)
  e = item_file.find(f'item[@key="{key}"]')
  if e.get('name') == "Universal Solvent":
    return "Universal Solvent"
  items_with_name = get_items_with_name(e.get('name'), item_file)
  item_ids = [a.get('key') for a in items_with_name]
  if len(item_ids) > 1:
    print(f"{len(item_ids)} items with name {e.get('name')}, attempting to compensate")
    for i in get_unique_items(item_ids, item_file, 'minLevel'):
      item = item_file.find(f'item[@key="{i}"]')
      this_name = f"{item.get('name')} (Level {item.get('minLevel')})"
      if item.get('key') not in to_return:
        to_return[item.get('key')] = get_item_helper(item.get('key'), item_file, scales_up, override_name=this_name)
      
    for i in get_unique_items(item_ids, item_file, 'quality'):
      item = item_file.find(f'item[@key="{i}"]')
      this_name = f"{item.get('name')} ({item.get('quality').capitalize().replace('Legendary', 'Epic')})"
      if item.get('key') not in to_return:
        to_return[item.get('key')] = get_item_helper(item.get('key'), item_file, scales_up, override_name=this_name)
          
    items_attributes = []
    by_quality = {"COMMON":[], "UNCOMMON":[], "RARE":[], "INCOMPARABLE":[], "LEGENDARY":[]}
    for it in [item_file.find(f'item[@key="{a}"]') for a in item_ids]:
      item_stats = get_item_stats(it.get('key'), item_file)
      by_quality[it.get('quality')].append(it)
      if item_stats:
        items_attributes.append({'key': it.get('key'), 'stats': [a['name'] for a in item_stats]})
    
    for cur in disambiguation_priority_list:
      items_with_attr = [item for item in items_attributes if cur in item.get('stats')]
      if len(items_with_attr) == 1:
        this_key = items_with_attr[0].get('key')
        this_name = f"{e.get('name')} ({cur})"
        
        if this_key not in to_return:
          to_return[this_key] = get_item_helper(this_key, item_file, scales_up, override_name=this_name)

      elif unique_quality := get_unique_items([x.get('key') for x in items_with_attr], item_file, 'quality'):
        for i in unique_quality:
          item = item_file.find(f'item[@key="{i}"]')
          this_name = f"{item.get('name')} ({cur}, {item.get('quality').capitalize().replace('Legendary', 'Epic')})"
          if i not in to_return:
            to_return[i] = get_item_helper(i, item_file, scales_up, override_name=this_name)
    
    for i in get_unique_items(item_ids, item_file, 'level'):
      item = item_file.find(f'item[@key="{i}"]')
      this_name = f"{item.get('name')} (Item Level {item.get('level')})"
      if i not in to_return:
        to_return[i] = get_item_helper(i, item_file, scales_up, override_name=this_name)
    
    for k, v in by_quality.items():
      ids = [a.get('key') for a in v]
      for i in get_unique_items(ids, item_file, by='level'):
        item = item_file.find(f'item[@key="{i}"]')
        this_name = f"{item.get('name')} (Item Level {item.get('level')}, {item.get('quality').capitalize().replace('Legendary', 'Epic')})"
        if i not in to_return:
          to_return[i] = get_item_helper(i, item_file, scales_up, override_name=this_name)
        
    if len(to_return.keys()) == len(item_ids):
      return to_return
    else:
      print("Failure: Could not disambiguate item.")
      print(key)
      return None
  if name_only:
    return e.get('name')
  else:
    return get_item_helper(key, item_file, scales_up)

def get_unique_items(item_ids, item_file, by):
  items = [item_file.find(f'item[@key="{a}"]') for a in item_ids]
  counts = {}
  for i in items:
    if (k := i.get(by)) in counts:
      counts[k].append(i.get('key'))
    else:
      counts[k] = [i.get('key')]
  return [value[0] for key, value in counts.items() if len(value)==1 and key!=None]

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
  if not chests:
    return ''
  chests = sorted(chests)
  dropinfo = "* " + "\n* ".join(chests)
  item_information = """
== Item Information ==
This item is a possible drop in the [[{}]] instance from the following chest(s):\n{}""".format(instance_name, dropinfo)
  return item_information