import xml.etree.cElementTree as ET
from pprint import pprint
import re
import codecs
import json

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]
    

##the procedure below helps in filtering the fields with proper naming conventions and data. it also creates the JSON object 
##structure for each node and way which we need for our analysis purpose
    
def shape_element(element):
    node = {}
    address={}
    if element.tag == "node" or element.tag == "way":
        #print element.attrib
        #YOUR CODE HERE
        node["type"] = element.tag
        node["created"] = {}
        node["pos"] =[ None , None]
        
        for key,val in element.attrib.items():
            
            if key in CREATED:
                
                node["created"].update({key:val})
            elif key == 'lat':
                node["pos"][0] = float(element.get(key))
            elif key == 'lon':
                node["pos"][1] = float(element.get(key))
            else:
                node[key] = element.get(key)
                
                
        
        a= []
        
        for i in element:
            
            if i.tag == 'nd':
                
                for refs,val in i.attrib.items():
                    #print(val)
                    a.append(val)
            node["node_refs"] = a
            
            if i.tag == 'tag':
                
                node["address"] = {}
                empty_dict = {}
               
                for loc,val in i.attrib.items():
                    
                    if val.startswith("addr:") and lower_colon.match(val):
                                
                                key, value = val.split(":")
                                #empty_dict = dict.fromkeys([value])
                                new_val = update_name(i.attrib['v'], mapping)
                                
                                if value == 'city':
                                    if new_val.lower() != 'mumbai':
                                        address[value] = 'Mumbai'
                                        address["location"] = new_val
                                else:
                                    address[value] = new_val
                                
                    elif "addr:" not in val and lower.match(val) and loc != 'v':
                        if val.lower() == "phone" or val.lower() == 'fax':
                            node[val] = update_telephone_no(i.attrib['v'])
                            
                        elif val.lower() == "cuisine":
                            node[val] = update_food(i.attrib['v'])
                        elif val.lower() == "amenity":
                            if 'atm' in i.attrib['v'].lower():
                                node[val] = i.attrib['v']
                                node["atm"] = "yes"
                            else:
                                node[val] = i.attrib['v']
                        else:
                            node[val] = i.attrib['v']
                    
                    elif "name" in val:
                        
                        if len(i.attrib['v']) != -1:
                            #print (i.attrib['v'])
                            new_name = update_name(i.attrib['v'], mapping)
                            node[val] = new_name
                            
                    elif problemchars.match(val):
                        pass
                                
                node["address"] = address   
                
        if "operator" in node and "name" not in node:
            node["name"] = node["operator"]
        
        if "brand" in node and "name" not in node:
            node["name"] = node["brand"]
            
        if "name" in node:
            if "atm" in node:
                #print(node["name"])
                node["name"] = update_bank_name(node["name"])  
                
        
        
    else:
        return None
    return node

def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return (data)