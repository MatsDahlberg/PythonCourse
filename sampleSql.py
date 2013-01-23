import sqlite3 as lite
import numpy as np
import scipy


# Create a connection to the database
con = lite.connect('rpkm.db')

# cur is a "cursor" object that can be used to traverse the records from the result,
# the curser is bound to a connection
cur = con.cursor() 


# Some sample queries
cur.execute('select gene_name, ensg from wangsandberg order by ensg')
# Get all the gene symbols and the ensg numbers
rows = cur.fetchall()
print len(rows)
print rows[0][0]

cur.execute('select * from wangsandberg where brain > 10 order by brain desc' )
# Select the rows with rpkm > 10 for brain and sort the result with higest brain rpkm at the top

rows = cur.fetchall()
iNrOfColumns = len(rows[0])
print len(rows)
print rows[0]
print np.asarray(rows[0][2:iNrOfColumns]).max()
print np.asarray(rows[0][2:iNrOfColumns]).mean()
print np.asarray(rows[0][2:iNrOfColumns]).min()



cur.execute('select gene_name, ensg, liver, liver_rel from wangsandberg where liver_rel=1 order by liver desc')
# Get all the genes that have the higest expression in the liver tissue
rows = cur.fetchall()
print len(rows)
print rows[0]

