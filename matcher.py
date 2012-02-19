import json
import pprint
import re

def clean_string(string_value):
    new_string_value = string_value.strip().lower()
    new_string_value = new_string_value.replace ( '_', ' ' )
    new_string_value = re.sub('[^A-Za-z0-9 ]+', '', new_string_value)
    return new_string_value
    
# This method takes in a string value and performs the following formatting functions to it:
#     - converts to lower case
#     - converts '_' to spaces
#     - removes duplicate white space
#     - removes special characters '()-*+/'
#  
# After performing the following functions it splits the string into multiple strings seperate by a single space character
# An array of strings is returned
def tokenize_keywords(string_value):
    new_string_value = clean_string(string_value)
    new_string_values = new_string_value.split()
    return new_string_values
    

#### main program code

# dict to store key index for manufacturer names
manufacturer_index = {}

# dict to store product listings
manufacturer_dict = {}

# listings file handler
listings_file = open('listings.txt', 'r')

for line in listings_file:
    jsonResponse = json.loads(line)
    
    manufacturer_count = 1
    
    # get keywords in listing
    title_keywords = tokenize_keywords(jsonResponse['title'])
    
    # get keywords in manufacturer's name
    manufacturer_keywords = tokenize_keywords(jsonResponse['manufacturer'])
    
    # add product to manufacturer-dict -> product-dict structure if price data exists
    if jsonResponse['price'] : 
        # create product dict
        product_dict = {}
        product_dict['price'] = jsonResponse['price']
        product_dict['keywords'] = title_keywords
        product_dict['object'] = jsonResponse
        
        # create manufacturer index
        manufacturer_index_key = clean_string(jsonResponse['manufacturer'])
        if manufacturer_index_key not in manufacturer_index and manufacturer_index_key != '':
            manufacturer_index[manufacturer_index_key] = manufacturer_keywords
        
        # check to see if manufacturer is already there, if so add to existing product list, if not, create a new list
        if manufacturer_index_key in manufacturer_dict :
            product_dict_list = manufacturer_dict[manufacturer_index_key]
        else :
            product_dict_list = []
            
        # add product to product list
        product_dict_list.append(product_dict)
        
        # add product list to manufacturer dict
        manufacturer_dict[manufacturer_index_key] = product_dict_list

# file handler for products file
products_file = open('products.txt', 'r')
all_results_dict = {}

for line in products_file:
    jsonResponse = json.loads(line)
    product_name = clean_string(jsonResponse['product_name'])
    product_manufacturer = clean_string(jsonResponse['manufacturer'])
    
    product_name_keywords = tokenize_keywords(product_name)
    product_manufacturer_keywords = tokenize_keywords(product_manufacturer)
    
    # get matching manufacturer index from manufacturer_index dict
    # check for exact match first
    found_match = False

    if product_manufacturer in manufacturer_index :
        manufacturer_key = product_manufacturer
        found_match = True
    else :
        for listing_manufacturer_idx_key, listing_manufacturer_keywords in manufacturer_index.iteritems() :
            found_match = True
            for product_manufacturer_keyword in product_manufacturer_keywords :
                if product_manufacturer_keyword not in listing_manufacturer_keywords:
                    found_match = False
                    break

            # if still true, it means this is a match
            if found_match :
                manufacturer_key = listing_manufacturer_idx_key
                break
        if not found_match : 
            print 'No match found for product "'+product_name+"' with manufacturer name '"+product_manufacturer+"'"
     
    # Next, if matching manufacturer is found, find the matching products in manfacturer dict
    if found_match :
        found_exact_match = True
        matching_listing_product = None
            
        for listing_product_dict in manufacturer_dict[manufacturer_key] :
            for product_name_keyword in product_name_keywords :
                if product_name_keyword not in listing_product_dict['keywords']:
                    found_exact_match = False
                    break
            if found_exact_match :
                matching_listing_product = listing_product_dict
                # add to results dictionary with product name as the key
                if product_name in all_results_dict :
                    matching_listings = all_results_dict[product_name]
                else :
                    matching_listings = []
                    
                # add new results to list
                matching_listings.append(matching_listing_product['object'])
                
                all_results_dict[product_name] = matching_listings
                
results_file = open('results.txt', 'w')
results_file.write( json.dumps(all_results_dict) )

            
    