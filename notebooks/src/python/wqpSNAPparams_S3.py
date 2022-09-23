cwd_path = {
    'vectorFile':'.\\vector\simile_laghi\simile_laghi.shp',
}

"""
DEFINE PROCESSING PARAMETERS FOR EACH SNAP OPERATOR
"""

# 1. Subset Processing Parameters
params_subset = [
        {
            'operator':'Subset'
        },
        {
            "region":"0,0,0,0",
            'geoRegion' : 'POLYGON((8.1 46.4,8.1 45.5,9.8 45.5,9.8 46.4,8.1 46.4))',
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
            'outputAsRrs': 'true',
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
                    'name' : 'chl',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_chl') else NaN",
                },
                {
                    'name' : 'tsm',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_tsm') else NaN",
                },
                {
                    'name' : 'chl_no_clip',
                    'type' : 'float32',
                    'expression' : "if not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_chl') else NaN",
                },
                {
                    'name' : 'tsm_no_clip',
                    'type' : 'float32',
                    'expression' : "if not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_tsm') else NaN",
                },
                {
                    'name' : 'chl_no_mask',
                    'type' : 'float32',
                    'expression' : 'conc_chl',
                },
                {
                    'name' : 'tsm_no_mask',
                    'type' : 'float32',
                    'expression' : 'conc_tsm',
                },
                {
                    'name' : 'chl_cloud_mask',
                    'type' : 'float32',
                    'expression' : "if not (Cloud_risk) then ('conc_chl') else NaN",
                },
                {
                    'name' : 'tsm_cloud_mask',
                    'type' : 'float32',
                    'expression' : "if not (Cloud_risk) then ('conc_tsm') else NaN",
                },
                {
                    'name' : 'chl_b15ok',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and ('rtoa_15'<0.04) and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_chl') else NaN",
                },
                {
                    'name' : 'tsm_b15ok',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and ('rtoa_15'<0.04) and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_tsm') else NaN",
                },
                {
                    'name' : 'rtoa_15',
                    'type' : 'float32',
                    'expression' : "rtoa_15",
                },
                {
                    'name' : 'chl_threshold_lower',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and ('conc_chl'>0) and ('conc_chl'<=15) and ('rtoa_15'<0.04) and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_chl') else NaN",
                },
                {
                    'name' : 'tsm_threshold_lower',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and ('conc_chl'>0) and ('rtoa_15'<0.04) and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_tsm') else NaN",
                },
                {
                    'name' : 'chl_threshold',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and ('conc_chl'>0) and ('rtoa_15'<0.04) and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_chl') else NaN",
                },
                {
                    'name' : 'tsm_threshold',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and ('conc_chl'>0) and ('rtoa_15'<0.04) and not (Cloud_risk or Rtosa_OOS or Rtosa_OOR or Rhow_OOR) then ('conc_tsm') else NaN",
                },
            ]
        }
    ]

params_bandMaths_rrs = [
        {
            'operator':'BandMaths'
        },
        {
            'name' : 'rrs',
            'description' : 'rrs',
            'targetBands' : [
                {
                    'name' : 'rrs_1',
                    'type' : 'float32',
                    'expression' : "rrs_1",
                },
                {
                    'name' : 'rrs_2',
                    'type' : 'float32',
                    'expression' : "rrs_2",
                },    
                {
                    'name' : 'rrs_3',
                    'type' : 'float32',
                    'expression' : "rrs_3",
                },    
                {
                    'name' : 'rrs_4',
                    'type' : 'float32',
                    'expression' : "rrs_4",
                },    
                {
                    'name' : 'rrs_5',
                    'type' : 'float32',
                    'expression' : "rrs_5",
                },    
                {
                    'name' : 'rrs_6',
                    'type' : 'float32',
                    'expression' : "rrs_6",
                },    
                {
                    'name' : 'rrs_7',
                    'type' : 'float32',
                    'expression' : "rrs_7",
                },    
                {
                    'name' : 'rrs_8',
                    'type' : 'float32',
                    'expression' : "rrs_8",
                },    
                {
                    'name' : 'rrs_9',
                    'type' : 'float32',
                    'expression' : "rrs_9",
                },    
                {
                    'name' : 'rrs_10',
                    'type' : 'float32',
                    'expression' : "rrs_10",
                },    
                {
                    'name' : 'rrs_11',
                    'type' : 'float32',
                    'expression' : "rrs_11",
                },         
                {
                    'name' : 'rrs_12',
                    'type' : 'float32',
                    'expression' : "rrs_12",
                },     
                {
                    'name' : 'rrs_16',
                    'type' : 'float32',
                    'expression' : "rrs_16",
                },    
                {
                    'name' : 'rrs_17',
                    'type' : 'float32',
                    'expression' : "rrs_17",
                },    
                {
                    'name' : 'rrs_18',
                    'type' : 'float32',
                    'expression' : "rrs_18",
                },      
                {
                    'name' : 'rrs_21',
                    'type' : 'float32',
                    'expression' : "rrs_21",
                }, 
            ]
        }
    ]

