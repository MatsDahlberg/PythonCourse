#!/usr/bin/env python
import sqlite3 as lite
import numpy as np
import scipy

# Create a connection to the database
con = lite.connect('rpkm.db')
cur = con.cursor() 

sSql = "delete from expression_distance"
# Clear old data
cur.execute(sSql)
con.commit()

# Create a new table the will contain the full distance matrix
try:
    cur.execute("""CREATE TABLE expression_distance (
    sample TEXT,
    other_sample TEXT,
    distance REAL)""")
except:
    pass # Ignore any errors (if you run this script multiple times)


# Grab the all *_rel values from the wangsandberg table
sSql = """select uhrlowcov_rel, brainlowcov_rel, adipose_rel, brain_rel, breast_rel, colon_rel,
          heart_rel, liver_rel, lymphnode_rel, skelmuscle_rel, testes_rel, cerebellum1_rel,
          cerebellum2_rel, cerebellum3_rel, cerebellum4_rel, cerebellum5_rel, cerebellum6_rel,
          mcf7_rel, bt474_rel, hme_rel, mb435_rel, t47d_rel from wangsandberg order by ensg"""
cur.execute(sSql)
rows = cur.fetchall()


saSamples = ("uhrlowcov_rel", "brainlowcov_rel", "adipose_rel", "brain_rel", "breast_rel", "colon_rel", "heart_rel", "liver_rel", "lymphnode_rel", "skelmuscle_rel", "testes_rel", "cerebellum1_rel", "cerebellum2_rel", "cerebellum3_rel", "cerebellum4_rel", "cerebellum5_rel", "cerebellum6_rel", "mcf7_rel", "bt474_rel", "hme_rel", "mb435_rel", "t47d_rel")
iNrOfGenes = len(rows)
iNrOfSamples = len(saSamples)
"""
The matrix D will contain all the normalized RPKM values that we have in the wangsandberg table
It will look lie this:
sample1, rpkm_gene1, rpkm_gene2, ..., rpkm_gene23115
sample2, rpkm_gene1, rpkm_gene2, ..., rpkm_gene23115
...
sample22, rpkm_gene1, rpkm_gene2, ..., rpkm_gene23115
"""
D = scipy.zeros([iNrOfSamples, iNrOfGenes])   # Initilize to all zeros
for sample in range(iNrOfSamples):
    for gene in range(iNrOfGenes):
        if rows[gene][sample] is None or np.isnan(float(rows[gene][sample])):  # Ugly but I know no other means!
            D[sample][gene] = 0
        else:
            D[sample][gene] = rows[gene][sample]


# We only need to calculate one half of the matrix, but since it is only 22x22 distances we don't care.
for i in range(iNrOfSamples):
    for j in range(iNrOfSamples):
        if i != j:
            distance = np.linalg.norm(D[i]-D[j]) # Numpy function to calculate the Euclidian distance between 2 vectors
            sSql = """insert into expression_distance (sample, other_sample, distance)
            values('%s', '%s', '%s')""" % (saSamples[i], saSamples[j], distance)
            slask = cur.execute(sSql)
con.commit()


cur.execute("select * from expression_distance where sample = 'brain_rel' order by distance asc")
# Just as a test we see what tissues have the closest expression profile to brain
rows = cur.fetchall()
print rows
