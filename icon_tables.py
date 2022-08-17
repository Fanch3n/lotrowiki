# build icon tables
# this creates a 'icon_tables' directory with a text file for each wiki table
import xml.etree.ElementTree as ET

import wikihelper

legendary_icons = ["1091472984", "1091472985", "1091472970"]

# Classes needed:
# 45 for Back/Cloaks
# 7 for Head plus L/M/H
# 6 for shoulders plus L/M/H
# 3 for chest plus L/M/H
# 5 for hands plus L/M/H
# 15 for legs plus L/M/H
# 23 for shoes plus L/M/H
# 33 for shields plus none, warden, heavy
# 49 for jewellery
#  slots: Finger, Ear, Pocket, Wrist, Neck

item_categories = {
  "Chest": {"class": "3", "subcategories": ["Light", "Medium", "Heavy"]},
  "Gloves": {"class": "5", "subcategories": ["Light", "Medium", "Heavy"]},
  "Shoulder": {"class": "6", "subcategories": ["Light", "Medium", "Heavy"]},
  "Head": {"class": "7", "subcategories": ["Light", "Medium", "Heavy"]},
  "Legs": {"class": "15", "subcategories": ["Light", "Medium", "Heavy"]},
  "Feet": {"class": "23", "subcategories": ["Light", "Medium", "Heavy"]},
  "Shield": {"class": "33", "subcategories": ["Shield", "Warden_Shield", "Heavy_Shield"]},
  "Back": {"class": "45"},
  "Ring": {"class": "49", "slot": "FINGER"},
  "Bracelet": {"class": "49", "slot": "WRIST"},
  "Earring": {"class": "49", "slot": "EAR"},
  "Pocket": {"class": "49", "slot": "POCKET"},
  "Necklace": {"class": "49", "slot": "NECK"},
  "One-handed Club": {"class": "40", "weapon_type": "ONE_HANDED_CLUB"},
  "Two-handed Club": {"class": "40", "weapon_type": "TWO_HANDED_CLUB"},
  "Spear": {"class": "46", "weapon_type": "SPEAR"},
  "Staff": {"class": "34", "weapon_type": "STAFF"},
  "Halberd": {"class": "36", "weapon_type": "HALBERD"},
  "One-handed Mace": {"class": "30", "weapon_type": "ONE_HANDED_MACE"},
  "Crossbow": {"class": "29", "weapon_type": "CROSSBOW"},
  "One-handed Hammer": {"class": "24", "weapon_type": "ONE_HANDED_HAMMER"},
  "Two-handed Hammer": {"class": "24", "weapon_type": "TWO_HANDED_HAMMER"},
  "One-handed Axe": {"class": "12", "weapon_type": "ONE_HANDED_AXE"},
  "Two-handed Axe": {"class": "12", "weapon_type": "TWO_HANDED_AXE"},
  "Dagger": {"class": "10", "weapon_type": "DAGGER"},
  "Bow": {"class": "1", "weapon_type": "BOW"},
  "One-handed Sword": {"class": "44", "weapon_type": "ONE_HANDED_SWORD"},
  "Two-handed Sword": {"class": "44", "weapon_type": "TWO_HANDED_SWORD"},
  "Implement": {"class": "91"},
  "Fire Rune-stone": {"class": "104", "weapon_type": "RUNE_STONE", "damage_type": "FIRE"},
  "Frost Rune-stone": {"class": "104", "weapon_type": "RUNE_STONE", "damage_type": "FROST"},
  "Lightning Rune-stone": {"class": "104", "weapon_type": "RUNE_STONE", "damage_type": "LIGHTNING"},
  "Javelin": {"class": "110", "weapon_type": "JAVELIN"},
  "Battle-gauntlets": {"class": "290", "weapon_type": "BATTLE_GAUNTLETS"},
}

additional_icons = {
  "NECK": ["1090523202-1090519045-1090523203"],
  "WRIST": [],
  "POCKET": [],
  "HAND": [],
  "FINGER": [],
  "EAR": [],
  "CHEST": [],
  "FEET": [],
  "HEAD": [],
  "LEGS": [],
  "BACK": [],
  "SHOULDER": []
}

def is_legendary(icon):
  return bool(set(icon.split("-")).intersection(legendary_icons))

