import sqlite3 as lite

var_school_id = '105'
var_bus_id = '020'
var_driver_name = 'Ankit Kurani'
var_driver_contact_no = '8408845374'
var_bus_reg_no = 'MH-12-JI-6392'
var_attendant_name = 'Rishi Padia'
var_attendant_contact_no = '9011004706'

con = lite.connect('local_data.db')

with con:

        
        cur = con.cursor()
        cur.execute("DROP TABLE IF EXISTS bus_details")    
        cur.execute("CREATE TABLE bus_details(school_id TEXT,bus_id TEXT,driver_name TEXT, driver_contact_no TEXT, bus_reg_no TEXT, attendant_name TEXT, attendant_contact_no TEXT)")
        cur.execute("INSERT INTO bus_details VALUES(?,?,?,?,?,?,?)", (var_school_id,var_bus_id,var_driver_name, var_driver_contact_no, var_bus_reg_no, var_attendant_name, var_attendant_contact_no))
            
        cur.execute("SELECT * FROM bus_details")

        rows = cur.fetchall()

        for row in rows:
                print str(row)
