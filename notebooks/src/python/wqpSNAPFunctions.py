"""
1. IMPORTS
"""
import math
import os
from datetime import datetime
import pandas as pd
import snappy
from snappy import (ProgressMonitor, VectorDataNode,
                    WKTReader, ProductIO, PlainFeatureFactory,
                    SimpleFeatureBuilder, DefaultGeographicCRS,
                    ListFeatureCollection, FeatureUtils,
                    WKTReader, HashMap, jpy, GPF)

###
# For more info on the parameters for each SNAP function use the cmd:
# > gpt -h
# For specific functions
# > gpt Subset -h
###

class snapProduct:
    def __init__(self, path, bbox):
        self.path = path
        self.name = path.split('/')[-2].split('.')[0]
        self.bbox = bbox # ROI bounding box

    def readSNAPProduct(self):
        # Read the product
        df = ProductIO.readProduct(self.path)
        self.product = df
        # Get the bounding box for the product
        minLon_p, maxLon_p, minLat_p, maxLat_p = getExtent(df)
        self.bbox_prod = {
            'minLat' : minLat_p,
            'maxLat' : maxLat_p,
            'minLon' : minLon_p,
            'maxLon' : maxLon_p,   
        }
        # Bounding box for the estimation of the wqp maps
        self.bbox_trim = trimBbox(self.bbox,self.bbox_prod)
    
    def updateSNAPSubset(self, params_subset):
        bbox_trim = self.bbox_trim
        bbox_ex = f"POLYGON(({bbox_trim['minLon']} {bbox_trim['maxLat']},{bbox_trim['minLon']} {bbox_trim['minLat']},{bbox_trim['maxLon']} {bbox_trim['minLat']},{bbox_trim['minLon']} {bbox_trim['maxLat']}))"
        params_subset[1]['geoRegion'] = bbox_ex
        return params_subset

    def updateSNAPTemperature(self, df_temp, params_C2RCC):
        #TODO: update temperature parameters_C2RCC
        params_C2RCC[1]['temperature']= extractTemp(self.name, df_temp)
        return params_C2RCC
    
    def updateSNAPAtmCorr(self, df_atm, params_bandMaths):
        #TODO: update temperature parameters_C2RCC
        bExpresions = extractAtmCorr(self.name, df_atm)
        params_bandMaths[1]['targetBands'][0]['expression'] = bExpresions['lswt_mid_high']
        params_bandMaths[1]['targetBands'][1]['expression'] = bExpresions['lswt_high']
        params_bandMaths[1]['targetBands'][2]['expression'] = bExpresions['lswt']
        return params_bandMaths
    

"""
2. DEFINE THE INPUT PARAMETERS FOR THE PROCESSING
"""
def inputParameters(sensor_input, sensor_output):
    # Define the paths to the input and output directories. e.g. '.\in\data\S3A'; '.\out\data\S3A'
    #Define the working folders path
    cwd_path = {
        'in':sensor_input,
        'out':sensor_output,
        'out_masks':os.path.join(sensor_output,'masks'),
        'out_oa':os.path.join(sensor_output,'oa'),
        'out_rrs':os.path.join(sensor_output,'rrs'),
        'out_wqp':os.path.join(sensor_output,'wqp'),
        'out_wqp_no_clip':os.path.join(sensor_output,'wqp_no_clip'),
        'out_wqp_cloud':os.path.join(sensor_output,'wqp_cloud_mask'),
        'out_wqp_no_mask':os.path.join(sensor_output,'wqp_no_mask'),
        'in_parameters': '.\in\data\satellite_imagery\wqp_parameters',
        'vectorFile':'.\\vector\simile_laghi\simile_laghi.shp',
    }

    return cwd_path

"""
3. DEFINE FUNCTIONS TO EXECUTE SNAP OPERATORS
"""
#Define function to extract the atmosferic correction parameters
def extractTemp(name, df_temp):
    #TODO: review time rounding vs interpolation
    date = name.split('_')[7]
    round_min = str(math.floor(int(date[11:13])/10)*10)
    if round_min == '0':
        dateFormat = "%s/%s/%s %s:%s" % (date[0:4],date[4:6],date[6:8],date[9:11],'00')
    else:
        dateFormat = "%s/%s/%s %s:%s" % (date[0:4],date[4:6],date[6:8],date[9:11],round_min)
    values = df_temp.loc[df_temp['Data-Ora']==dateFormat]
    t = values.iloc[0][' Medio']
    if t < 0:
        #Error on the processing for negative
        t = 0.1
    print('Date: {} \nTemperature: {}°C'.format(dateFormat,t))
    return t

