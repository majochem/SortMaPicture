
from collections import defaultdict, namedtuple
from heapq import heappop, heappush

import customtkinter as ctk

import utilities as util
from mapicture import Photo, supportedFormats


# Generic Listbox widget, which ctk doesn't naturally support
class File_Listbox(ctk.CTkScrollableFrame):
    def __init__(self, master):
        super().__init__(master)
        self.items = set()
        self.itemsDetails = [] 
        self.columnconfigure(0, weight=1)
        self.columnconfigure((1,2,3), weight=0)
        self.textButton = {
            "font": ('Helvetica', 14),
            "fg_color": "#405480",
            "text_color": "#FFFFFF",
            "text_color_disabled": "#FFFFFF"
        }
        self.utilityButton = {
            "font": ('Helvetica', 14, 'bold'),
            "fg_color": {
                "delete": "#6a0f0f",
                "up": "#002980",
                "down": "#002980"
            },

            "hover_color": {
                "delete": "#500b0b",
                "up": "#170080",
                "down": "#170080"
            },

            "fg_color_disabled":{
                "delete": "#775555",
                "up": "#505f80",
                "down": "#505f80"
            }
        }
    
    def add_item(self, item:str, category:str = "none"):
        if item not in self.items:
            self.items.add(item)
            itemIndex = self.itemsDetails.__len__()

            # create new entry as dict
            newEntry = {
                'index': itemIndex,
                'fullName': item,
                'name': util.get_filename(item),
                'category':category,
                'button': ctk.CTkButton(self, 
                                        text=util.get_filename(item), 
                                        state="disabled",
                                        fg_color=self.textButton["fg_color"],
                                        text_color=self.textButton["text_color"], 
                                        text_color_disabled=self.textButton["text_color_disabled"], 
                                        font=self.textButton["font"]
                                        ),
                'downButton': ctk.CTkButton(self, font=self.utilityButton["font"], text="▼", width=0),
                'upButton': ctk.CTkButton(self, font=self.utilityButton["font"], text="▲", width=0),
                'deleteButton': ctk.CTkButton(self, font=self.utilityButton["font"], text="X", width=0),

            }

            #insert into list at correct position
            #DEBUG: print(f"ItemIndex: {itemIndex}")
            self.itemsDetails.insert(itemIndex, newEntry)
            self.assign_functions(itemIndex)
            if itemIndex > 0:
                self.assign_functions(itemIndex-1) # need to update functions on second to last button
            self.rearrange_list()
    
    def assign_functions(self, index):
        index = self.itemsDetails[index]['index']
        upButton = self.itemsDetails[index]['upButton']
        downButton = self.itemsDetails[index]['downButton']
        deleteButton = self.itemsDetails[index]['deleteButton']

        #declare temp functions
        def upFunc(index):
            def _funcUp():
                self.move_item(index, "up")
            return _funcUp
        
        def downFunc(index):
            def _funcDown():
                self.move_item(index, "down")
            return _funcDown
        
        def deleteFunc(index):
            def _funcDel():
                self.delete_item(index, self.itemsDetails[index]['fullName'])
            return _funcDel

        # assign new functions
        upButton.configure(command=upFunc(index), state="normal", fg_color=self.utilityButton["fg_color"]["up"], hover_color=self.utilityButton["hover_color"]["up"])
        downButton.configure(command=downFunc(index), state="normal", fg_color=self.utilityButton["fg_color"]["down"], hover_color=self.utilityButton["hover_color"]["down"])
        deleteButton.configure(command=deleteFunc(index), state="normal", fg_color=self.utilityButton["fg_color"]["delete"], hover_color=self.utilityButton["hover_color"]["delete"])

        # special cases
        ## disable up/down buttons on top and bottom element
        if index == 0:
            upButton.configure(state="disabled", fg_color=self.utilityButton["fg_color_disabled"]["up"])
        elif index == len(self.itemsDetails)-1:
            downButton.configure(state="disabled", fg_color=self.utilityButton["fg_color_disabled"]["down"])
        ## disable delete button on protected tags
        if self.itemsDetails[index]["category"] in app._protectedTags:
            deleteButton.configure(state="disabled", fg_color=self.utilityButton["fg_color_disabled"]["delete"])
            
            

    def rearrange_list (self):
        for _index, entry in enumerate(self.itemsDetails):
            entry['index'] = _index
            entry['button'].grid(row=entry['index'], column=0, padx=1, sticky="EW")
            entry['downButton'].grid(row=entry['index'], column=1, padx=1, sticky="EW")
            entry['upButton'].grid(row=entry['index'], column=2, padx=1, sticky="EW")
            entry['deleteButton'].grid(row=entry['index'], column=3, padx=1, sticky="EW")

    def move_item(self, index:int, direction:str):
        if direction == "up":
            # check if there is an element above
            if (index-1) >= 0:
                self.swap_items(index-1, index)
            else:
                print("No items above")

        elif direction =="down":
            if (index+1) < len(self.itemsDetails):
                self.swap_items(index, index+1)
            else:
                print("No items below")
        else:
            raise ValueError(f"Invalid direction: {direction}. Needs to be 'up' or 'down'")
    
    def swap_items(self,indexA:int, indexB:int):
        
        #DEBUG print(f"Swapping item {indexA}: {self.itemsDetails[indexA]['fullName']}, with {indexB}: {self.itemsDetails[indexB]['fullName']}")
        #DEBUG print("Before:\n")
        #DEBUG self.print_item_list()

        # swap entries
        tempEntryA = self.itemsDetails[indexA] # temporarily save data from A
        self.itemsDetails[indexA] = self.itemsDetails[indexB]
        self.itemsDetails[indexB] = tempEntryA

        # update index values
        self.itemsDetails[indexA]['index'] = indexA
        self.itemsDetails[indexB]['index'] = indexB

        # Index values are now correct, but buttons still contain wrong function arguments
        self.assign_functions(indexA)
        self.assign_functions(indexB)
        self.rearrange_list()

        #DEBUG print("After: \n")
        #DEBUG self.print_item_list()
    
    def delete_item(self, index:int, item:str):

        for key in ("button", "downButton", "upButton", "deleteButton"):
            self.itemsDetails[index][key].destroy()

        self.items.remove(item)
        self.itemsDetails.pop(index)
        #DEBUG print(f"Removed: {item} at position: {index}")
        self.rearrange_list()
        #DEBUG self.print_item_list()
        # reassign all function buttons
        for _index, value in enumerate(self.itemsDetails):
            self.assign_functions(_index)

    def delete_all(self):
    #todo currently only deletes half of the items???
    # hypthesis: index is defined before deletion, but invalid after every deleted item (because the index is adjusted afterwards)


    # clear all entries from the list
        for item in self.itemsDetails[:]:
            if item["category"] in app._protectedTags:
                pass # don't remove
            else:
                for key in ("button", "downButton", "upButton", "deleteButton"): # destroy all attached buttons
                    item[key].destroy()

                self.items.remove(item['fullName'])
                self.itemsDetails.remove(item)
        self.rearrange_list() # still need to rearrange at the end to account for protected tags    
    
    def delete_category(self, category:str):
        for index, item in enumerate(self.itemsDetails):
            if item["category"] == category:
                self.delete_item(index, item["fullName"])

    def update_category(self, category:str):
        element = app.get_category_elements(category)

        for index, item in enumerate(self.itemsDetails):
            if item["category"] == category:
                self.items.remove(item["fullName"])
                self.items.add(element.dropvalue)
                item["name"] = element.dropvalue
                item["fullName"] = element.dropvalue
                item["button"].configure(text=element.dropvalue)
    
    def get_special_items(self, categoryList:list):
    # returns all items that match the provided categories
        itemList = list()
        for category in categoryList:
            for item in self.itemsDetails:
                if item["category"] == category:
                    itemList.append(item)
        return itemList
    
    def print_item_list(self):
        for index, entry in enumerate(self.itemsDetails):
            print(f"ListIndex: {index} - IndexValue: {entry['index']} - Name: {entry['name']} - Category: {entry["category"]}")

    def get_itemsDetails(self):
        return self.itemsDetails

