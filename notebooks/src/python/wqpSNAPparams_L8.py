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
            "referenceBand":"green",
            'geoRegion' : 'POLYGON((7.9 46.65,7.9 45.3,9.95 45.3,9.95 46.65,7.9 46.65))',
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
            'crs' : 'UTM Zone 32 / World Geodetic System 1984',
        }
    ]

# 3. Resample Processing Parameters
params_resample = [
        {
            'operator':'Resample'
        },
        {
            'referenceBand' : 'green',
            'upsampling' : 'Nearest',
            'downsampling' : 'First',
            'flagDownsampling' : 'First',
            'resampleOnPyramidLevels' : 'true' 
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

# 5.1. BandMaths Processing Parameters
params_bandMaths = [
        {
            'operator':'BandMaths'
        },
        {
            'name' : 'wqp',
            'description' : 'L8 computations',
            'targetBands' : [
                {
                    'name' : 'lswt_mid_high',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and not (cloud or cloud_confidence_mid or cloud_shadow_confidence_mid or cloud_shadow_confidence_high or cirrus_confidence_mid or cirrus_confidence_high) then (1321.08 / log(774.89/ ((('thermal_infrared_(tirs)_1')-0.46-0.93 *(1-0.98)*0.79)/(0.93 *0.98))+1)-273) else NaN"
                },
                {
                    'name' : 'lswt_high',
                    'type' : 'float32',
                    'expression' : "if simile_laghi and not (cloud or cloud_shadow_confidence_high or cirrus_confidence_high) then (1321.08 / log(774.89/ ((('thermal_infrared_(tirs)_1')-0.46-0.93 *(1-0.98)*0.79)/(0.93 *0.98))+1)-273) else NaN",
                },
                {
                    'name' : 'lswt',
                    'type' : 'float32',
                    'expression' : "(1321.08 / log(774.89/ ((('thermal_infrared_(tirs)_1')-0.46-0.93*(1-0.98)*0.79)/(0.93 *0.98))+1)-273)",
                }
            ]
        }
    ]

params_bandMaths_masks = [
        {
            'operator':'BandMaths'
        },
        {
            'name' : 'masks',
            'description' : 'L8 masks',
            'targetBands' : [
                {
                    'name' : 'cloud_confidence_mid',
                    'type' : 'float32',
                    'expression' : "cloud_confidence_mid",
                },
                {
                    'name' : 'cloud_confidence_high',
                    'type' : 'float32',
                    'expression' : "cloud_confidence_high",
                },
                {
                    'name' : 'cloud_shadow_confidence_mid',
                    'type' : 'float32',
                    'expression' : "cloud_shadow_confidence_mid",
                },
                {
                    'name' : 'cloud_shadow_confidence_high',
                    'type' : 'float32',
                    'expression' : "cloud_shadow_confidence_high",
                },
                {
                    'name' : 'cirrus_confidence_mid',
                    'type' : 'float32',
                    'expression' : "cirrus_confidence_mid",
                },
                {
                    'name' : 'cirrus_confidence_high',
                    'type' : 'float32',
                    'expression' : "cirrus_confidence_high",
                }
            ]
        }
]

# 6. BandExtract Processing Parameters
params_bandExtractor_lswt = [
        {
            'operator':'BandsExtractorOp'
        },
        {
            'sourceBandNames' : 'lswt',
        }
    ]

params_bandExtractor_lswt_mid_high = [
        {
            'operator':'BandsExtractorOp'
        },
        {
            'sourceBandNames' : 'lswt_mid_high',
        }
    ]

params_bandExtractor_lswt_high = [
        {
            'operator':'BandsExtractorOp'
        },
        {
            'sourceBandNames' : 'lswt_high',
        }
    ]

params_bandExtractor_masks = [
    {
        'operator':'bandsExtractorOp'
    },
    { "sourceBandNames":"cloud_confidence_mid,cloud_confidence_high,cloud_shadow_confidence_mid,cloud_shadow_confidence_high,cirrus_confidence_mid,cirrus_confidence_high"
    }
]