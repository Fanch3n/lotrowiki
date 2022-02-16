from PIL import Image, ImageChops
import pandas as pd

def main():
  print("Don't call directly")

if __name__ == "__main__":
  main()

BASE = '../../itemIcons/items/'

def get_image(filename):
  return Image.open(BASE+filename+'.png')

def create_icon(iconstring, basepath=BASE):
  parts = iconstring.split('-')
  if len(parts)==1:
    return get_image(parts[0])
  new_img = get_image(parts[1])
  if (len(parts)>3):
    new_img.paste(get_image(parts[3]), get_image(parts[3]))
  if (len(parts)>2):
    new_img.paste(get_image(parts[2]), get_image(parts[2]))
  new_img.paste(get_image(parts[0]), get_image(parts[0]))
  return new_img

def save_image(image, filepath):
  image.save(filepath)


# get correct wiki icon names

def get_wiki_icon(icon_id):
  icons = pd.read_csv("../../icons.csv", header=None)  
  icons = icons[[0,1]]
  iconlist = icons.values.tolist()
  result = [value for key, value in iconlist if icon_id in str(key).lower()]
  if len(result) > 1:
    print(result)
    print("Multiple results, needs checking")
  elif len(result) == 1:
    return result[0][:-4]