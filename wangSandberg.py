import sqlite3 as lite
import sys
import csv
import numpy as np


# Create a connection to the database
con = lite.connect('rpkm.db')

# cur is a "cursor" object that can be used to traverse the records from the result, the curser is bound to a connection
cur = con.cursor() 

# Get the database version
cur.execute('SELECT SQLITE_VERSION()')

# Fetch the result of the query
data = cur.fetchone()

# Print the result
print "SQLite version: %s" % data 


# This is what the 2 first lines of the "raw data" looks like:
#Gene   UHRLowcov	brainLowcov	adipose	brain	breast	colon	heart	liver	lymphNode	skelMuscle	testes	cerebellum1	cerebellum2	cerebellum3	cerebellum4	cerebellum5	cerebellum6	MCF7	BT474	HME	MB435	T47D	Symbol	Description
#ENSG00000000003	18.51	1.33	5.91	2.41	4.25	3.90	2.51	17.43	1.40	0.51	8.95	0.58	0.33	0.35	0.36	0.33	0.44	7.25	0.81	3.09	5.02	3.00	TSPAN6	transmembrane 4 superfamily member 6
# ... 23115 times

# Creat a table that looks as your data ( I am skipping the description column)
cur.execute("""CREATE TABLE wangsandberg (
  ensg TEXT,
  gene_name TEXT,
  uhrlowcov REAL,
  brainlowcov REAL,
  adipose REAL,
  brain REAL,
  breast REAL,
  colon REAL,
  heart REAL,
  liver REAL,
  lymphnode REAL,
  skelmuscle REAL,
  testes REAL,
  cerebellum1 REAL,
  cerebellum2 REAL,
  cerebellum3 REAL,
  cerebellum4 REAL,
  cerebellum5 REAL,
  cerebellum6 REAL,
  mcf7 REAL,
  bt474 REAL,
  hme REAL,
  mb435 REAL,
  t47d REAL)""")


# Open the data file for reading
ifile = open("WangSandberg.rpkm.txt", "rb")

# It is "tab-separated"
reader = csv.reader(ifile, delimiter='\t')

# Skip the first line of the file since that is the header
next(reader)

iCount = 0
for row in reader:
    if (iCount % 500) == 0:
        # For every 500 lines we commit the transaction to the database, otherwise the redo log will grow
        con.commit()
        print "At line: " + str(iCount)
    sSql = """insert into wangsandberg (gene_name, ensg, uhrlowcov, brainlowcov, adipose, brain, breast,
    colon, heart, liver, lymphnode, skelmuscle, testes, cerebellum1, cerebellum2, cerebellum3, cerebellum4,
    cerebellum5, cerebellum6, mcf7, bt474, hme, mb435, t47d) values
    ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
    """ % (row[23], row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9],
    row[10], row[11], row[12], row[13], row[14], row[15], row[16], row[17], row[18], row[19], row[20], row[21], row[22])
    slask = cur.execute(sSql)
    iCount += 1

# One more commit for the last lines
con.commit()

# Create an unique index on the ensg column, this will speed up inserts and selects about 100-1000 times
# important that we create the index AFTER we have inserted all the ensg IDs
cur.execute('CREATE UNIQUE INDEX ensg_unique ON wangsandberg (ensg ASC)')


# Some sample queries
cur.execute('select gene_name, ensg from wangsandberg order by ensg')
# Get all the gene symbols and the ensg numbers
rows = cur.fetchall()
print len(rows)
print rows[0][0]

cur.execute('select * from wangsandberg where brain > 10 order by brain desc' )
# Sort the table on the highest rpkm value for the brain tissue, require that the rpkm in brain should be more than 10
rows = cur.fetchall()
print len(rows)
print rows[0]
print np.asarray(rows[0][2:len(rows[0])]).max()
print np.asarray(rows[0][2:len(rows[0])]).mean()
print np.asarray(rows[0][2:len(rows[0])]).min()


