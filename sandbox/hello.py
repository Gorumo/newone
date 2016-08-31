import pymongo
from bson.objectid import ObjectId
import json
#Connection to MongoDB and DB & Collection choice
conn = pymongo.Connection('localhost', 27017)
db = conn.edxapp
coll = db.modulestore.structures
published = db.modulestore.active_versions

#array of ObjectID of all active courses
published_courses_array=[]
for published_courses in published.find({}):
    published_courses_array.append(published_courses["versions"]["published-branch"])
#print published_courses_array



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
course_structure = {}


#Getting array of courses with their data
for course_id in published_courses_array:
    for whole_course_document in coll.find({"_id" : course_id}, {"blocks.fields.display_name":1, "blocks.fields.children":1,"blocks.block_type":1,"blocks.definition":1}):
        for course_block in whole_course_document["blocks"]:
            if course_block["block_type"]=="course":
                course_structure["course_chapters"]=[]
                course_structure["course_id"]=course_block["definition"]
                course_structure["course_name"]=course_block["fields"]["display_name"]
                #print course_structure["course_name"]
                #print json.dumps(course_block["fields"]["children"][0], sort_keys=True, indent=4, separators=(',', ': '))
                for course_chapterss in course_block["fields"]["children"]:
                    #print course_chapterss[1]
                    course_structure["course_chapters"].append(course_chapterss[1])

                    
                    #print course_chapters
                        #need to find chapter info by chapter id
                        
                        
                course_structure_array.append(course_structure.copy())
                #print course_structure["course_chapters"]
print json.dumps(course_structure_array[2]["course_name"])
print json.dumps(course_structure_array[3]["course_chapters"], sort_keys=True, indent=4, separators=(',', ': '))




                










