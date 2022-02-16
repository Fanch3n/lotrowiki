
import xml.etree.ElementTree as ET
import itemhelper, wikihelper

items = ET.parse('../../LotRO Companion\\app\data\lore\items.xml')
containers = ET.parse('../../LotRO Companion\\app\data\lore\containers.xml')
loots = ET.parse('../../LotRO Companion\\app\data\lore\loots.xml')
#markers = ET.parse('LotRO Companion\\app\data\lore\maps\markers\markers-2-14-15.xml') # AZ
markers = ET.parse('../../LotRO Companion\\app\data\lore\maps\markers\markers-2-15-13.xml') # Pughlak

# Find all loot from a certain instance chest

def getNameFromItemId(itemId):
  item = items.find('item[@key="'+itemId+'"]')
  return item.get('name')

def getInstanceNameFromChestId(chest_id):
  pzid = markers.find('marker[@did="'+chest_id+'"]').get('parentZoneId')
  pencs = ET.parse('../../LotRO Companion\\app\data\lore\privateEncounters.xml')
  zoneId = pencs.find(f'.//skirmishPrivateEncounter/instanceMap/zone[@zoneId="{pzid}"]....').get('name')
  return zoneId

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

container_id = "1879421336"
marker = markers.find('marker[@did="'+container_id+'"]')
lootbox_label = marker.get('label')

result = containers.find('container[@id="'+container_id+'"]')

filteredTrophyTableID = result.get('filteredTrophyTableId')
filteredTrophyTableId2 = result.get('filteredTrophyTableId2') # TODO add enhancement runes: How to output quality and level?
treasureListId = result.get('treasureListId')


trophies = loots.find('filteredTrophyTable[@id="'+filteredTrophyTableID+'"]')

treasureItemIds = getTreasures(treasureListId)

for child in trophies:
  armour_class = child.get('requiredClass')
  if armour_class == 'Beorning;Captain;Champion;Guardian;Brawler':
    heavy = child.get('trophyListId')
  elif armour_class == 'Burglar;Hunter;Warden':
    medium = child.get('trophyListId')
  elif armour_class == 'Lore-master;Minstrel;Rune-keeper':
    light = child.get('trophyListId')
  
heavyItems = set(getItemIds(heavy))
mediumItems = set(getItemIds(medium))
lightItems = set(getItemIds(light))

itemIds = heavyItems | mediumItems | lightItems
onlyHeavy = heavyItems - mediumItems - lightItems
onlyMedium = mediumItems - lightItems - heavyItems
onlyLight = lightItems - mediumItems - heavyItems

commonItems = itemIds - onlyHeavy - onlyMedium - onlyLight

# print(wikihelper.tablify(lootbox_label, map(getNameFromItemId,onlyHeavy), 'Heavy Armour'))
# print(wikihelper.tablify(lootbox_label, map(getNameFromItemId,onlyMedium), 'Medium Armour'))
# print(wikihelper.tablify(lootbox_label, map(getNameFromItemId,onlyLight), 'Light Armour'))
# print(wikihelper.tablify(lootbox_label, map(getNameFromItemId,commonItems), 'Other'))
# print(wikihelper.tablify(lootbox_label, map(getNameFromItemId,treasureItemIds), 'Cosmetics'))

# def getAllItemsWithName(item_name):
#   return items.findall('item[@name="'+item_name+'"]')

all_info = ""
for _id in itemIds - commonItems:
#for _id in treasureItemIds:
  item_name, item_wiki_format = wikihelper.get_item(_id, items)
  if item_wiki_format is None:
    print("No icon available, skipping Item: " + item_name)
    continue
  item_wiki_format = item_name + "\n" + item_wiki_format
  chests = itemhelper.get_source_chests(_id, markers)
  item_information = wikihelper.construct_drop_information([chestname for key,chestname in chests], getInstanceNameFromChestId(container_id))
  disenchantment = itemhelper.get_disenchantment(_id)
  item_information += "\n{{Disenchant |"+disenchantment[0]+"| "+ disenchantment[1]+"}}"
  item_wiki_format += item_information
  number_of_items_with_name = len(getAllItemsWithName(item_name))
  if number_of_items_with_name > 1:
    print("Attention! There are {} items with this name! Skipping item.".format(number_of_items_with_name))
  else:
    all_info += "Begin Item:\n" + item_wiki_format + "\n"

  # with open('chestdrops', 'w', encoding='utf8') as chestdrops:
  #   chestdrops.write(all_info)