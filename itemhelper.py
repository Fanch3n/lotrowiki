import xml.etree.ElementTree as ET

disenchantments = ET.parse('../../LotRO Companion\\app\data\lore\\disenchantments.xml')
loots = ET.parse('../../LotRO Companion\\app\data\lore\loots.xml')
containers = ET.parse('../../LotRO Companion\\app\data\lore\containers.xml')
valueTable = ET.parse('../../LotRO Companion\\app\data\lore\\valueTables.xml')

def main():
  print("Don't call directly")

if __name__ == "__main__":
  main()


def get_disenchantment(item_id):
  item = disenchantments.find(f"disenchantment[@sourceItemId='{item_id}']")
  quantity = item.get('quantity')
  result_name = item.get('name')
  if quantity is None:
    trophy = item.get('trophyListId')
    quantity = '1'
    trophy = loots.find('trophyList[@id="'+trophy+'"]')
    result_name = trophy.get('description')
    image_id = trophy.get('imageId')
    if image_id == '1092695094':
      result_name += ' (Gundabad Hide)'
    elif image_id == '1092695105':
      result_name += ' (Gundabad Skarn)'
    elif image_id == '1092695104':
      result_name += ' (Sunstone)'

  return (quantity, result_name)


def get_source_chests(item_key, markers):
  tables = []
  for items_table in loots.iter('itemsTable'):
    ites = items_table.find(f"itemsTableEntry[@itemId='{item_key}']")
    if ites is not None:
      tables.append(items_table)
  
  table_ids = [a.get('id') for a in tables]
  trophies = []
  for trophy_list in loots.iter('trophyList'):
    for a in table_ids:
      if trophy_list.find(f"trophyListEntry[@treasureGroupProfileId='{a}']") is not None:
        trophies.append(trophy_list.get('id'))
      
  trophy_tables = []
  for filtered_trophy_table in loots.iter('filteredTrophyTable'):
    for a in trophies:
      if filtered_trophy_table.find(f"filteredTrophyTableEntry[@trophyListId='{a}']") is not None:
        trophy_tables.append(filtered_trophy_table.get('id'))

  contained_in = []
  for elem in containers.iter('containers'):
    for e in elem:
      if (e.get('filteredTrophyTableId') in trophy_tables or e.get('filteredTrophyTableId2') in trophy_tables or
          e.get('treasureListId') in trophy_tables or e.get('trophyListId') in trophy_tables or
          e.get('relicId') in trophy_tables or e.get('relicsListId') in trophy_tables):
        contained_in.append(e.get('id'))
  
  lootboxes = []
  # TODO only checks containers in supplied markers file
  for elem in markers.iter('markers'):
    for e in elem:
      if e.get('did') in contained_in:
        lootboxes.append((e.get('id'), e.get('label')))
  return lootboxes



def get_item_value(value_table_id, ilvl, iquality):
    values = valueTable.find(f"valueTable[@id='{value_table_id}']//quality[@key='{iquality}']")
    factor = float(values.attrib.get('factor'))
    value = float(valueTable.find(f"valueTable[@id='{value_table_id}']//baseValue[@level='{ilvl}']").get('value'))
    return factor * value