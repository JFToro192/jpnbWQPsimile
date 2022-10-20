import os
import pandas as pd
import geopandas as gpd
import json
import pytz
import requests
import json

class istSOSClient:
    WQP_PROCEDURES = ['CHL','TURB','TEMP']
    HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    OFFERING_NAME = "temporary"
    PROCEDURES = {
        'COMO': [
            # CHL & TSM MEAN
            'SATELLITE_CHL_TURB_CO_E',
            'SATELLITE_CHL_TURB_CO_N',
            'SATELLITE_CHL_TURB_CO_W',
            # CHL & TSM 1ST QUANTILE
            'SATELLITE_CHL_TURB_CO_E_1Q',
            'SATELLITE_CHL_TURB_CO_N_1Q',
            'SATELLITE_CHL_TURB_CO_W_1Q',
            # CHL & TSM 3RD QUANTILE
            'SATELLITE_CHL_TURB_CO_E_3Q',
            'SATELLITE_CHL_TURB_CO_N_3Q',
            'SATELLITE_CHL_TURB_CO_W_3Q',
            # CHL & TSM STANDARD DEVIATION
            'SATELLITE_CHL_TURB_CO_E_SD',
            'SATELLITE_CHL_TURB_CO_N_SD',
            'SATELLITE_CHL_TURB_CO_W_SD',
            # LSWT MEAN
            'SATELLITE_TEMP_CO_E',
            'SATELLITE_TEMP_CO_N',
            'SATELLITE_TEMP_CO_W',
            # LSWT 1ST QUANTILE
            'SATELLITE_TEMP_CO_E_1Q',
            'SATELLITE_TEMP_CO_N_1Q',
            'SATELLITE_TEMP_CO_W_1Q',
            # LSWT 3RD QUANTILE
            'SATELLITE_TEMP_CO_E_3Q',
            'SATELLITE_TEMP_CO_N_3Q',
            'SATELLITE_TEMP_CO_W_3Q',
            # LSWT STANDARD DEVIATION
            'SATELLITE_TEMP_CO_E_SD',
            'SATELLITE_TEMP_CO_N_SD',
            'SATELLITE_TEMP_CO_W_SD',
        ],
        'LUGANO': [
            # CHL & TSM MEAN
            'SATELLITE_CHL_TURB_LUG_N',
            'SATELLITE_CHL_TURB_LUG_S',
            # CHL & TSM 1ST QUANTILE
            'SATELLITE_CHL_TURB_LUG_N_1Q',
            'SATELLITE_CHL_TURB_LUG_S_1Q',
            # CHL & TSM 3RD QUANTILE
            'SATELLITE_CHL_TURB_LUG_N_3Q',
            'SATELLITE_CHL_TURB_LUG_S_3Q',
            # CHL & TSM STANDARD DEVIATION
            'SATELLITE_CHL_TURB_LUG_N_SD',
            'SATELLITE_CHL_TURB_LUG_S_SD',
            # LSWT MEAN
            'SATELLITE_TEMP_LUG_N',
            'SATELLITE_TEMP_LUG_S',
            # LSWT 1ST QUANTILE
            'SATELLITE_TEMP_LUG_N_1Q',
            'SATELLITE_TEMP_LUG_S_1Q',
            # LSWT 3RD QUANTILE
            'SATELLITE_TEMP_LUG_N_3Q',
            'SATELLITE_TEMP_LUG_S_3Q',
            # LSWT STANDARD DEVIATION
            'SATELLITE_TEMP_LUG_N_SD',
            'SATELLITE_TEMP_LUG_S_SD'     
        ],
        'MAGGIORE': [
            # CHL & TSM MEAN
            'SATELLITE_CHL_TURB_MA', 
            # CHL & TSM 1ST QUANTILE
            'SATELLITE_CHL_TURB_MA_1Q', 
            # CHL & TSM 3RD QUANTILE
            'SATELLITE_CHL_TURB_MA_3Q', 
            # CHL & TSM STANDARD DEVIATION
            'SATELLITE_CHL_TURB_MA_SD', 
            # LSWT MEAN
            'SATELLITE_TEMP_MA',
            # LSWT 1ST QUANTILE
            'SATELLITE_TEMP_MA_1Q',
            # LSWT 3RD QUANTILE
            'SATELLITE_TEMP_MA_3Q',
            # LSWT STANDARD DEVIATION
            'SATELLITE_TEMP_MA_SD',
        ]
    }

    WQP_DEFINITIONS = {
        "Time":{
            "name": "Time",
            "definition": "urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"       
        },
        "CHL":{
            "name": "water-Chl-a",
            "definition":"urn:ogc:def:parameter:x-istsos:1.0:water:Chl:a",
            "uom":"mg/m3"
        },
        "TURB":{
            "name": "water-TSS",
            "definition":"urn:ogc:def:parameter:x-istsos:1.0:water:TSS",
            "uom":"g/m3" 
        },
        "TEMP":{
            "name": "water-temperature",
            "definition":"urn:ogc:def:parameter:x-istsos:1.0:water:temperature",
            "uom":"\u00b0C"    
        },
    }
    
    def __init__(self, HOST, HEADERS, SERVICE, PROCEDURE_LAKE, ENV_FILE):
        with open(ENV_FILE, 'r') as f:
            payload = json.load(f)
        TOKEN_URL = f'{HOST}/auth/realms/istsos/protocol/openid-connect/token'
        API_ENDPOINT = f'{HOST}/istsos/wa/istsos/services/{SERVICE}'
        self.payload = payload
        self.headers = HEADERS
        self.tokenUrl = TOKEN_URL
        self.apiEndpoint = API_ENDPOINT
        self.procedures = self.PROCEDURES[PROCEDURE_LAKE]
        
    def updateBearerToken(self):
        response = requests.post(self.tokenUrl, data=self.payload, headers=self.headers)
        self.authToken = response.json()['access_token']
        self.apiCallBT()
    
    def apiCallBT(self):
        self.requestHeaders = {
            'Content-Type': 'application/json',
            'Authorization' : f'Bearer {self.authToken}'
        }

    def getProcedureIDs(self):
        ASSIGNED_SENSOR_ID = dict()
        for PROCEDURE in  self.procedures:
            print(PROCEDURE)
            url_test = f"{self.apiEndpoint}/procedures/{PROCEDURE}"
            resp = requests.get(url_test, headers=self.requestHeaders, timeout=100)
            if (resp.status_code==200):
                try:
                    ASSIGNED_SENSOR_ID[PROCEDURE] = resp.json()['data']['assignedSensorId']
                except:
                    ASSIGNED_SENSOR_ID[PROCEDURE] = ''
                    print('The procedure {} has not been provided with an ID.'.format(PROCEDURE))
            elif(resp.status_code==401 and resp.json()['message']=='Signature has expired'):
                self.updateBearerToken()
                print('Updating authentication token.\n')
                self.getProcedureIDs()
        return ASSIGNED_SENSOR_ID
    
    def getRequestSample(self, PROCEDURE):
        apiRequest = f'/operations/getobservation/offerings/temporary/procedures/{PROCEDURE}/observedproperties/:/eventtime/last'
        response = requests.get(self.apiEndpoint+apiRequest, 
                    headers = self.requestHeaders)
        data = response.json()
        if data['success'] == True:
            print(data['message'])
            data = data['data'][0]
        else:
            print(data['message'])
        
        return data
    
