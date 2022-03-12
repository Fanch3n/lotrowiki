import xml.etree.ElementTree as ET
import itemhelper, wikihelper

#items = ET.parse('../../LotRO Companion\\app\data\lore\items.xml')
items = ET.parse('../../items.xml')
containers = ET.parse('../../LotRO Companion\\app\data\lore\containers.xml')
loots = ET.parse('../../LotRO Companion\\app\data\lore\loots.xml')
markers = ET.parse('../../LotRO Companion\\app\data\lore\maps\markers\markers-2-14-15.xml') # AZ
# markers = ET.parse('../../LotRO Companion\\app\data\lore\maps\markers\markers-2-15-13.xml') # Pughlak

def getNameFromItemId(item_id):
  if item_id.startswith("Random level-adjusted Tracery"):
    return item_id
  item = items.find('item[@key="'+item_id+'"]')
  name = item.get('name')
  if name.startswith("Enhancement Rune"):
    level = item.get('level')
    quality = item.get('quality').lower().replace("legendary", "epic")
    name = f"Enhancement Rune, Lvl {level} ({quality})"
  else:
    name = wikihelper.get_item(item_id, items, name_only=True)
  return name

def getInstanceNameFromChestId(chest_id):
  pzid = markers.find('marker[@did="'+chest_id+'"]').get('parentZoneId')
  pencs = ET.parse('../../LotRO Companion\\app\data\lore\privateEncounters.xml')
  zone_id = pencs.find(f'.//skirmishPrivateEncounter/instanceMap/zone[@zoneId="{pzid}"]....').get('name')
  return zone_id

def getItemIds(trophyListId): # return all items in that trophy list tree
  trophyList = loots.find('trophyList[@id="'+trophyListId+'"]')
  itemIds = []
  for child in trophyList:
    if 'itemId' in child.keys():
      itemIds.append(child.get('itemId'))
    elif 'treasureGroupProfileId' in child.keys():
      itemsTableId = child.get('treasureGroupProfileId')
      itemsTable = loots.find('itemsTable[@id="'+itemsTableId+'"]')
      for itemsTableEntry in itemsTable:
        itemIds.append(itemsTableEntry.get('itemId'))
  return itemIds

def getTreasures(treasureListId):
  treasures = loots.find('treasureList[@id="'+treasureListId+'"]')
  treasureItemIds = set()
  for treasureListEntry in treasures:
    treasureGroupProfileId = treasureListEntry.get('treasureGroupProfileId')
    itemsTable = loots.find('itemsTable[@id="'+treasureGroupProfileId+'"]')
    for itemsTableEntry in itemsTable:
      treasureItemIds.add(itemsTableEntry.get('itemId'))
  return treasureItemIds

def get_treasure_from_container(container_id): #Cosmetics
  marker = markers.find('marker[@did="'+container_id+'"]')
  lootbox_label = marker.get('label')
  treasure_list_id = containers.find('container[@id="'+container_id+'"]').get('treasureListId')
  if treasure_list_id:
    treasure_item_ids = getTreasures(treasure_list_id)
    return wikihelper.tablify(lootbox_label, map(getNameFromItemId,treasure_item_ids), 'Cosmetics')
  return ""

def get_trophy_list_items_from_container(list_id):
  trophylist_entries = loots.findall(f"trophyList[@id='{list_id}']//")
  return [a.get('itemId') for a in trophylist_entries]

def get_filtered_trophy_table_items_from_container(list_id):
  trophies = loots.findall(f'filteredTrophyTable[@id="{list_id}"]//')[-1:] # TODO only checking last for now
  if not trophies or trophies[0].get('trophyListId') is None:
    print("filteredTrophyTableId2 not found")
    trophies = []
  else:
    trophies = getItemIds(trophies[0].get('trophyListId'))
  return trophies

