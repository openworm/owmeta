TriX_data = """<?xml version='1.0' encoding='UTF-8'?>
<TriX xmlns='http://www.w3.org/2004/03/trix/trix-1/'>
	<graph>
		<uri>http://openworm.org/entities/molecules/6de7e55334036bbe7ca2e364ad00372db26ddfe3b43fed5acab1987c</uri>
		<triple>
			<uri>http://somehost.com/s</uri>
			<uri>http://somehost.com/p</uri>
			<uri>http://somehost.com/o</uri>
		</triple>
	</graph>
</TriX>
"""
Trig_data = """
@prefix dc: <http://purl.org/dc/terms/> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
<http://example.org/alice> dc:publisher "Alice" .
GRAPH <http://example.org/bob>
{
   [] foaf:name "Bob" ;
      foaf:mbox <mailto:bob@oldcorp.example.org> ;
      foaf:knows _:b .
}
GRAPH <http://example.org/alice>
{
    _:b foaf:name "Alice" ;
        foaf:mbox <mailto:alice@work.example.org>
}
"""
