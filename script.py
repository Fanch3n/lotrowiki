import xml.etree.ElementTree as ET
import itemhelper, wikihelper

items = ET.parse('../../LotRO Companion\\app\data\lore\items.xml')
containers = ET.parse('../../LotRO Companion\\app\data\lore\containers.xml')
loots = ET.parse('../../LotRO Companion\\app\data\lore\loots.xml')
#markers = ET.parse('LotRO Companion\\app\data\lore\maps\markers\markers-2-14-15.xml') # AZ
markers = ET.parse('../../LotRO Companion\\app\data\lore\maps\markers\markers-2-15-13.xml') # Pughlak

# Find all loot from a certain instance chest

def getNameFromItemId(item_id):
  item = items.find('item[@key="'+item_id+'"]')
  return item.get('name')

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

def getIconId(itemId):
  return items.find('item[@key="'+itemId+'"]').get('icon')

def getTreasures(treasureListId):
  treasures = loots.find('treasureList[@id="'+treasureListId+'"]')
  treasureItemIds = set()
  for treasureListEntry in treasures:
    treasureGroupProfileId = treasureListEntry.get('treasureGroupProfileId')
    itemsTable = loots.find('itemsTable[@id="'+treasureGroupProfileId+'"]')
    for itemsTableEntry in itemsTable:
      treasureItemIds.add(itemsTableEntry.get('itemId'))
  return treasureItemIds

def getAllItemsWithName(item_name):
    return items.findall('item[@name="'+item_name+'"]')


def get_items_from_container(container_id):
  result = containers.find('container[@id="'+container_id+'"]')

  filteredTrophyTableID = result.get('filteredTrophyTableId')
  filteredTrophyTableId2 = result.get('filteredTrophyTableId2') # TODO add enhancement runes: How to output quality and level?
  filtered_trophy_table_id3 = result.get('filteredTrophyTableId3')
  trophy_list_id = result.get('trophyListId')
  treasureListId = result.get('treasureListId')
  # TODO most of these seem to be duplicates (so are included already), but should be handled properly

  trophies = loots.find('filteredTrophyTable[@id="'+filteredTrophyTableID+'"]')

  if treasureListId:
    treasureItemIds = getTreasures(treasureListId)

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
  return loot_items

def create_container_loot_table(loot_items, container_id):
  marker = markers.find('marker[@did="'+container_id+'"]')
  lootbox_label = marker.get('label')
  class_to_armour = {
    'Beorning;Captain;Champion;Guardian;Brawler': 'Heavy Armour',
    'Burglar;Hunter;Warden': 'Medium Armour',
    'Lore-master;Minstrel;Rune-keeper': 'Light Armour'
  }
  output = []
  for class_, item_ids in loot_items.items():
    if class_ in class_to_armour:
      class_ = class_to_armour[class_]
    output.append(wikihelper.tablify(lootbox_label, map(getNameFromItemId,item_ids), class_))
    # print(wikihelper.tablify(lootbox_label, map(getNameFromItemId,treasureItemIds), 'Cosmetics')) TODO
  return output

def create_wiki_page(item_id, container_id):
  sets = ET.parse('../../LotRO Companion\\app\data\lore\sets.xml')
  set_ = sets.find(f'.//set/item[@id="{item_id}"]..')
  set_name = None
  if set_:
    set_name = set_.get('name').replace('\n', ' ')    
  item_name, item_wiki_format = wikihelper.get_item(item_id, items, set_name)
  if item_wiki_format is None:
    print("No icon available, skipping Item: " + item_name)
    return None
  chests = itemhelper.get_source_chests(item_id, markers)
  item_information = wikihelper.construct_drop_information([chestname for key,chestname in chests], getInstanceNameFromChestId(container_id))
  disenchantment = itemhelper.get_disenchantment(item_id)
  item_information += "\n{{Disenchant |"+disenchantment[0]+"| "+ disenchantment[1]+"}}"
  item_wiki_format += item_information
  number_of_items_with_name = len(getAllItemsWithName(item_name))
  if number_of_items_with_name > 1:
    print(f"Attention! There are {number_of_items_with_name} items with this name! Skipping item {item_name}")
  else:
    return {'name': item_name, 'wiki_format': item_wiki_format}



def wiki_pages_for_loot_from_containers(containers):
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
  for container_id in container_ids:
    output = output + create_container_loot_table(get_items_from_container(container_id), container_id)
  return output

# Hiddenhoard containers (B1 T1-5, B2 T1-5, B3 T1-5)
container_ids = ["1879441352",
# "1879441344",
# "1879441347",
# "1879441340",
# "1879441342",
# "1879441353",
# "1879441349",
# "1879441351",
# "1879441345",
# "1879441348",
# "1879441350",
# "1879441343",
# "1879441346",
# "1879441339",
"1879441341"]

output = wiki_pages_for_loot_from_containers(container_ids)
# output = create_wiki_tables_for_containers(container_ids)
# print(wikihelper.get_item("1879433509", items)[1])

output_to_file("".join(output))


# sets = ET.parse('../../LotRO Companion\\app\data\lore\sets.xml')
# id = '1879444347'
# set_ = sets.find(f'.//set/item[@id="{id}"]..')
# set_name = set_.get('name')
# set_maxlvl = set_.get('maxLevel')
# set_description = set_.get('description')
# set_bonuses = set_.findall('.//bonus')