def check_for_tracery_trophy_table(table_id):
  if table_id == "1879428521":
    return ["Random level-adjusted Tracery, uncommon"]
  elif table_id == "1879428517":
    return ["Random level-adjusted Tracery, rare"]
  elif table_id == "1879428567":
    return ["Random level-adjusted Tracery, incomparable"]
  elif table_id == "1879428563":
    return ["Random level-adjusted Tracery, epic"]
  else:
    return None

def get_items_from_container(container_id):
  result = containers.find('container[@id="'+container_id+'"]')

  filtered_trophy_table_id = result.get('filteredTrophyTableId')
  filtered_trophy_table_id_2 = result.get('filteredTrophyTableId2')
  filtered_trophy_table_id_3 = result.get('filteredTrophyTableId3')
  trophy_list_id = result.get('trophyListId')
  trophies = loots.find('filteredTrophyTable[@id="'+filtered_trophy_table_id+'"]')
  
  required_class = {}
  for child in trophies:
    required_class[child.get('requiredClass')] = child.get('trophyListId')
    
  loot_items = {}
  for class_, trophylist in required_class.items():
    loot_items[class_] = getItemIds(trophylist)
  common_items = {}
  if loot_items:
    common_items = set(list(loot_items.values())[0]).intersection(*loot_items.values())

  for class_, values in loot_items.items():
    for e in common_items:
      if e in values:
        values.remove(e)
  
  loot_items['Common'] = list(common_items)
  trophy_list_items = get_trophy_list_items_from_container(trophy_list_id)
  trophies_2_items = check_for_tracery_trophy_table(filtered_trophy_table_id_2)
  if not trophies_2_items:
    trophies_2_items = get_filtered_trophy_table_items_from_container(filtered_trophy_table_id_2)
  trophies_3_items = check_for_tracery_trophy_table(filtered_trophy_table_id_3)
  if not trophies_3_items:
    trophies_3_items = get_filtered_trophy_table_items_from_container(filtered_trophy_table_id_3)
  if trophy_list_items:
    loot_items['Common'].extend(trophy_list_items)
  if trophies_2_items:
    loot_items['Common'].extend(trophies_2_items)
  if trophies_3_items:
    loot_items['Common'].extend(trophies_3_items)
  # above items seem to be in Common currently, but that's not checked explicitly
  return loot_items

def create_container_loot_table(loot_items, container_id, group_by='armour'):
  marker = markers.find('marker[@did="'+container_id+'"]')
  lootbox_label = marker.get('label')
  class_to_armour = {
    'Beorning;Captain;Champion;Guardian;Brawler': 'Heavy Armour',
    'Burglar;Hunter;Warden': 'Medium Armour',
    'Lore-master;Minstrel;Rune-keeper': 'Light Armour'
  }
  output = []
  grouped = {}
  for class_, item_ids in loot_items.items():
    if class_ in class_to_armour:
      class_ = class_to_armour[class_]
    elif group_by == 'armour' and class_ in 'Beorning;Captain;Champion;Guardian;Brawler'.split(';'):
      class_ = 'Heavy Armour'
    elif group_by == 'armour' and class_ in 'Burglar;Hunter;Warden'.split(';'):
      class_ = 'Medium Armour'
    elif group_by == 'armour' and class_ in 'Lore-master;Minstrel;Rune-keeper'.split(';'):
      class_ = 'Light Armour'
    if class_ in grouped:
      grouped[class_].extend(item_ids)
    else:
      grouped[class_] = item_ids
    
  for key, elem in grouped.items():
    elem_unique = list(dict.fromkeys(elem))
    output.append(wikihelper.tablify(lootbox_label, map(getNameFromItemId,elem_unique), key))
  return output