def updateDataRequest(df, dataSample, WQP_DEFINITIONS, WQP_PROCEDURES, PROCEDURE, STATISTIC):
    d = dataSample
    wqps = list(set(PROCEDURE.split('_')).intersection(WQP_PROCEDURES))
    print(wqps)
    
    DATE_START = pytz.utc.localize(df.date.min()).isoformat().replace('+00:00','Z')
    DATE_END = pytz.utc.localize(df.date.max()).isoformat().replace('+00:00','Z')
    print(DATE_START)
    print(DATE_END)
    d['samplingTime'] = {
        'beginPosition':DATE_START,
        'endPosition':DATE_END,
    }
    d['procedure'] = f'urn:ogc:def:procedure:x-istsos:1.0:{PROCEDURE}'
    d['observedProperty']['CompositePhenomenon']['dimension'] = str(len(wqps)+1)

    OP_COMPONENT = ["urn:ogc:def:parameter:x-istsos:1.0:time:iso8601"]
    for wqp in wqps: 
        OP_COMPONENT.append(WQP_DEFINITIONS[wqp]['definition'])
    d['observedProperty']['component'] = OP_COMPONENT 
    
    # Data Array
    d['result']['DataArray']['elementCount'] = str(len(wqps)+1)
    
    RES_DA_FIELDS = [WQP_DEFINITIONS['Time']]
    for wqp in wqps: 
        RES_DA_FIELDS.append(WQP_DEFINITIONS[wqp])
    d['result']['DataArray']['field'] = RES_DA_FIELDS
    
    if STATISTIC == 'mean':
        if 'MA' in PROCEDURE.split('_'):
            BASIN = 'MA'
        else:
            BASIN = '_'.join(PROCEDURE.split('_')[-2:])
    elif STATISTIC in ['percentile_25','percentile_75','std']:
        if 'MA' in PROCEDURE.split('_'):
            BASIN = 'MA'
        else:
            BASIN = '_'.join(PROCEDURE.split('_')[-3:-1])
    
    d['result']['DataArray']['values'] = resultsWQPvalues(df, wqps, BASIN, STATISTIC)

    return d
        

def appendStatsFile(df, out_path):
    """
        Export the statistics result to a file (append data if existing)
        df:  Pandas DataFrame exported into the .csv file
        out_path: path to the csv storing the data
    """
    out_file = out_path
    print(out_file)
    if os.path.exists(out_file):
        df.to_csv(out_file,mode='a', header=False)
    else:
        df.to_csv(out_file) 

def getGMLfeature(vector_path, procedure):
    #Retrieve GML feature from GML file polygon type
    with open(os.path.join(vector_path,f'{procedure}.gml')) as f:
        lines = f.read()
    geometry_procedure = lines.split('<ogr:geometryProperty>')[1].split("</ogr:geometryProperty>")[0]
    return geometry_procedure

def resultsWQPvalues(df, WQP_INPUT, BASIN, STATISTIC):
    RES_DA_VALUES = []
    wqps = []
    for k in WQP_INPUT:
        if k == 'CHL':
            wqps.append('CHL')
        elif k == 'TURB':
            wqps.append('TSM')
        elif k == 'TEMP':
            wqps.append('LSWT')     
    df = df.loc[df['typology'].isin(wqps)]
    dates_list = df['date'].unique()
    for d in dates_list:
        temp = [pytz.utc.localize(pd.to_datetime(d)).isoformat().replace('+00:00','Z')]
        for wqp in wqps: 
            try:
                o = df.loc[(df['date']==d)&(df['typology']==wqp)].iloc[0][f'{STATISTIC}_{BASIN}']
                temp.append(o)
            except:
                print('Missing value:', d,':',wqp,':',BASIN)
        
        RES_DA_VALUES.append(temp)
                
    return RES_DA_VALUES

#
    
    