So my ADCP request and processing scripts are in the attached zip file.  Like I said, it's kludgy, but its worked for me.

query_rawdata_server_rec_v2.py
query_rawdata_server_tel_pd8_v2.py
query_rawdata_server_tel_pd12_v2.py
process_ooi_ADCP_PD0_data_v3.py
process_ooi_ADCP_PD8_data_v2.py
process_ooi_ADCP_PD12_data_v2.py

The query_rawdata*.py search for adcp data files in the telemetered and recovered directories on the raw data server. query_rawdata_server_rec_v2.py downloads recovered data (which is PD0 format).  query_rawdata_server_tel_pd8_v2.py and query_rawdata_server_tel_pd12_v2.py downloads telemetered data (the format depends on the particular mooring).  The data go to a directory defined by the mooring ID.

The process*.py files then parse the raw files and convert the data to a netcdf file.