def create_wiki_page(item_id, container_id):
  item_name, item_wiki_format = wikihelper.get_item(item_id, items)
  if item_wiki_format is None:
    print("No icon available, skipping Item: " + item_name)
    return None
  chests = itemhelper.get_source_chests(item_id, markers)
  item_information = wikihelper.construct_drop_information([chestname for key,chestname in chests], getInstanceNameFromChestId(container_id))
  disenchantment = itemhelper.get_disenchantment(item_id)
  if disenchantment:
    item_information += "\n{{Disenchant |"+disenchantment[0]+"| "+ disenchantment[1]+"}}"
  item_wiki_format += item_information
  return {'name': item_name, 'wiki_format': item_wiki_format}


def wiki_pages_for_loot_from_containers(containers: list):
  result = []
  all_items = {}
  for container_id in containers:
    item_ids = get_items_from_container(container_id)
    for itemlist in item_ids.values():
      for a in itemlist:
        all_items[a] = None
    for e in item_ids.get('Common'):
      all_items.pop(e)
    # TODO ignoring items that drop for all classes currently
  for item_id in all_items:
  # for item_id in getTreasures("1879440744"): # TODO include treasures by default
  # for item_id in item_ids.get('Common'):
    res = create_wiki_page(item_id, container_id)
    if res:
      item_name = res['name']
      wiki_format = res['wiki_format']
      result.append(f"Begin Item:\n{item_name}\n{wiki_format}\n")   
  return result

def output_to_file(string_to_write, filename="output.txt"):
  with open(filename, 'w', encoding='utf8') as outputfile:
    outputfile.write(string_to_write)


def create_wiki_tables_for_containers(containers):
  output = []
  for container_id in containers:
    output = output + create_container_loot_table(get_items_from_container(container_id), container_id)
  return output

def get_item_stat(progression: str, ilvl: int):
  progressions = ET.parse('../../LotRO Companion/app/data/lore/progressions.xml')
  prog = progressions.findall(f"linearInterpolationProgression[@identifier='{progression}']/")
  x_lower = -1
  y_lower = 0
  x_higher = 1000
  y_higher = 0
  for e in prog:
    cur_att = int(e.attrib['x'])
    if cur_att > x_lower and cur_att <= ilvl:
      x_lower = cur_att
      y_lower = float(e.attrib['y'])
    if cur_att < x_higher and cur_att >= ilvl:
      x_higher = cur_att
      y_higher = float(e.attrib['y'])
  return linear_interpolation(x_lower, y_lower, x_higher, y_higher, ilvl)

    
def linear_interpolation(x0, y0, x1, y1, x):
    return (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)

def construct_set_piece_string(item_id):
  e = items.find('item[@key="'+item_id+'"]')
  quality = e.get('quality')
  if quality == 'LEGENDARY':
    quality = 'EPIC'
  quality = quality.capitalize()
  itemname = e.get('name')
  return f"{{{{loot|{quality}|Item:{itemname}|{itemname}}}}}"

def construct_set_bonus_string(effects):
  bonus_effects = []
  for effect in effects:
    base_text = f"| bonus{effect['nbItems']}       = "
    if ('descriptionOverride' in effect
        and effect['descriptionOverride'] is not None
        and effect['descriptionOverride'] != "-"):
      bonus_effects.append(f"{base_text}&nbsp;&nbsp;{effect['descriptionOverride']}")
    elif 'specialEffect' not in effect:
      effect_strings = []
      for e in effect.get('effects'):
        value = e.get('value')
        if value[-1:] == "0":
          value = value[:-2]
        name = e.get('name')
        perc = e.get('isPercentage')
        if name in ["Agility", "Might", "Vitality", "Fate", "Will"]:
          value = f'{int(value):,}'
        effect_strings.append(f"&nbsp;&nbsp;{''if perc else '+'}{value}{'%' if perc else ''} {name}")
      bonus_effects.append(f"{base_text}{'<br>'.join(effect_strings)}")
    else:
      bonus_effects.append(f"{base_text}&nbsp;&nbsp;{effect['specialEffect']}")
  return "\n".join(bonus_effects)