#Define function to extract the atmosferic correction parameters
def extractAtmCorr(name, df_atm):
    try:
        refDate = datetime.strptime(name.split('_')[3], '%Y%m%d') 
        df_check = df_atm.loc[df_atm['DateTime']==refDate.date()]
        Lu = df_check.iloc[0].Lu
        t = df_check.iloc[0].t
        Ld = df_check.iloc[0].Ld
        bExpression = dict()
        bExpression['lswt_mid_high'] = f"if simile_laghi and not (cloud or cloud_confidence_mid or cloud_shadow_confidence_mid or cloud_shadow_confidence_high or cirrus_confidence_mid or cirrus_confidence_high) then (1321.08 / log(774.89/ ((('thermal_infrared_(tirs)_1')-{Lu}-{t} *(1-0.98)*{Ld})/({t} *0.98))+1)-273) else NaN"
        bExpression['lswt_high'] = f"if simile_laghi and not (cloud or cloud_shadow_confidence_high or cirrus_confidence_high) then (1321.08 / log(774.89/ ((('thermal_infrared_(tirs)_1')-{Lu}-{t} *(1-0.98)*{Ld})/({t} *0.98))+1)-273) else NaN"
        bExpression['lswt'] = f"(1321.08 / log(774.89/ ((('thermal_infrared_(tirs)_1')-{Lu}-{t} *(1-0.98)*{Ld})/({t} *0.98))+1)-273)"
        print(f'Date: {refDate} \n Lu: {Lu}, t: {t}, Ld: {Ld}')
    except:
        print("There are no atmosferic correction parameters for the specified date")
    return bExpression


#Add processing parameters
def setProcessingParameters(params):
    hm = HashMap()
    for key in params:
        if key != 'targetBands':
            hm.put(key,params[key])
    return hm

# Build the target bands array for the BandMaths function input
def buildTargetBands(parameters):
    targetBands_arr = parameters['targetBands']
    BandDescriptor = jpy.get_type('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor')
    targetBands = jpy.array('org.esa.snap.core.gpf.common.BandMathsOp$BandDescriptor', len(targetBands_arr))
    
    for idx, targetBand_params in enumerate(targetBands_arr):
        tb = BandDescriptor()
        for key in targetBand_params:
            setattr(tb,key,targetBand_params[key])
        targetBands[idx] = tb
    parameters_bandmaths = setProcessingParameters(parameters)
    parameters_bandmaths.put('targetBands', targetBands)

    return parameters_bandmaths

#General function to execute SNAP functions
def executeSNAPFunction(product, parameters):
    operator = parameters[0]['operator']
    params = parameters[1]
    if operator == 'BandMaths':
        hm_params = buildTargetBands(params)
    else: 
        hm_params = setProcessingParameters(params)
    processed_product = snappy.GPF.createProduct(operator, hm_params, product)
    #Return processed product
    return processed_product

# Compare the coordinates to obtain the min/max values
def getMinMax(current,minV,maxV):
	if current < minV:
		minV = current
	if current > maxV:
		maxV = current
	return [minV, maxV]

def getExtent(myProd):
	########
	## Get corner coordinates of the ESA SNAP product (get extent)
	########
	# int step - the step given in pixels
	step = 1
	minLon = 999.99

	GeoPos = snappy.ProductUtils.createGeoBoundary(myProd, step)

	maxLon = -minLon
	minLat = minLon
	maxLat = maxLon
	for element in GeoPos:
		try:
			lon = element.getLon()
			[minLon, maxLon] = getMinMax(lon,minLon,maxLon)
		except (NameError):
			pass
		try:
			# TODO: separate method to get min and max
			lat = element.getLat()
			[minLat, maxLat] = getMinMax(lat,minLat,maxLat)
		except (NameError):
			pass

	return minLon, maxLon, minLat, maxLat

def trimBbox(bbox, bbox_prod):
    bbox_trim = dict()
    # Min latitude check
    if bbox['minLat']>bbox_prod['minLat']:
        bbox_trim['minLat'] = bbox['minLat']
    else:
        bbox_trim['minLat'] = bbox_prod['minLat']
    # Min longitude check
    if bbox['minLon']>bbox_prod['minLon']:
        bbox_trim['minLon'] = bbox['minLon']
    else:
        bbox_trim['minLon'] = bbox_prod['minLon']
    # Max latitude check
    if bbox['maxLat']<bbox_prod['maxLat']:
        bbox_trim['maxLat'] = bbox['maxLat']
    else:
        bbox_trim['maxLat'] = bbox_prod['maxLat']
    # Max latitude check
    if bbox['maxLon']<bbox_prod['maxLon']:
        bbox_trim['maxLon'] = bbox['maxLon']
    else:
        bbox_trim['maxLon'] = bbox_prod['maxLon']
    return bbox_trim

def exportProductBands(product, out_path, writeFormat):
    ProductIO.writeProduct(product, out_path, writeFormat)