import pymongo
import re
from bson.objectid import ObjectId
import json
import MySQLdb
sql_db = MySQLdb.connect(host="localhost",    
                     user="root",        
                     passwd="",  
                     db="edxapp")   
edxapp = sql_db.cursor()

#Connection to MongoDB and DB & Collection choice
conn = pymongo.Connection('localhost', 27017)
db = conn.edxapp
coll = db.modulestore.structures
published = db.modulestore.active_versions
defin = db.modulestore.definitions

#array of ObjectID of all active courses
published_courses_array=[]
for published_courses in published.find({}):
    published_courses_array.append(published_courses["versions"]["published-branch"])
#print published_courses_array

definitions_array=[]

#mongo query's
''' 
db.getCollection('modulestore.structures').
find({"blocks.block_id" : "d8a6192ade314473a78242dfeedfbf5b", "blocks.block_type" : "course"}, 
{"blocks.fields.display_name":1, "blocks.fields.children":1, "blocks.block_type":1, 
 "blocks.definition":1})
//db.getCollection('modulestore.structures').distinct("blocks.definition", {"blocks.block_id" : "d8a6192ade314473a78242dfeedfbf5b","blocks.block_type" : "course"})
'''



#automatic Collection creation by data insert
'''import datetime
post = {"author": "Mike", "text": "My first blog post!", "tags": ["mongodb", "python", "pymongo"],"date": datetime.datetime.utcnow()}
coll.insert(post)'''
course_structure_array=[]



#Getting array of courses with their data
for course_id in published_courses_array:
    for whole_course_document in coll.find({"_id" : course_id}, {"blocks.fields.display_name":1, "blocks.fields.children":1,"blocks.block_type":1,"blocks.definition":1,"blocks.block_id":1 }):
        for course_block in whole_course_document["blocks"]:
            if course_block["block_type"]=="course":
                course_structure = {}
                course_structure["course_chapters"]=[]
                #!!!!!!!!!Narrow space, because block_id of course is "course", not objectID
                course_structure["course_id"]=course_block["block_id"]
                course_structure["course_name"]=course_block["fields"]["display_name"]
                for course_chapters in course_block["fields"]["children"]:
                    chapter_structure1={}
                    chapter_structure1["chapter_id"]=course_chapters[1]
                    course_structure["course_chapters"].append(chapter_structure1)
                course_structure_array.append(course_structure.copy())
                print "--------------Next course-----------------"
        
        for course_block in whole_course_document["blocks"]:
            if course_block["block_type"]=="chapter":
                for course in course_structure_array:
                    for chapter in course["course_chapters"]:
                        if course_block["block_id"] == chapter["chapter_id"]:
                            #print course_block["block_id"]
                            chapter["chapter_name"]=course_block["fields"]["display_name"]
                            chapter["sequentials"]=[]
                            for chapter_sequentials in course_block["fields"]["children"]:
                                sequential_structure={}
                                sequential_structure["sequential_id"]=chapter_sequentials[1]
                                chapter["sequentials"].append(sequential_structure)

        for course_block in whole_course_document["blocks"]:
            if course_block["block_type"]=="sequential":
                for course in course_structure_array:
                    for chapter in course["course_chapters"]:
                        for sequential in chapter["sequentials"]:
                            if course_block["block_id"] == sequential["sequential_id"]:
                                sequential["sequential_name"]=course_block["fields"]["display_name"]
                                sequential["verticals"]=[]
                                for sequential_verticals in course_block["fields"]["children"]:
                                    vertical_structure={}
                                    vertical_structure["vertical_id"]=sequential_verticals[1]
                                    sequential["verticals"].append(vertical_structure)

        for course_block in whole_course_document["blocks"]:
            if course_block["block_type"]=="vertical":
                for course in course_structure_array:
                    for chapter in course["course_chapters"]:
                        for sequential in chapter["sequentials"]:
                            for vertical in sequential["verticals"]:
                                if course_block["block_id"] == vertical["vertical_id"]:
                                    vertical["units"]=[]
                                    try:
                                        vertical["vertical_name"]=course_block["fields"]["display_name"]
                                    except:
                                        print "There's no display_name in this vertical"
                                    for vertical_units in course_block["fields"]["children"]:
                                        unit_structure={}
                                        unit_structure["unit_type"]=vertical_units[0]
                                        unit_structure["unit_id"]=vertical_units[1]
                                        for units_content in whole_course_document["blocks"]:
                                            if units_content["block_id"] == unit_structure["unit_id"] and units_content["block_type"] == "html":
                                                #ObjectID for Content from definitions collection
                                                for definitions in defin.find({"_id":ObjectId(units_content["definition"])}):
                                                    try:
                                                        unit_structure["data"]=re.sub(r'(\<(/?[^>]+)>)', '', definitions["fields"]["data"]) 
                                                    except:
                                                        unit_structure["data"]=""
                                                    vertical["units"].append(unit_structure)
                                                                                                                                            #INSERT NAME OF XBLOCK!!!
                                            if units_content["block_id"] == unit_structure["unit_id"] and units_content["block_type"] == "newone":
                                                try:
                                                    #unit_structure["data"]="xblock"
                                                    edxapp.execute("SELECT value FROM courseware_xmoduleuserstatesummaryfield WHERE usage_id LIKE '%"+unit_structure["unit_id"]+"';")
                                                    for row in edxapp.fetchall():
                                                        unit_structure["data"]=row[0] 
                                                except:
                                                    unit_structure["data"]=""
                                                vertical["units"].append(unit_structure)

                                        


                



#5690cbf1457ebc0ba8429d4d - fail
#5690d6a8457ebc0ba9429d52
#5690d8ac457ebc0ba9429fb5



print json.dumps(course_structure_array, sort_keys=True, indent=4, separators=(',', ': '))