items = ET.parse('../../LotRO Companion\\app\data\lore\items.xml')
icon_dict = dict.fromkeys(item_categories.keys())
for item_key, item_cats in item_categories.items():
  item_class = item_cats["class"]
  for its in items.iter('items'):
    for i in its:
      if (i.get('class') == item_class):
        if "subcategories" in item_cats:
          for sub in item_cats["subcategories"]:
            if i.get('armourType') == sub.upper():
              if not is_legendary(i.get('icon')):
                if icon_dict[item_key] is None:
                  icon_dict[item_key] = {}
                if sub in icon_dict[item_key]:
                  icon_dict[item_key][sub].append(i.get('icon'))
                else:
                  icon_dict[item_key][sub] = [i.get('icon')]
        elif "slot" in item_cats:
          if i.get('slot') == item_cats["slot"]:
            if not is_legendary(i.get('icon')):
              if icon_dict[item_key]:
                icon_dict[item_key].append(i.get('icon'))
              else:
                icon_dict[item_key] = [i.get('icon')]
        elif "weapon_type" in item_cats:
          if i.get('weaponType') == item_cats["weapon_type"]:
            if "damage_type" in item_cats and (d_t := item_cats['damage_type']) and d_t != i.get('damageType'):
              continue
            if not is_legendary(i.get('icon')):
              if icon_dict[item_key]:
                icon_dict[item_key].append(i.get('icon'))
              else:
                icon_dict[item_key] = [i.get('icon')]
        else:
          if not is_legendary(i.get('icon')):
            if icon_dict[item_key]:
              icon_dict[item_key].append(i.get('icon'))
            else:
              icon_dict[item_key] = [i.get('icon')]

# icon_dict.extend(additional_icons[slot])
# TODO this is needed for at least one item that should be in the resulting table
# but is not categorized for it.


# also TODO: Rodongol is class 7 (Head) but should be Cloak

def create_row(content):
  obj = {}
  for key, value in content:
    obj[key] = {'Common': "",
                "Uncommon": '',
                "Rare": '',
                "Incomparable": '',
                "Epic": '',
                "Other": []}
    for v in value:
      if v[1] in obj[key] and obj[key][v[1]] == '':
        obj[key][v[1]] = v[0]
      else:
        obj[key]["Other"].append(v[0])
  return obj

def build_icon_table(icon_ids):
  nl_list = []
  for i in icon_ids:
    nl_list.append([i, wikihelper.categorize_icon(i.split('-')[1])])
  base_icons = list(dict.fromkeys([a.split('-')[0] for a in sorted(icon_ids)]))
  nl_all = {}
  for i in base_icons:
    nl_all[i] = [a for a in nl_list if a[0].split('-')[0]==i]
    nl_all[i].sort(key=lambda x: (len(x[0]), x[0]))
  
  table_string = ""
  table_data = create_row(nl_all.items())
  longest_other = 0
  for o, vals in table_data.items():
    if len(vals["Other"]) > longest_other:
      longest_other = len(vals["Other"])

  for i, row in enumerate(table_data.items(), start=1):
    table_string += '|-\n'
    for a in row[1]:
      if type(row[1][a]) is list:
        while(len(row[1][a])<longest_other):
          row[1][a].append("")
        for d in row[1][a]:
          file_string = f"[[File:{d}.png]]" if d else ""
          # file_string = f"{d}" if d else ""
          table_string += f'| {file_string}\n'
      else:
        file_string = f"[[File:{row[1][a]}.png]]" if row[1][a] else ""
        # file_string = f"{row[1][a]}" if row[1][a] else ""
        table_string += f'| {file_string}\n'

  table_string = table_string[:-2] + '\n|}'

  table_prefix = """{| Class="altRowsMed centerTable"
! colspan=""" + str(6+longest_other) + """ | Generic Icons
|-
! width=50px  | Comm
! width=50px  | Uncom
! width=50px  | Rare
! width=50px  | Incom
! width=50px  | Epic"""
# ! width=50px  | Cosmetic
# ! width=50px  | Incomp_Aud
# ! width=50px  | Rare_Rep
# ! width=50px  | Incomp_Rep
# ! width=50px  | Unknown?

  for e in range(longest_other):
    table_prefix += '\n! width=50px  | Other'

  table_string = table_prefix + '\n' + table_string
  return table_string

import os
try:
  os.mkdir("icon_tables")
except OSError as e:
  print(e)

for k, v in icon_dict.items():
  if type(v) is list:
    table = build_icon_table(list(dict.fromkeys(v)))
    with open(f"icon_tables/{k}.txt", 'a+', encoding='utf8') as outfile:      
      outfile.seek(0)
      if outfile.read() == table:
        print("Is same content")
      else:        
        outfile.write(table)
        outfile.truncate()
  else:
    for i,j in v.items():
      table = build_icon_table(list(dict.fromkeys(j)))
      with open(f"icon_tables/{k}_{i}.txt", 'a+', encoding='utf8') as outfile:
        outfile.seek(0)
        if outfile.read() == table:
          print("Is same content")
        else:          
          outfile.write(table)
          outfile.truncate()