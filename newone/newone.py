"""TO-DO: Write a description of what this XBlock is."""
import json
import pkg_resources
import datetime
import mysql.connector
import urllib2

from xblock.core import XBlock
from xblock.fields import Scope, Integer, String
from xblock.fragment import Fragment
from SPARQLWrapper import SPARQLWrapper, JSON, XML, N3, RDF
import settings as s


class NewOneXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """
    arr=[]
    arr_links=[]
    arr_description = []
    sprql_arr=[]
    
    # display name for xblock
    """display_name = String(
        display_name="Display Name",
        help="This name appears in the horizontal navigation at the top of the page.",
        scope=Scope.settings,
        default="Image Explorer"
    )"""
    
    sparql_search = String(
        default=None, scope=Scope.user_state_summary,
        help="shows next nuber",
    )
    but = String(
        default=None, scope=Scope.user_state_summary,
        help="shows next nuber",
    )
    count = String(
        default=None, scope=Scope.user_state_summary,
        help="A simple counter, to show something happening",
    )
    sprql = String(
        default=0, scope=Scope.user_state_summary,
        help="shows next nuber",
    )

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    # TO-DO: change this view to display your data your own way.
    def student_view(self, context=None):
        """
        The primary view of the NewOneXBlock, shown to students
        when viewing courses.
        """
        # !!! Staff or Student? 
        if self.is_course_staff():
            return self.staff_view()
        # !!!    
        html = self.resource_string("static/html/newone.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/newone.css"))
        frag.add_javascript(self.resource_string("static/js/src/newone.js"))
        frag.initialize_js('NewOneXBlock')
        return frag
    
    # staff_view is not a standart function of xblock!
    def is_course_staff(self):
        return getattr(self.xmodule_runtime, 'user_is_staff', False)
        
    def staff_view(self):
        """
        Create a fragment used to display the edit view in the Studio.
        """
        html = self.resource_string("static/html/newone_edit.html")
        frag = Fragment(html.format(self=self))
        frag.add_css(self.resource_string("static/css/newone.css"))
        frag.add_javascript(self.resource_string("static/js/src/newone.js"))
        frag.initialize_js('NewOneXBlock')
        return frag
    
        
    @XBlock.json_handler
    def increment_count(self, data, suffix=''):
        """
        An example handler, which increments the data.
        """
        # Just to show data coming in...
        assert data['hello'] == 'world'
        """
        response = urllib2.urlopen('https://en.wikipedia.org/w/api.php?action=opensearch&search=tria&limit=10&namespace=0&format=json')
        temp = json.load(response)
        self.count = json.dumps(temp[1])
        """
        self.arr[:]=[]
        self.arr_description[:]=[]
        self.arr_links[:]=[]
        block_id = str(self.location.name)
        cnx = mysql.connector.connect(**s.database)
        cursor = cnx.cursor()
        cursor.execute("SELECT concept_label, concept_description,concept_URI FROM Concepts, Concept_Content_Manager WHERE block_id = '"+block_id+"' AND Concepts.concept_id = Concept_Content_Manager.concept_id;")
        data = cursor.fetchall() 
        for self.n in data:
            self.arr.append(self.n[0])
            self.arr_description.append(self.n[1])
            self.arr_links.append(self.n[2])
        self.count = json.dumps(self.arr)
        desc = json.dumps(self.arr_description)
        link = json.dumps(self.arr_links)
        return {"count": self.count,"desc":desc,"link": link}

    # Handler for live seach over local concepts and dbpedia concepts
    @XBlock.json_handler
    def live_search(self, data, suffix=''):
        self.m=data['key']
        if self.m == '':
            self.but = json.dumps('')
            desc = json.dumps('')
            link = json.dumps('')
        else:   
            self.arr[:]=[]
            self.arr_description[:]=[]
            self.arr_links[:]=[]
            
            #Local search in SQL database
            cnx = mysql.connector.connect(**s.database)
            cursor = cnx.cursor()
            cursor.execute("SELECT `concept_label`,`concept_description` FROM `Concepts` WHERE `concept_label` LIKE '"+self.m+"%' ;")
            data = cursor.fetchall() 
            for self.n in data:
                self.arr.append(self.n[0])
                self.arr_description.append(self.n[1])  
                self.arr_links.append('')
                
            response = urllib2.urlopen("https://en.wikipedia.org/w/api.php?action=opensearch&search="+self.m+"&limit=10&namespace=0&format=json")
            data = json.load(response)
            for self.n in data[1]:
                self.arr.append(self.n)
            for self.n in data[2]:    
                self.arr_description.append(self.n)
            for self.n in data[3]:  
                self.n=self.n.replace('https://en.wikipedia.org/wiki','http://dbpedia.org/page')  
                self.arr_links.append(self.n)    
                 
            self.but = json.dumps(self.arr)
            desc = json.dumps(self.arr_description)
            link = json.dumps(self.arr_links)
            block_id = str(self.location.name)
        return {"but": self.but, "desc": desc, "link": link, "block_id": block_id}
        
    # Test handler. SPARQL Endpoint connection.
    @XBlock.json_handler
    def sparql_q(self, data, suffix=''):
        self.sprql_arr[:]=[]
        self.sp=data['key']
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        sparql.setQuery("""
            SELECT DISTINCT ?item ?itemLabel
            WHERE
            {
                ?item wdt:P279 wd:Q24034552 .
                ?item rdfs:label ?itemLabel
                FILTER regex(?itemLabel, "^"""+self.sp+"""", "i")
                SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }   
            }""")
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        
        for result in results["results"]["bindings"]:
            #self.sprql_arr.append(result["item"]["value"])
            self.sprql_arr.append(result["itemLabel"]["value"])
        self.sprql = json.dumps(self.sprql_arr) 
        return {"sprql" : self.sprql}
     
    # Handler for data insert to SQL database about new concepts or add new links between concept and xblock  
    @XBlock.json_handler
    def termsListCheck(self, data, suffix=''):
        new_term = data['concept'] #concept
        
        # !!! Need to convert all symbols to readable sql and RDF format
        te = data['description']
        new_desc = te.encode('ascii', 'ignore') #concept_description
        # !!!
        
        new_link = data['link'] #concept_link
        new_id = self.location.name #block_id
        field_id = 1

        cnx = mysql.connector.connect(**s.database)
        cursor = cnx.cursor()
        cursor.execute("SELECT `concept_id` FROM `Concepts` WHERE `concept_label` = '"+new_term+"' ;")
        data = cursor.fetchall() 
        count = cursor.rowcount
        if count == 0:
            cursor.execute("INSERT INTO `Concepts` (`concept_id`, `concept_URI`, `field_id`, `concept_label`, `concept_description`) VALUES (NULL, %s, %s, %s, %s)", (new_link, field_id, new_term, new_desc))
            count = cursor.lastrowid
            cnx.commit()
            cursor.execute("INSERT INTO `Concept_Content_Manager` (`id_m`, `block_id`, `concept_id`) VALUES (NULL, %s, %s)", (new_id, count))
        else:
            term_id = data[0][0]
            cursor.execute("SELECT `id_m` FROM `Concept_Content_Manager` WHERE `concept_id` = %s AND `block_id` = %s ;" % (term_id, new_id))
            cursor.fetchall()
            if cursor.rowcount == 0:
                cursor.execute("INSERT INTO `Concept_Content_Manager` (`id_m`, `block_id`, `concept_id`) VALUES (NULL, %s, %s)", (new_id, term_id))
            else:
                new_id = 'Error'
                new_term = 'Error'
        cnx.commit()
        cursor.close() 
        cnx.close()
        
        return {"new_term" : new_term, "new_desc":new_desc,"new_link":new_link}    
            
    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("NewOneXBlock",
             """<newone/>
             """),
            ("Multiple NewOneXBlock",
             """<vertical_demo>
                <newone/>
                <newone/>
                <newone/>
                </vertical_demo>
             """),
        ]

    