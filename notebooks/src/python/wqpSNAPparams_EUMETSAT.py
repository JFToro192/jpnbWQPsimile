cwd_path = {
    'vectorFile':'./vector/simile_laghi/simile_laghi.shp',
}

"""
DEFINE PROCESSING PARAMETERS FOR EACH SNAP OPERATOR
"""
### Define the processing parameters for each SNAP operator ###

# 1. Subset Processing Parameters
params_subset = [
        {
            'operator':'Subset'
        },
        {
            "region":"0,0,0,0",
            'geoRegion' : 'POLYGON((8.1 46.34,8.1 45.59,9.8 45.59,9.8 46.34,8.1 46.34))',
            "subSamplingX":"1",
            "subSamplingY":"1",
            "fullSwath":"false",
            'copyMetadata' : 'true'
        }
    ]

# 2. Reproject Processing Parameters
params_reproject = [
        {
            'operator':'Reproject'
        },
        {
            # 'crs' :  """PROJCS["UTM Zone 32 / World Geodetic System 1984", 
            #                 GEOGCS["World Geodetic System 1984", 
            #                 DATUM["World Geodetic System 1984", 
            #                     SPHEROID["WGS 84", 6378137.0, 298.257223563, AUTHORITY["EPSG","7030"]], 
            #                     AUTHORITY["EPSG","6326"]], 
            #                 PRIMEM["Greenwich", 0.0, AUTHORITY["EPSG","8901"]], 
            #                 UNIT["degree", 0.017453292519943295], 
            #                 AXIS["Geodetic longitude", EAST], 
            #                 AXIS["Geodetic latitude", NORTH]], 
            #             PROJECTION["Transverse_Mercator"], 
            #             PARAMETER["central_meridian", 9.0], 
            #             PARAMETER["latitude_of_origin", 0.0], 
            #             PARAMETER["scale_factor", 0.9996], 
            #             PARAMETER["false_easting", 500000.0], 
            #             PARAMETER["false_northing", 0.0], 
            #             UNIT["m", 1.0], 
            #             AXIS["Easting", EAST], 
            #             AXIS["Northing", NORTH]]""",
            'crs' : "EPSG:32632",
            'resampling' : 'Nearest',
            'pixelSizeX' : '300',
            'pixelSizeY' : '300',
            'orthorectify' : 'false',
            'noDataValue' : 'NaN',
            'includeTiePointGrids' : 'true',
        }
    ]

# 3. C2RCC OLCI processing Parameters
params_C2RCC = [
        {
            'operator':'c2rcc.olci'
        },
        {
            'salinity' : '0.5', #PSU
            'temperature' : '15', #Degrees
            'ozone' : '330', #DU
            'press' : '1000', #hPa
            'TSMfac' : '1.06',
            'TSMexp': '0.942',
            'CHLexp': '0.65',
            'CHLfac': '19.8',
            'thresholdRtosaOOS': '0.01',
            'thresholdAcReflecOos': '0.15',
            'thresholdCloudTDown865': '0.955',
            'outputAsRrs': 'false',
            'deriveRwFromPathAndTransmittance': 'false',
            'useEcmwfAuxData': 'true',
            'outputRtoa': 'true',
            'outputRtosaGc': 'false',
            'outputRtosaGcAann': 'false',
            'outputRpath': 'false',
            'outputTdown': 'false',
            'outputTup': 'false',
            'outputAcReflectance': 'true',
            'outputRhown': 'true',
            'outputOos': 'true',
            'outputKd': 'true',
            'outputUncertainties': 'true',
        }
    ]

# 4. Import-Vector Processing Parameters
params_importVector = [
        {
            'operator':'Import-Vector'
        },
        {
            'vectorFile' : cwd_path['vectorFile'],
            'separateShapes' : 'false'
        }
    ]

# 5. BandMaths Processing Parameters
params_bandMaths = [
        {
            'operator':'BandMaths'
        },
        {
            'name' : 'wqp',
            'description' : 'S3 computations',
            'targetBands' : [
                {
                    'name' : 'chl_nn',
                    'type' : 'float32',
                    'expression' : "if simile_laghi then ('CHL_NN') else NaN",
                },
                {
                    'name' : 'chl_oc4me',
                    'type' : 'float32',
                    'expression' : "if simile_laghi then ('CHL_OC4ME') else NaN",
                },
                {
                    'name' : 'tsm_nn',
                    'type' : 'float32',
                    'expression' : "if simile_laghi then ('TSM_NN') else NaN",
                }
            ]
        }
    ]

# 6. 
params_bandExtractor_chl_nn = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"chl_nn",
    }
]
params_bandExtractor_chl_oc4me = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"chl_oc4me",
    }
]
params_bandExtractor_tsm_nn = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"tsm_nn",
    }
]