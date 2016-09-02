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
                                chapter["sequentials"].append(chapter_sequentials[1])
                            #print course_block["sequentials"]
                        
                            #chapter.append(chapter_structure)


            

            '''for one in course_structure_array:
                for two in one["course_chapters"]:
                    if (course_block["block_type"]=="chapter") and (two==course_block["block_id"]): 
                #print course_block["fields"]["display_name"]
                        chapter_structure={}
                        chapter_structure["chapter_sequentials"]=[]
                        chapter_structure["chapter_id"]=course_block["block_id"]
                        chapter_structure["chapter_name"]=course_block["fields"]["display_name"]
                        print chapter_structure'''

            #if course_block["block_type"]=="chapter":
#print json.dumps(course_structure_array[1]["course_name"])
print json.dumps(course_structure_array, sort_keys=True, indent=4, separators=(',', ': '))




                