# Main app window 
class App(ctk.CTk):
    def __init__(self):
        
        super().__init__()

        self.title("Sort Ma Picture")
        width = round(self.winfo_screenwidth() * 0.75)
        height = round(self.winfo_screenheight() * 0.75)        
        self.geometry(f"{width}x{height}")  # Set the window size
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        
        # Set up customtkinter appearance
        ctk.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"
        
        # "Constants" / variables (should not be changed)
        separators = ["", "-", "_"]
        dateComponents = ["YYYY", "MM", "DD"]
        timeComponents = ["hh", "mm", "ss"]
        self._iteratorComponents = "##"
        self._categoryDate = "date" # these strings are used to categorize individual tags and treat them differently
        self._categoryTime = "time"
        self._categoryIterator = "iterator"
        self._categoryTag = "customTag"
        self._categoryFile = "filepath"
        self._protectedTags = (self._categoryTime, self._categoryDate, self._categoryIterator) # these will be protected from removal
        self._supportedFormats = supportedFormats
        self._errorMsgFormat = {"font": ('Helvetica', 14, 'bold')}

        
        # populate lists with combinations
        dateOptions = [util.concat_strings(dateComponents, separator) for separator in separators]
        timeOptions = [util.concat_strings(timeComponents, separator) for separator in separators]

        # Attributes (could be changed)
        self.defaultSeparator = "_"
        self.fileset = set()
        self.tagDictList = []
        self.dateIdDict = defaultdict(list)
        self.customTag = False
        self.dateTag = False
        self.timeTag = False


        ###
        # Files Frame (left)
        ###

        self.filesFrame = ctk.CTkFrame(self)
        self.filesFrame.grid(row=1, column=0, pady=10, padx=10, sticky="NSWE")
        self.filesFrame.columnconfigure((0,1), weight=1)

        ## Label
        self.filesFrame._label = "Select files to rename"
        self.filesFrame.label = ctk.CTkLabel(self.filesFrame, text=self.filesFrame._label)
        self.filesFrame.label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="NEW")
        
        ## File List
        self.filesBox = File_Listbox(self.filesFrame)
        self.filesBox.grid(row=1, column=0, columnspan=3, pady=10, padx=10, sticky="NWE")

        ## File management buttons
        self.filesAddButton = ctk.CTkButton(self.filesFrame, text="Add files", command=self.select_file)
        self.filesAddButton.grid(column=2,row=2, pady=10, padx=10, sticky="E")
        self.filesClearButton = ctk.CTkButton(self.filesFrame, text="Clear all", command=self.filesBox.delete_all)
        self.filesClearButton.grid(column=1,row=2, pady=10, padx=10, sticky="E")

        ###
        # Config Frame (right)
        ###
        self.configFrame = ctk.CTkFrame(self)
        self.configFrame.grid(row=1, column=1, pady=10, padx=10, sticky="NSWE")
        self.configFrame.columnconfigure(0, weight=1)
        self.configFrame.rowconfigure((3,), weight=1)
        self.configFrame.rowconfigure((1, 2, 90, 95, 99), weight=0)

        ## Label
        self.configFrame._label = "Configure filename tags"
        self.configFrame.label = ctk.CTkLabel(self.configFrame,text=self.configFrame._label)
        self.configFrame.label.grid(row=0, sticky="NEW", pady=20, padx=10)

        ## Entry Form
        self.configTagEntry = ctk.CTkEntry(self.configFrame, placeholder_text="Enter Tag")
        self.configTagEntry.grid(row=1, pady=5, padx=20, sticky="NEW")
        self.configTagEntry.bind('<Return>', self.submit_entry)

        ## Entry Check
        self.configTagText = ctk.CTkTextbox(self.configFrame, height=0, state="normal", fg_color="transparent", border_color=None, bg_color="transparent", text_color="red")
        self.configTagText.grid(row=2, pady=5, padx=20, sticky="NEW")
        self.configTagText.insert(index="0.0", text="")
        self.configTagText.configure(state="disabled", font=self._errorMsgFormat['font'], wrap="word")

        ## Entry List
        self.configTagList = File_Listbox(self.configFrame)
        self.configTagList.grid(row=3, pady=10, padx=20, sticky="NEW")

        ## Config Extra Tags
        ### Date
        self.configDateCheck = ctk.CTkCheckBox(self.configFrame, text="Add Date Tag", command= lambda: self.toggle_special_tag(self._categoryDate))
        self.configDateCheck.grid(row=90, pady=5, padx=20, sticky="SW")
        
        def update_date(value): #value is passed automatically by the dropdown, even if unused
            self.configTagList.update_category(self._categoryDate)

        self.configDateDrop = ctk.CTkComboBox(self.configFrame, values=dateOptions, state="normal", command= update_date)
        self.configDateDrop.grid(row=91, pady=5, padx=20, sticky="SWE")
        self.configDateDrop.set(value=dateOptions[0])
        self.configDateDrop.configure(state="disabled")
        
        ### Time
        self.configTimeCheck = ctk.CTkCheckBox(self.configFrame, text="Add Time Tag", command= lambda: self.toggle_special_tag(self._categoryTime))
        self.configTimeCheck.grid(row=92, pady=5, padx=20, sticky="SW")

        def update_time(value): #value is passed automatically by the dropdown, even if unused
            self.configTagList.update_category(self._categoryTime)
        
        self.configTimeDrop = ctk.CTkComboBox(self.configFrame, values=timeOptions, state="normal", command= update_time)
        self.configTimeDrop.grid(row=93, pady=5, padx=20, sticky="SWE")
        self.configTimeDrop.set(value=timeOptions[0])
        self.configTimeDrop.configure(state="disabled") #can only disable after assigning default value
        
        ### Iterator
        #not needed for now because there is no dropdown for iterators
        """ def update_iterator(value): #value is passed automatically by the dropdown, even if unused
            self.configTagList.update_category(self._categoryIterator) """

        self.configIteratorCheck = ctk.CTkCheckBox(self.configFrame, text="Add Iterator Tag", command= lambda: self.toggle_special_tag(self._categoryIterator))
        self.configIteratorCheck.grid(row=95, pady=5, padx=20, sticky="SW")
        
        ## Submit button
        self.confirmButton = ctk.CTkButton(self.configFrame, text="Rename Files", command=self.rename_all_files)
        self.confirmButton.grid(row=99, pady=30, padx=20, sticky="S")
        


    ###
    # methods:
    ###

    # Files Frame
    
    def select_file(self):
        startdir = util.get_pictures_dir()

        files = ctk.filedialog.askopenfilenames(initialdir=startdir, filetypes=[("Images", util.concat_strings(supportedFormats, " "))])
        #DEBUG print(files)
        for file in files:
            self.filesBox.add_item(file, self._categoryFile)
    

    # Config Frame

    def submit_entry(self, event):
        if self.validate_entry():
            self.configTagList.add_item(self.configTagEntry.get(), self._categoryTag)
            
        #DEBUG print(f"Entered: {self.configTagEntry.get()}")

    def validate_entry(self) -> bool:
        entryText = self.configTagEntry.get()
        result = util.is_valid_file_tag(entryText)
        if result[0]:
            self.configTagText.configure(state="normal")
            self.configTagText.delete("0.0", 'end')
            self.configTagText.configure(state="disabled")
            return True
        else:
            self.configTagText.configure(state="normal")
            self.configTagText.delete("0.0", 'end')
            self.configTagText.insert("0.0", result[1])
            self.configTagText.configure(state="disabled")
            return False

    def get_category_elements(self, category):
    # returns alls relevant objects and values for a given category
        match category:
            case self._categoryDate:
                checkbox = self.configDateCheck
                checkvalue = checkbox.get()
                dropdown = self.configDateDrop
                dropvalue =dropdown.get()
            
            case self._categoryTime:
                checkbox = self.configTimeCheck
                checkvalue = checkbox.get()
                dropdown = self.configTimeDrop
                dropvalue =dropdown.get()
            
            case self._categoryIterator:
                checkbox = self.configIteratorCheck
                checkvalue = checkbox.get()
                dropdown = None
                dropvalue = self._iteratorComponents # not really a drop value, but hardcoded

            case _:
                raise ValueError(f"{category} is not a supported category")
        
        output = namedtuple("output", ["checkbox", "checkvalue", "dropdown", "dropvalue"])
        return output(checkbox, checkvalue, dropdown, dropvalue)
        
        
    
    def toggle_special_tag(self, tagCategory:str):
    # sets an element to 'disabled' or 'readonly' on activation of the activator element
        
        element = self.get_category_elements(tagCategory)
        checkvalue = element.checkvalue
        dropdown = element.dropdown
        dropvalue = element.dropvalue
            
        if checkvalue:
            if dropdown: #if a dropdown exists, 
                dropdown.configure(state="readonly")
            self.configTagList.add_item(dropvalue, tagCategory)

        else:
            if dropdown: 
                dropdown.configure(state="disabled")
            self.configTagList.delete_category(tagCategory)
    
    def get_new_name(self, fileName):
        newName = ""
        
        
        newName = newName + self.get_custom_tags()
        
        return newName

    def get_all_tags(self) -> list:
        tagOutput = []

        for item in self.configTagList.itemsDetails:
            tempDict = {
                "index": item["index"],
                "text": item["name"],
                "category": item["category"]
            }
            tagOutput.insert(tempDict['index'], tempDict)
        return tagOutput
    
    def get_all_photo_generator(self):
        for item in self.filesBox.itemsDetails:
            outPhoto = Photo(item["fullName"])
            yield outPhoto

    def generate_name(self, photo:Photo, tagDictList:list):
        outputName = str()
        tagList = []
        for tag in tagDictList:
            position = int(tag["index"])
            match tag["category"]:
                case self._categoryDate: #Date
                    tag["text"] = photo.adjust_date_tag(tag["text"])
                case self._categoryTime: #Time
                    tag["text"] = photo.adjust_time_tag(tag["text"])
                case self._categoryIterator: #Iterator
                    tag["text"] = photo.adjust_iterator_tag(tag["text"])
                case self._categoryTag: #Custom/Generic Tag
                    pass
                case _:
                    raise ValueError(f"Unknown tag category: {tag['text']}")
            tagList.insert(position, tag['text'])
        
        outputName = util.concat_strings(tagList, self.defaultSeparator)
        outputName= outputName + photo.get_file_type() # add file suffix back in
        return outputName


    """ def get_custom_tags(self):
        outStr = ""
        tags = []
        for index, entry in enumerate(self.configTagList.itemsDetails):
            tags.insert(index, entry["name"])
        
        for tag in tags:
            outStr = util.concat_strings(tags, self.defaultSeparator)
        
        return outStr """
    
    def update_iterator_tag(self):
        numFiles = len(self.filesBox.itemsDetails)
        tagLength = len(self._iteratorComponents)
        newTag = "#" * max(numFiles,tagLength)
        self._iteratorComponents = newTag


    # Button to start renaming
    def rename_all_files(self):
        self.update_iterator_tag()
        self.tagDictList = self.get_all_tags()
        self.get_iterator_ids()
        #DEBUG
        print(self.dateIdDict)
        
        for photo in self.get_all_photo_generator():
            photo.set_iterator_id(self.dateIdDict)
            newName = photo.generate_name(self)
            photo.setName(newName)
            photo.print_attributes()
            util.rename_file(photo.attributes['path_old'], photo.attributes['path'])
            #print(f"Would rename file: {photo.attributes['name_old']} to {photo.attributes['name_new']}{photo.attributes['file_type']}")
            #DEBUG print(f"Attributes for current photo: \nYear: {photo.attributes['YYYY']}, Minute: {photo.attributes['mm']}, Second: {photo.attributes['ss']}")
    
    def get_iterator_ids(self):
        dateHeap = []

        for photo in self.get_all_photo_generator():
            dateTime = photo.attributes["date_time"]
            heappush(dateHeap, dateTime)
        

        idCounter = 1
        while dateHeap:
            currentDateTime = heappop(dateHeap)
            self.dateIdDict[currentDateTime].append(idCounter)
            idCounter += 1
    
    




# Create the main application window
app = App()  # Initialize the window

# Run the application
app.mainloop()
