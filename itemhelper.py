import xml.etree.ElementTree as ET

disenchantments = ET.parse('../../LotRO Companion\\app\data\lore\\disenchantments.xml')
loots = ET.parse('../../LotRO Companion\\app\data\lore\loots.xml')
containers = ET.parse('../../LotRO Companion\\app\data\lore\containers.xml')
valueTable = ET.parse('../../LotRO Companion\\app\data\lore\\valueTables.xml')

def main():
  print("Don't call directly")

if __name__ == "__main__":
  main()

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
  return str(linear_interpolation(x_lower, y_lower, x_higher, y_higher, ilvl))

    
def linear_interpolation(x0, y0, x1, y1, x):
    return (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)

def get_disenchantment(item_id):
  item = disenchantments.find(f"disenchantment[@sourceItemId='{item_id}']")
  if item is None:
    return None
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


def get_source_chests(item_key: str, markers) -> list:
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
  
  treasures = []
  for treasure_list in loots.iter('treasureList'):
    for a in table_ids:
      if treasure_list.find(f"treasureListEntry[@treasureGroupProfileId='{a}']") is not None:
        treasures.append(treasure_list.get('id'))
  
  trophy_tables = []
  for filtered_trophy_table in loots.iter('filteredTrophyTable'):
    for a in trophies:
      if filtered_trophy_table.find(f"filteredTrophyTableEntry[@trophyListId='{a}']") is not None:
        trophy_tables.append(filtered_trophy_table.get('id'))
  trophy_tables.extend(treasures)
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