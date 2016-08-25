import json
import mysql.connector
import settings as s
cnx = mysql.connector.connect(**s.database)
cursor = cnx.cursor()
block_id = str(111)
cursor.execute("SELECT concept_label FROM Concepts, Concept_Content_Manager WHERE block_id = '"+block_id+"' AND Concepts.concept_id = Concept_Content_Manager.concept_id;")
data = cursor.fetchall() 
print(data)