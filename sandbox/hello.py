import pymongo
from bson.objectid import ObjectId
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
course_structure["course_chapters"]=[]

#Getting array of courses with their data
for course_id in published_courses_array:
    for whole_course_document in coll.find({"_id" : course_id}, {"blocks.fields.display_name":1, "blocks.fields.children":1,"blocks.block_type":1,"blocks.definition":1}):
        for course_block in whole_course_document["blocks"]:
            if course_block["block_type"]=="course":
                course_structure["course_id"]=course_block["definition"]
                course_structure["course_name"]=course_block["fields"]["display_name"]
                for course_chapters in course_block["fields"]["children"]:
                    course_structure["course_chapters"].append(course_chapters[1])
                    #need to find chapter info by chapter id
                    
                    
                course_structure_array.append(course_structure.copy())

print course_structure_array[0]["course_chapters"]




                










