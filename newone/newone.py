"""TO-DO: Write a description of what this XBlock is."""
import json
import pkg_resources
import datetime
import mysql.connector

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
    sprql_arr=[]
    
    mas=['aaa','aa','a','bbb','bb','cccc','ccc','cc','c','d','dd','ddd','dddd','ddddd']
    
    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    # TO-DO: delete count, and define your own fields.
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
    count = Integer(
        default=0, scope=Scope.user_state_summary,
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
        html = self.resource_string("static/html/newone.html")
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

        self.count += 1
        return {"count": self.count}

    @XBlock.json_handler
    def sub_but(self, data, suffix=''):
        self.m=data['key']
        self.arr[:]=[]
        for self.n in self.mas:
            if self.n.startswith(self.m):
                self.arr.append(self.n)
        self.but = json.dumps(self.arr)
        return {"but": self.but}
        
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
        
    @XBlock.json_handler
    def termsListCheck(self, data, suffix=''):
        new_term = data['key']
        new_id = 111
        field_id = 1

        cnx = mysql.connector.connect(**s.database)
        cursor = cnx.cursor()
        
        cursor.execute("SELECT `concept_id` FROM `Concepts` WHERE `concept_label` = '"+new_term+"' ;")
        data = cursor.fetchall() 
        count = cursor.rowcount
        if count == 0:
            cursor.execute("INSERT INTO `Concepts` (`concept_id`, `concept_URI`, `field_id`, `concept_label`, `concept_description`) VALUES (NULL, %s, %s, %s, %s)", ('URI', field_id, new_term,'Description of concept'))
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
        #except mysql.connector.Error as err:
            #new_id = "Something went wrong: {}".format(err)
        return {"sparql_search" : new_term}    
            
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