def construct_set_page(set_id):
  sets = ET.parse('../../LotRO Companion\\app\data\lore\sets.xml')
  set_ = sets.find(f'.//set[@id="{set_id}"]')
  set_name = set_.get('name').split("\n")[0]
  set_maxlvl = set_.get('maxLevel')
  set_level = set_.get('level')
  set_description = set_.get('description') # TODO not used on current set
  set_bonuses = set_.findall('.//bonus')
  set_pieces = [piece.get('id') for piece in set_.findall('.//item')]
  temp = []
  for bonus in set_bonuses:
    i = {'effects': []}
    i['nbItems'] = bonus.get('nbItems')
    for n in bonus.findall('.//stat'):
      c = n.get('constant')
      effect = {}
      if c is None:
        c = str(int(get_item_stat(n.get('scaling'), int(set_level))))
      else:
        effect['isPercentage'] = True
      effect['name'] = wikihelper.stats_names.get(n.get('name')).get('name')
      effect['value'] = c
      if 'descriptionOverride' not in i:
        i['descriptionOverride'] = n.get('descriptionOverride')
      i['effects'].append(effect)
      
    for n in bonus.findall('.//specialEffect'):
      i['specialEffect'] = n.get('label')
    temp.append(i)

  pieces = "<br>".join([construct_set_piece_string(a) for a in set_pieces])

  string = """<onlyinclude>{{Settip
| mode         = {{{mode|}}}
| arg          = {{{arg|}}}
| name         = """+set_name+"""
| disambigpage = {{subst:FULLPAGENAME}}
| maxlevel     = """+set_maxlvl+"""
| pieces       = """+pieces+"\n"+construct_set_bonus_string(temp)+"""
}}</onlyinclude>__NOTOC__
== Source ==
Items from this set drop in the [[The Hiddenhoard of Abnankâra]] raid.

[[Category:The Hiddenhoard of Abnankâra Armour Sets]]
"""
  return string



set_ids = ["1879444526", "1879444522", "1879444513", "1879444497", "1879444493", "1879444460",
 "1879444458", "1879444457", "1879444447", "1879444436", "1879444421", "1879444411", "1879444410",
 "1879444403", "1879444396","1879444391", "1879444383", "1879444373", "1879444364", "1879444354",
 "1879444352", "1879444351", "1879444339", "1879444327", "1879444326", "1879444316",
 "1879444313", "1879444301", "1879444292", "1879444284", "1879444276", "1879444272", "1879444266"]

conts = """1879441968
1879441976
1879441970
1879441973
1879441969
1879441967
1879441978
1879441980
1879441975
1879441977
1879441969
1879441971
1879441965
1879441964
1879441981
1879441979
1879441972
1879441974"""

# Hiddenhoard containers (B1 T1-5, B2 T1-5, B3 T1-5)
container_ids = [
  "1879441976" # AZ
#  "1879441352",
#  "1879441344",
# "1879441347",
# "1879441340",
# "1879441342",
#  "1879441353",
#  "1879441349",
# "1879441351",
# "1879441345",
# "1879441348",
#  "1879441350",
#  "1879441343",
# "1879441346",
# "1879441339",
# "1879441341"
]
container_ids = conts.split('\n')
# set_results = []
# for i in set_ids:
#   sets = ET.parse('../../LotRO Companion\\app\data\lore\sets.xml')
#   set_ = sets.find(f'.//set[@id="{i}"]')
#   set_name = None
#   if set_:
#     set_name = set_.get('name').split('\n')[0]
#   set_results.append(set_name + "\n" + construct_set_page(i))

# output = "\nNew Set Item\n".join(set_results)
output = wiki_pages_for_loot_from_containers(container_ids)
# output = create_wiki_tables_for_containers(container_ids)
# output = get_treasure_from_container("1879441974")
# output = []
# for c_id in container_ids:
#   output.append(get_treasure_from_container(c_id))
# print(wikihelper.get_item("1879433509", items)[1])

output_to_file("".join(output))
