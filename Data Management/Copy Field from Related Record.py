import arcpy

edit = arcpy.da.Editor(r'D:\4558-_Tech_Monitoring_PPDR1\754670033e1742368a57af93d6d41047.gdb')

edit.startEditing(False, True)
edit.startOperation()




fc = r'D:\4558-_Tech_Monitoring_PPDR1\754670033e1742368a57af93d6d41047.gdb\usaceAssessment'
fc2 = r'D:\4558-_Tech_Monitoring_PPDR1\754670033e1742368a57af93d6d41047.gdb\_4558__Tech_Monitoring_PPDR'

fields2 = ['globalid','street']
fields = ['parentglobalid','parcelStreet']

with arcpy.da.UpdateCursor(fc, fields) as cursor:
    for row in cursor:
        with arcpy.da.SearchCursor(fc2, fields2) as cursor2:
            for row2 in cursor2:
                if row[0] == row2[0]:
                    row[1] = row2[1]
                    cursor.updateRow(row)


