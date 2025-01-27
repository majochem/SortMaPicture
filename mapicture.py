
from collections import defaultdict
from pathlib import Path

from PIL import Image

import utilities as util
from fileinfo import get_date_time_data
from utilities import get_PIL_supported_formats

supportedFormats = get_PIL_supported_formats()




class Photo:
    def __init__(self, filepath):

        #check input
        self.check_filepath(filepath)
        
        #Properties
        self._supportedFormats = supportedFormats
        self._path = Path(filepath) # path object
        
        # open file briefly to get image data
        self._img = Image.open(filepath)
        self._exif = self._img.getexif() 
        self._img.close()
        self._dateTimeStrTpl = get_date_time_data(filepath)
        self.attributes = {
            "id": int(),
            "name": self._path.name,
            "name_old": self._path.name,
            "name_new": str(), # starts empty
            "path": Path(filepath),
            "path_new": None, # starts empty
            "path_old": Path(filepath),
            "was_renamed": False,
            "date_time": self._dateTimeStrTpl.date + " " + self._dateTimeStrTpl.time,
            "YYYY": self._dateTimeStrTpl.YYYY,
            "MM": self._dateTimeStrTpl.MM,
            "DD": self._dateTimeStrTpl.DD,
            "hh": self._dateTimeStrTpl.hh,
            "mm": self._dateTimeStrTpl.mm,
            "ss": self._dateTimeStrTpl.ss,
            "file_type": self._path.suffix
            # might extend in the future if more properties are wanted
        }

    def print_attributes(self):
        for key, value in self.attributes.items():
            print(f"{key}: {value}")

        
    def check_filepath(self,filepath:str):
        errorMSG = {
            "start": "Provided filepath is not valid:",
            "notPath": "is not a valid path",
            "notFile": "is not a path to a file",
            "notImage": "file type is not a supported image"
        }

        if not Path(filepath).exists():
            raise ValueError(f"{errorMSG['start']} {errorMSG['notPath']} \n Filepath given: {filepath}")
        elif not Path(filepath).is_file():
            raise ValueError(f"{errorMSG['start']} {errorMSG['notFile']} \n Filepath given: {filepath}")
        elif Path(filepath).suffix.lower() not in supportedFormats:
            raise ValueError(f"{errorMSG['start']} {errorMSG['notImage']} \n Filepath given: {filepath}")
    
    def adjust_date_tag(self, dateTag:str) -> str:
        dateTag = dateTag.replace("YYYY", self.attributes["YYYY"])
        dateTag = dateTag.replace("MM", self.attributes["MM"])
        dateTag = dateTag.replace("DD", self.attributes["DD"])
        #DEBUG
        #DEBUG print("DateTag Function:")
        #DEBUG print(f"Name: {self.attributes['name_old']}, DateTag: {dateTag}")
        #DEBUG print(f"YYYY: {self.attributes['YYYY']} - MM: {self.attributes['MM']} - DD: {self.attributes['DD']}")
        return dateTag
    
    def adjust_time_tag(self, timeTag:str) -> str:
        print(f"TimeTag at start: {timeTag}")
        tagOut = timeTag.replace("hh", self.attributes["hh"])
        tagOut = tagOut.replace("mm", self.attributes["mm"])
        tagOut = tagOut.replace("ss", self.attributes["ss"])
        #Debug
        #DEBUG print("TimeTag Function:")
        #DEBUG print(f"Name: {self.attributes['name_old']}, TimeTag: {tagOut}")
        #DEBUG print(f"hh: {self.attributes['hh']} - mm: {self.attributes['mm']} - ss: {self.attributes['ss']}")
        return tagOut
    
    def adjust_iterator_tag(self, iteratorTag:str) -> str:
        digits = max(len(iteratorTag), len(str(self.attributes["id"]))) # iterator tag needs enough digits for maximum id value
        tagOut = str(self.attributes['id']).zfill(digits)
        return tagOut
    
    def get_file_type(self) -> str:
        return self.attributes['file_type']
    
    def generate_name(self, app:object) -> str:
        # app object must be of class App from main.py
        tagDictList = app.tagDictList
        outputName = str()
        tagList = []
        for tag in tagDictList:
            position = int(tag["index"])
            tempTagText = tag['text'] #need to write to new variable to avoid overwriting
            match tag["category"]:
                case app._categoryDate: #Date
                    tempTagText = self.adjust_date_tag(tempTagText)
                case app._categoryTime: #Time
                    tempTagText = self.adjust_time_tag(tempTagText)
                case app._categoryIterator: #Iterator
                    tempTagText = self.adjust_iterator_tag(tempTagText)
                case app._categoryTag: #Custom/Generic Tag
                    pass
                case _:
                    raise ValueError(f"Unknown tag category: {tempTagText}")
            tagList.insert(position, tempTagText)
        
        outputName = util.concat_strings(tagList, app.defaultSeparator)
        outputName= outputName + self.get_file_type() # add file suffix back in
        return outputName
    
    def setName(self, newName:str):
    # Updates all necessary attributes in case of a name change
        self.attributes['name_old'] = self.attributes['name']
        self.attributes['name'] = newName
        self.attributes['name_new'] = newName
        self.attributes['path_old'] = self.attributes['path']
        self.attributes['path'] = self.attributes['path'].with_name(newName)
        self.attributes['path_new'] = self.attributes['path']
        self.attributes['was_renamed'] = True

    def set_iterator_id(self, dateIdDict:defaultdict):
        # In the dictionary of all dates, pop the first id values for an entry matching the date_time of the photo
        self.attributes["id"] = dateIdDict[self.attributes["date_time"]].pop(0)
        

        
        