# Create a new column for each tissue type
cur.execute("alter table wangsandberg add column uhrlowcov_rel REAL")
cur.execute("alter table wangsandberg add column brainlowcov_rel REAL")
cur.execute("alter table wangsandberg add column adipose_rel REAL")
cur.execute("alter table wangsandberg add column brain_rel REAL")
cur.execute("alter table wangsandberg add column breast_rel REAL")
cur.execute("alter table wangsandberg add column colon_rel REAL")
cur.execute("alter table wangsandberg add column heart_rel REAL")
cur.execute("alter table wangsandberg add column liver_rel REAL")
cur.execute("alter table wangsandberg add column lymphnode_rel REAL")
cur.execute("alter table wangsandberg add column skelmuscle_rel REAL")
cur.execute("alter table wangsandberg add column testes_rel REAL")
cur.execute("alter table wangsandberg add column cerebellum1_rel REAL")
cur.execute("alter table wangsandberg add column cerebellum2_rel REAL")
cur.execute("alter table wangsandberg add column cerebellum3_rel REAL")
cur.execute("alter table wangsandberg add column cerebellum4_rel REAL")
cur.execute("alter table wangsandberg add column cerebellum5_rel REAL")
cur.execute("alter table wangsandberg add column cerebellum6_rel REAL")
cur.execute("alter table wangsandberg add column mcf7_rel REAL")
cur.execute("alter table wangsandberg add column bt474_rel REAL")
cur.execute("alter table wangsandberg add column hme_rel REAL")
cur.execute("alter table wangsandberg add column mb435_rel REAL")
cur.execute("alter table wangsandberg add column t47d_rel REAL")




# Next step is to add a normalized value for each tissue and each gene
sSql = """select ensg, uhrlowcov, brainlowcov, adipose, brain, breast,
    colon, heart, liver, lymphnode, skelmuscle, testes, cerebellum1, cerebellum2, cerebellum3, cerebellum4,
    cerebellum5, cerebellum6, mcf7, bt474, hme, mb435, t47d from wangsandberg order by ensg""" 
# Fetch all the data in the table
cur.execute(sSql)
rows = cur.fetchall()

iCount = 0
lenOfRow = len(rows[0])
for row in rows:         # This loop will calculate normalized values and insert the new data into the new columns we created
    iCount += 1
    if (iCount % 100) == 0:
        # Commit everey 500 insert to spare the redo log
        con.commit()
        print iCount
    fMax = np.asarray(row[1:lenOfRow]).max()      # higest rpkm value for this gene
    if fMax == 0:
        # If there are no values for the gene, then we skip it and take the next one
        continue
    row2 = [float(x) for x in row[1:lenOfRow]]  # copy the values for this gene
    row2 /= fMax     # Divide all values with highest

    # Update the database with the normalized values
    sSql = """update wangsandberg set uhrlowcov_rel='%s', brainlowcov_rel='%s', adipose_rel='%s', brain_rel='%s', breast_rel='%s',
    colon_rel='%s', heart_rel='%s', liver_rel='%s', lymphnode_rel='%s', skelmuscle_rel='%s', testes_rel='%s', cerebellum1_rel='%s',
    cerebellum2_rel='%s', cerebellum3_rel='%s', cerebellum4_rel='%s', cerebellum5_rel='%s', cerebellum6_rel='%s', mcf7_rel='%s',
    bt474_rel='%s', hme_rel='%s', mb435_rel='%s', t47d_rel='%s' where ensg = '%s'
    """ % (row2[0], row2[1], row2[2], row2[3], row2[4], row2[5], row2[6], row2[7], row2[8], row2[9], row2[10], row2[11], row2[12],
    row2[13], row2[14], row2[15], row2[16], row2[17], row2[18], row2[19], row2[20], row2[21], row[0])
    slask = cur.execute(sSql)
# Commit the last bunch of inserts
con.commit()


cur.execute('select gene_name, ensg, liver, liver_rel from wangsandberg where liver_rel=1 order by liver desc')
# Get all the genes that have the higest expression in the liver tissue
rows = cur.fetchall()
print len(rows)
print rows[0]
