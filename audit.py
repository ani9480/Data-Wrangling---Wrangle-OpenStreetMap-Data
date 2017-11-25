import xml.etree.cElementTree as ET
from collections import defaultdict
import re
import pprint

OSMFILE = "sample_mumbai.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)


expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road", 
            "Trail", "Parkway", "Commons"]

unwanted = ["govandi" , "World" , "compound" ,"Powai", "Multiplex", "Gokuldham"]

# UPDATE THIS VARIABLE

#creating mapping for street, cuisines and bank names
mapping = { "St": "Street",
            "St.": "Street",
            "Rd." : "Road",
            "Rd" : "Road",
            "Ave" : "Avenue",
            "stn" : "Station",
            "naka" : "Toll",
            "Naka" : "Toll",
            "Restauran" : "Restaurant"
            }

cuisine_mapping = {"burger" : "American",
                   "pizza" : "Italian",
                   "coffee" : "Italian",
                   "regional": "Maharashtrian",
                   "cake" : "Pastry",
                   "vegetarian":"Indian",
                   "coffee_shop" : "Italian",
                   "bread amlet" : "Indian",
                   "all_types_of_food": "Indian",
                   "indian_aagri": "Indian",
                   "international" : "continental"
    
                   }



bank_mapping = {"Greater" : "Greater Bombay Co-operative Bank",
                "Union" : "Union Bank of India ",
                "State" : "State Bank of India",
                "Dena" : "Dena Bank",
                "HDFC" : "HDFC Bank",
                "Kotak" : "Kotak Mahindra Bank",
                "Central": "Central Bank of India",
                "Karnataka": "Karnataka Bank",
                "HSBC" : "HSBC Bank",
                "SBI" : "State Bank of India",
                "Raheja" : "Raheja Classique Bank",
                "Punjab" : "Punjab National Bank",
                "AXIS" : "AXIS Bank"
               }

#creating a procedure audit_street_type for cleaning the street names

def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)            # using regex to get the street name 
   
    if m:
        street_type = m.group()
        if street_type not in expected and not street_type.isdigit() and street_type not in unwanted:
            if ',' not in street_type:
                if street_type == 'Maharashtra':
                    street_types["Road"].add(street_name)
                else:
                    street_types[street_type].add(street_name)
            else:
                pos_type = street_type.find(',')
                pos_name = street_name.find(',')
                
                street_type = street_type[:pos_type]
                street_name = street_name[:pos_name]
                #print (street_name)
                
                street_types[street_type].add(street_name)
    


def is_street_name(elem):
    return (elem.attrib['k'] == "addr:street")


def audit(osmfile):
    osm_file = open(osmfile, encoding="utf8")
    street_types = defaultdict(set)
    for event, elem in ET.iterparse(osm_file, events=("start",)):

        if elem.tag == "node" or elem.tag == "way":
            for tag in elem.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    osm_file.close()
    return street_types


#defining procedures for cleaning and updating name field, telephone field, cuisines and bank names field.

def update_name(name, mapping):

    # YOUR CODE HERE
    last_word = street_type_re.search(name)
    last_word = (last_word.group(0))
    if (last_word) in (mapping.keys()):
        
        name = name.replace(last_word, mapping[last_word])
        #print(name)
    return name

def update_telephone_no(nos):
    mod_num=''
    if '/' in nos:
                 
        splittednmbers=re.split('/',nos)
        #print(splittednmbers)
        value=[]
        for c in splittednmbers:
            b=''
            
            c=re.split('[^0-9]',c)
            for i in c:
                b = b + i
            if '91' not in b[0:2]:    
                value.append('+9122' + b)
            else:
                value.append('+' + b)
        return(value)
      
    else:
        nos= re.split('[ ()-]',nos)
        for num in nos:
            mod_num = mod_num + num
            
        
        length = len(mod_num)
        rem = length - 10
        mod_num =  '+91' +  mod_num[rem:]
        return (mod_num)
        
def update_food(items):
    
    
    if ';' in items:
        new_cuisine = re.split('[;]',items)
        if 'asian' in new_cuisine or 'french' in new_cuisine:
            return('continental')
        elif 'indian' in new_cuisine:
            return('indian')
        elif 'american' in new_cuisine:
            return('american')
            
    elif items in cuisine_mapping:
        return(cuisine_mapping[items])
    else:
        return(items)
    
    
def update_bank_name(name):
    pos = name.find(" ",1)
    #print(pos)
    if pos != -1:
        first_word = name[:pos]
        if first_word in bank_mapping:
            return bank_mapping[first_word]
        else:
            return name
    elif name in bank_mapping:
        return bank_mapping[name]
    else:
        return name