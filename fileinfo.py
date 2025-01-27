import os
from collections import namedtuple
from datetime import datetime
from pathlib import Path

from PIL import ExifTags, Image

from utilities import get_filepath

testPath = r"C:\Users\majoc\Coding\GitHub\SortMaPicture\src\test_photos\IMG_0.JPG"

supportedTags = {
    "DateTime": 306,
    "Model": 272,
    "GPSInfo": 34853
}


def main():
    filepath = get_filepath()
    """ img = Image.open(filepath)
    exif = img.getexif() """
    output = get_date_time_data(filepath)
    print(f"DateTime value: {output}")
    

def get_all_data(filepath):
    if os.path.exists(filepath):
        img = Image.open(filepath)
        exif = img.getexif()
        img.close()
        for tag, value in exif.items():
            if tag in ExifTags.TAGS:
                print("Tag: ", tag, "Name: ", ExifTags.TAGS[tag], ": ", value)
            else:
                print("Tag: ", tag, "Value: ", value)
        
    else:
        print(f"Filepath: {filepath} doesn't exist")

def get_date_time_data(filepath:str):
    with Image.open(filepath) as img:
        exif = img.getexif()
    


    exifTagID = get_exif_tag_id_from_str("DateTime")
    
    exifDateTime = get_exif_data(exif, exifTagID)

    DateTimeStrTpl = namedtuple("DateTimeStrTpl", ["date", "time", "YYYY", "MM", "DD", "hh", "mm", "ss"])

    if exifDateTime: #check if Date taken is in exiff data
        exifDate, exifTime = exifDateTime.split()
        YYYY,MM,DD = exifDate.split(":")
        hh,mm,ss = exifTime.split(":")
        output = DateTimeStrTpl(exifDate, exifTime, YYYY, MM, DD, hh, mm, ss)
    else: # if not take "file created" data
        path = Path(filepath)
        sysCreationTime = path.stat().st_birthtime # time in seconds
        sysDateTime = datetime.fromtimestamp(sysCreationTime)
        YYYY = str(sysDateTime.year)
        MM = str(sysDateTime.month).zfill(2) # make sure it's always a 2 character string
        DD = str(sysDateTime.day).zfill(2)
        hh = str(sysDateTime.hour).zfill(2)
        mm = str(sysDateTime.minute).zfill(2)
        ss = str(sysDateTime.second).zfill(2)
        output = DateTimeStrTpl(f"{YYYY}:{MM}:{DD}", f"{hh}:{mm}:{ss}", YYYY, MM, DD, hh, mm, ss)
        
    return output
    

def get_exif_tag_id_from_str(tag_str:str):
    for tag_id in ExifTags.TAGS:
        #print(f"TagID: {tag_id} - TagVal: {ExifTags.TAGS[tag_id]} - TagStr: {tag_str}")
        if ExifTags.TAGS[tag_id] == tag_str:
            return tag_id

def get_exif_data(exif, tag:int) -> str:
    try: 
        _ = ExifTags.TAGS[tag]
    except:  # noqa: E722
        raise ValueError(f"{tag} is not a valid ID for an ExifTag")
    
    for _tag, value in exif.items():
        if tag == _tag:
            return value




    

if __name__ == "__main__":
    main()