params_bandMaths_oa = [
        {
            'operator':'BandMaths'
        },
        {
            'name' : 'Oa_bands',
            'description' : 'Oa_bands',
            'targetBands' : [
                {
                    'name' : 'Oa01_radiance',
                    'type' : 'float32',
                    'expression' : "Oa01_radiance",
                },
                {
                    'name' : 'Oa02_radiance',
                    'type' : 'float32',
                    'expression' : "Oa02_radiance",
                },
                {
                    'name' : 'Oa03_radiance',
                    'type' : 'float32',
                    'expression' : "Oa03_radiance",
                },
                {
                    'name' : 'Oa04_radiance',
                    'type' : 'float32',
                    'expression' : "Oa04_radiance",
                },
                {
                    'name' : 'Oa05_radiance',
                    'type' : 'float32',
                    'expression' : "Oa05_radiance",
                },
                {
                    'name' : 'Oa06_radiance',
                    'type' : 'float32',
                    'expression' : "Oa06_radiance",
                },
                {
                    'name' : 'Oa07_radiance',
                    'type' : 'float32',
                    'expression' : "Oa07_radiance",
                },
                {
                    'name' : 'Oa08_radiance',
                    'type' : 'float32',
                    'expression' : "Oa08_radiance",
                },
                {
                    'name' : 'Oa09_radiance',
                    'type' : 'float32',
                    'expression' : "Oa09_radiance",
                },
                {
                    'name' : 'Oa10_radiance',
                    'type' : 'float32',
                    'expression' : "Oa10_radiance",
                },
                {
                    'name' : 'Oa11_radiance',
                    'type' : 'float32',
                    'expression' : "Oa11_radiance",
                },
                {
                    'name' : 'Oa12_radiance',
                    'type' : 'float32',
                    'expression' : "Oa12_radiance",
                },
                {
                    'name' : 'Oa13_radiance',
                    'type' : 'float32',
                    'expression' : "Oa13_radiance",
                },
                {
                    'name' : 'Oa14_radiance',
                    'type' : 'float32',
                    'expression' : "Oa14_radiance",
                },
                {
                    'name' : 'Oa15_radiance',
                    'type' : 'float32',
                    'expression' : "Oa15_radiance",
                },
                {
                    'name' : 'Oa16_radiance',
                    'type' : 'float32',
                    'expression' : "Oa16_radiance",
                },
                {
                    'name' : 'Oa17_radiance',
                    'type' : 'float32',
                    'expression' : "Oa17_radiance",
                },
                {
                    'name' : 'Oa18_radiance',
                    'type' : 'float32',
                    'expression' : "Oa18_radiance",
                },
                {
                    'name' : 'Oa19_radiance',
                    'type' : 'float32',
                    'expression' : "Oa19_radiance",
                },
                {
                    'name' : 'Oa20_radiance',
                    'type' : 'float32',
                    'expression' : "Oa20_radiance",
                },
                {
                    'name' : 'Oa21_radiance',
                    'type' : 'float32',
                    'expression' : "Oa21_radiance",
                },
            ]
        }
    ]

params_bandMaths_masks = [
        {
            'operator':'BandMaths'
        },
        {
            'name' : 'masks',
            'description' : 'masks',
            'targetBands' : [
                {
                    'name' : 'Cloud_risk',
                    'type' : 'float32',
                    'expression' : "Cloud_risk",
                }, 
                {
                    'name' : 'Rtosa_OOS',
                    'type' : 'float32',
                    'expression' : "Rtosa_OOS",
                }, 
                {
                    'name' : 'Rtosa_OOR',
                    'type' : 'float32',
                    'expression' : "Rtosa_OOR",
                }, 
                {
                    'name' : 'Rhow_OOR',
                    'type' : 'float32',
                    'expression' : "Rhow_OOR",
                }, 
            ]
        }
    ]

# 6. Extract bands from products

# Extract water surface reflectance bands
params_bandExtractor_rrs = [
    {
        'operator':'bandsExtractorOp'
    },
    { "sourceBandNames":"rrs_1,rrs_2,rrs_3,rrs_4,rrs_5,rrs_6,rrs_7,rrs_8,rrs_9,rrs_10,rrs_11,rrs_12,rrs_16,rrs_17,rrs_18,rrs_21",
    }
]

# Extract radiance bands
params_bandExtractor_oa = [
    {
        'operator':'bandsExtractorOp'
    },
    { "sourceBandNames":"Oa01_radiance,Oa02_radiance,Oa03_radiance,Oa04_radiance,Oa05_radiance,Oa06_radiance,Oa07_radiance,Oa08_radiance,Oa09_radiance,Oa10_radiance,Oa11_radiance,Oa12_radiance,Oa13_radiance,Oa14_radiance,Oa15_radiance,Oa16_radiance,Oa17_radiance,Oa18_radiance,Oa19_radiance,Oa20_radiance,Oa21_radiance",
    }
]

# Extract mask layers
params_bandExtractor_masks = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"Cloud_risk,Rtosa_OOS,Rtosa_OOR,Rhow_OOR",
    }
]

# Extract CHL C2RCC estimates
params_bandExtractor_chl = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"chl",
    }
]

# Extract TSM C2RCC estimates
params_bandExtractor_tsm = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"tsm",
    }
]

# Extract CHL C2RCC estimates
params_bandExtractor_chl_no_clip = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"chl_no_clip",
    }
]

# Extract TSM C2RCC estimates
params_bandExtractor_tsm_no_clip = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"tsm_no_clip",
    }
]

# Extract CHL C2RCC estimates
params_bandExtractor_chl_no_masks = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"chl_no_mask",
    }
]

# Extract TSM C2RCC estimates
params_bandExtractor_tsm_no_masks = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"tsm_no_mask",
    }
]

# Extract CHL C2RCC estimates (cloud mask only)
params_bandExtractor_chl_cloud_mask = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"chl_cloud_mask",
    }
]

# Extract TSM C2RCC estimates (cloud mask only)
params_bandExtractor_tsm_cloud_mask = [
    {
        'operator':'bandsExtractorOp'
    },
    {
        "sourceBandNames":"tsm_cloud_mask",
    }
]