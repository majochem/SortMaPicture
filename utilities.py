
from pathlib import Path

from PIL import Image


def main():
    pass

def get_filepath():
    while True:
        filepath = input("Enter filepath: ")
        # Debugging feature for empty input
        #if filepath == "":
            #filepath = r"src\test_photos\IMG_0.JPG"

        if Path(filepath):
            return filepath
        elif filepath == "exit":
            return "No filepath chosen"
        else:
            print("Filepath " + filepath + " doesn't exist")

def get_pictures_dir():
    debugPath = Path(r"src\test_photos")

    if not debugPath.exists():
        userDir = Path.home()
        return Path.joinpath(userDir, "Pictures")
    else:
        return debugPath

def get_filename(filepath:str):
    path= Path(filepath)
    return path.stem + path.suffix

def rename_file(pathOld:Path, pathNew:Path):
    duplicateSuffix = 2
    while True:
        try:
            pathOld.rename(pathNew)
            break
        except FileExistsError:
            try: # try with initial duplicate value
                tempPath = add_duplicate_suffix(pathNew, duplicateSuffix)
                pathOld.rename(tempPath)
                break
            except FileExistsError: # otherwise loop until duplicate is big enough
                duplicateSuffix += 1


def add_duplicate_suffix(path:Path, counter:int)->Path:
    strCounter = "__" + str(counter)
    name = path.name
    suffix = path.suffix
    new_suffix = strCounter + suffix
    new_name = name.replace(suffix,new_suffix)
    return path.with_name(new_name)


def concat_strings(strList:list, separator):
# takes a list of words and a separator and returns the concatenated string

    outStr = ""
    for word in strList:
        if outStr == "":
            outStr = outStr + word
        else:
            outStr = outStr + separator + word
    return outStr

# Credit for this function to user Primoz on Stackoverflow thread:
# https://stackoverflow.com/questions/71112986/retrieve-a-list-of-supported-read-file-extensions-formats
def get_PIL_supported_formats():
    exts = Image.registered_extensions()
    supported_extensions = {ex for ex, f in exts.items() if f in Image.OPEN}
    return supported_extensions

def is_valid_file_tag(fileTag:str)-> tuple[bool, str]:
# checks for valid tag names, returns boolean and an errorMsg

    # criteria
    invalidChars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    invalidCharsStr = concat_strings(invalidChars,', ')
    reservedNames = ['CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 
                      'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 
                      'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9']
    
    # error messages
    errorMsgChar = f"Tags may not contain: {invalidCharsStr}"
    errorMsgSpace = "Tags may not contain spaces" # added " " because white spaces don't make much sense
    errorMsgName = " is a protected name and cannot be used in tags" # technically this isn't correcty, but it's much easier to fix it this way
    errorMsgTroll = "Your tag contains an ASCII control character. If it's in in there you know what that means and why it's bad"

    
    # Check for invalid characters
    if any(char in invalidChars for char in fileTag):
        return (False, errorMsgChar)
    
    # Check for whitespace
    if " " in fileTag:
        return (False, errorMsgSpace)
    
    # Check for protected names
    if fileTag in reservedNames:
        return (False, fileTag + errorMsgName)

    # Check for control characters
    if any(ord(char) < 32 for char in fileTag):
        return (False, errorMsgTroll)

    return (True, "Valid Entry")


    


if __name__ == "__main__":
    main()

