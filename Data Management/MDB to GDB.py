#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from tqdm.notebook import tqdm_notebook


# In[ ]:


def main():
    import arcpy
    import os

    # input and output folders
    folder_mdb = r'C:\GeoNet\mdb2gdb\test\pgdb'  # input folder
    folder_gdb = r'C:\GeoNet\mdb2gdb\test\fgdb3'  # output folder

    # set workspace to mdb folder and lst personal gdb's
    arcpy.env.workspace = folder_mdb
    pgdbs = arcpy.ListWorkspaces(workspace_type="Access")

    # loop through personal gdb's
    for pgdb in pgdbs:
        # create output empty output fgdb
        mdb_name = os.path.split(pgdb)[1]
        gdb_name = os.path.splitext(mdb_name)[0] + ".gdb"

        fgdb = os.path.join(folder_gdb, gdb_name)
        print("Create FGDB: {}".format(fgdb))
        arcpy.CreateFileGDB_management(folder_gdb, gdb_name, "CURRENT")

        # list feature datasets
        arcpy.env.workspace = pgdb
        fdss = arcpy.ListDatasets()
        fdss.append('')

        # loop through feature datasets to ceate list of RC's
        lst_rc = []
        for fds_name in fdss:
            print(" - Processing FDS: {}".format(fds_name))
            if fds_name != '':
                # create fds
                fds_mdb = os.path.join(pgdb, fds_name)
                sr = arcpy.Describe(fds_mdb).spatialReference
                arcpy.CreateFeatureDataset_management(fgdb, fds_name, sr)

                fcs = arcpy.ListFeatureClasses('*', None, fds_name)
                for fc_name in fcs:
                    fc_mdb = os.path.join(pgdb, fds_name, fc_name)
                    fc_gdb = os.path.join(fgdb, fds_name, fc_name)

                    # detect relationshipclasses
                    rc_names = arcpy.Describe(fc_mdb).relationshipClassNames
                    if len(rc_names) > 0:
                        for rc_name in rc_names:
                            print "    - rc_name:", rc_name
                            rc_mdb = os.path.join(pgdb, fds_name, rc_name)
                            rc_gdb = os.path.join(fgdb, fds_name, rc_name)
                        lst_rc.append([rc_mdb, rc_gdb])


        # copy relationship classes
        print(" - Copy Relationshipclasses")
        for rc in lst_rc:
            rc_mdb = rc[0]
            rc_name = os.path.split(rc_mdb)[1]
            rc_gdb = rc[1]
            print("   - Copy RC: {}".format(rc_name))
            arcpy.Copy_management(rc_mdb, rc_gdb)

        # copy featureclasses (that do not exist yet)
        print(" - Copy Featureclasses")
        for fds_name in fdss:
            print(" - Processing FDS: {}".format(fds_name))
            if fds_name != '':
                # create fds
                fds_mdb = os.path.join(pgdb, fds_name)
                sr = arcpy.Describe(fds_mdb).spatialReference

                fcs = arcpy.ListFeatureClasses('*', None, fds_name)
                for fc_name in fcs:
                    fc_mdb = os.path.join(pgdb, fds_name, fc_name)
                    fc_gdb = os.path.join(fgdb, fds_name, fc_name)
                    if arcpy.Exists(fc_gdb) == False:
                        print("   - Copy FC: {}".format(fc_name))
                        arcpy.Copy_management(fc_mdb, fc_gdb)

        # copy stand alone tables
        print(" - Copy Standalone tables")
        tbls = arcpy.ListTables()
        for tbl_name in tbls:
            tbl_mdb = os.path.join(pgdb, tbl_name)
            tbl_gdb = os.path.join(fgdb, tbl_name)
            if arcpy.Exists(tbl_gdb) == False:
                print("   - Copy TBL: {}".format(tbl_name))
                arcpy.Copy_management(tbl_mdb, tbl_gdb)


if __name__ == '__main__':
    main()‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍‍

