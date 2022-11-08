import os
import math
import csv
from datetime import datetime
import numpy as np
import pandas as pd
import fiona
import rasterio
from rasterio.merge import merge
import rasterio.mask
from rasterio.io import MemoryFile
from rasterstats import zonal_stats, point_query
import matplotlib.pyplot as plt

class wqp:

    # Extract the metadata of the datasets    
    def __init__(self, path):
        temp_path = path.split('/')
        temp_path = '/'.join(temp_path)
        temp_path = path.split('/')
        name = temp_path[-1].split('.')[0]
        self.path = path
        self.name = name        
        self.sensor = name.split('/')[-1].split('_')[0]
        # Sentinel-3 
        if (self.sensor in ['S3','S3A','S3B']):
            date_format = "%Y%m%dT%H%M%S"
            self.typology = name.split('_')[1]
            if name.split('_')[-2] != 'Oa':
                self.date = datetime.strptime(name.split('_')[-2], date_format)
                self.crs = name.split('_')[2]
            else:
                self.date = datetime.strptime(name.split('_')[2], date_format)
                self.crs = name.split('_')[1]
                
        # Landsat-8
        elif (self.sensor in ['L8']):
            date_format = "%Y%m%d"
            if name.split('_')[-2] != 'Oa':
                self.date = datetime.strptime(name.split('_')[-2], date_format)  
                self.typology = name.split('_')[1]
                self.crs = name.split('_')[2]
    
    # Read the datasets using rasterio
    def readWQP(self):
        self.image = rasterio.open(self.path)
        
    # Close the dataset using rasterio
    def closeWQP(self):
        self.image.close()
        
    def writeWQP(self, out_path, array):
        
        # Register GDAL format drivers and configuration options with a
        # context manager.
        with rasterio.Env():

            # Write an array as a raster band to a new 8-bit file. For
            # the new file's profile, we start with the profile of the source
            
            profile = self.image.profile

            # And then change the band count to 1, set the
            # dtype to uint8, and specify LZW compression.
            profile.update(
                dtype=rasterio.float32,
                count=1,
                # compress='lzw'
                )

            if self.typology == 'oa':
                f_name = os.path.join(out_path+'.tif')
            else:
                f_name = os.path.join(out_path)

            with rasterio.open(f_name, 'w', **profile) as dst:
                dst.write(array.astype(rasterio.float32), 1)
           
    
    # Compute the zonal statistics for a reference raster and polygon
    def computeStatistics(self, vectorData, nameField, stats, nodata):
        # Default stats returned by the method
        # Use the stats documentation provided for rasterstats
        zs_temp = zonal_stats(vectorData, self.path, stats=stats, nodata=nodata)
        
        # Organize the data according to the feature
        zs = dict()
        j = 0
        for d in zs_temp:
            zs[vectorData.loc[j][nameField]] = d
            j += 1
            
        self.stats = zs
        

    # Extract point data from the reference product for single band raster
    def extractSamplePoints(self, vectorData):
        obs = []
        for i, point in vectorData.iterrows():
            n = point[0] 
            x = point[2].xy[0][0]
            y = point[2].xy[1][0]
            row, col = self.image.index(x,y)
            try:
                value = self.image.read(1)[row,col]
                o = [n, x,y,row,col,value]
                obs.append(o)
            except:
                print(x,',',y,' coordinates are out of the image')
        
        df = pd.DataFrame(obs, columns = ['id','x','y','row','col',self.typology])
        
        self.samplePoint = df
        
    def organizeWQPEstimates(d_stats):
        # Organize the WQP descriptive statistics in an structure suitable to be exported as a dataframe
        d = dict()
        for key_feature in d_stats:
            for key_stat in d_stats[key_feature]:
                d['{}_{}'.format(key_stat,key_feature)] = d_stats[key_feature][key_stat]
        return d
    
    def exportWQPFormatStats(src):
        d = wqp.organizeWQPEstimates(src.stats)
        stats_keys = list(d.keys())
        
        #TODO: exception on null value for the samplePoints
        d['name'] = src.name
        d['path'] = src.path
        d['sensor'] = src.sensor
        d['typology'] = src.typology
        d['crs'] = src.crs
        d['date'] = src.date
        
        cols = ['name','path', 'sensor', 'typology', 'crs', 'date']
        con = np.concatenate((cols,stats_keys))

        df = pd.DataFrame([d])
        df = df.reindex(columns = con)
        
        return df
    
    def exportWQPFormatStatsOutliers(src):
        d = wqp.organizeWQPEstimates(src.outliers_stats)
        stats_keys = list(d.keys())
        
        #TODO: exception on null value for the samplePoints
        d['name'] = src.name
        d['path'] = src.path
        d['sensor'] = src.sensor
        d['typology'] = src.typology
        d['crs'] = src.crs
        d['date'] = src.date
        
        cols = ['name','path', 'sensor', 'typology', 'crs', 'date']
        con = np.concatenate((cols,stats_keys))

        df = pd.DataFrame([d])
        df = df.reindex(columns = con)
        
        return df
    
    #OUTLIER REJECTION FUNCTIONS
    """
    DEFINE THE PROCESSING AND STORING FUNCTIONS
    """
    # Single feature crop save. Default saved band: 0.
    def saveMaskedImage(self,out_path,NameFeature, band=0):
        profile = self.image.profile.copy()
        profile.update({
                'dtype': 'float32',
                'height': self.crops[NameFeature]['crop'][0].shape[0],
                'width': self.crops[NameFeature]['crop'][0].shape[1],
                'count': 1,
                'transform': self.crops[NameFeature]['transform']
            })  

        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write_band(1, self.crops[NameFeature]['crop'][band-1])
        
    """
    IMPORT THE INDEPENDENT LAYERS FOR THE LAKES
    """

    def importVector(path, nameField):
        shapes = dict()
        with fiona.open(path, "r") as shapefile:
            for feature in shapefile:
                shapes[feature['properties'][nameField]] = dict()
                shapes[feature['properties'][nameField]]["geometry"] = [feature["geometry"]]
        return shapes

#     """
#     CREATE DATASET
#     """
#     def create_dataset(data, crs, transform):
#         # Receives a 3D array, a transform and a crs to create a rasterio dataset

#         memfile = MemoryFile()
#         dataset = memfile.open(driver='GTiff', height=data.shape[0], width=data.shape[1], count=1, crs=crs, 
#                                transform=transform, dtype=data.dtype)
#         dataset.write(data)

#         return dataset
     
    """
    METHODS FOR DETECTING OUTLIERS THROUGH THRESHOLDS
    """
    def outlierDetectionMethods(stats, method):
        #TODO: compute the boundaries depending according to the selected method. Pass the limits to the outlier rejection method        
        #methods_list = ['IQR', '2Sigma', '3Sigma']
        bounds = dict()
        if method == 'IQR':
            IQR = stats['percentile_75'] - stats['percentile_25']
            lowerBound = stats['percentile_25'] - 1.5*IQR
            upperBound = stats['percentile_75'] + 1.5*IQR
        elif method == '2Sigma':
            lowerBound = stats['mean'] - 2*stats['std']
            upperBound = stats['mean'] + 2*stats['std']
        elif method == '3Sigma':
            lowerBound = stats['mean'] - 3*stats['std']
            upperBound = stats['mean'] + 3*stats['std']
        
        bounds['lowerBound'] = lowerBound
        bounds['upperBound'] = upperBound
        
        return bounds
    
    def outlierRejection(self, method=None, minLower=None, maxUpper=None):
        orDict = dict()  
        raster_collection = dict()
        outliers_collection = dict()
        for key in self.crops:
            orDict[key] = dict() 
            stats = self.stats[key]
            if (stats['min'] != None):
                
                if (method != None):
                    try:
                        bounds = wqp.outlierDetectionMethods(stats, method)
                    except:
                        print('Select one of the available methods')
                else:
                    bounds = {'lowerBound':minLower,'upperBound': maxUpper}
                    
                # Verify that the computed thresholds are smaller/greater than the min/max arguments (if input)
                if ( minLower != None and bounds['lowerBound']<minLower ):
                    bounds['lowerBound'] = minLower
                if ( maxUpper != None and bounds['upperBound']>maxUpper ):
                    bounds['upperBound'] = maxUpper
                
                lowerBound = bounds['lowerBound']
                upperBound = bounds['upperBound']
                
                # Identify the number of outliers for each threshold
                raster = self.crops[key]['crop'].copy()
                countTotal = np.count_nonzero(~np.isnan(raster))
                # Extract the outliers values to the corresponding thresholds
                raster[(raster<=lowerBound) | (raster>=upperBound)] = np.nan 
                countValid = np.count_nonzero(~np.isnan(raster))
                if (countValid>0):
                    percValid = countValid / countTotal
                else:
                    percValid = 0
                
                # Extract outliers from the crop raster
                outliers = self.crops[key]['crop'].copy()
                outliers[outliers==0] = np.nan
    #             outliers[(outliers>=lowerBound) | (outliers<=upperBound)] = np.nan  
                outliers[(outliers>lowerBound) & (outliers<upperBound)] = np.nan  
                countLower = np.count_nonzero(outliers<lowerBound)
                countUpper = np.count_nonzero(outliers>upperBound)

                # Organize results in dictionary
                orDict[key]['Method'] = method
                orDict[key]['lowerBound'] = lowerBound
                orDict[key]['upperBound'] = upperBound
                orDict[key]['countLower'] = countLower
                orDict[key]['countUpper'] = countUpper
                orDict[key]['countValid'] = countValid
                orDict[key]['countTotal'] = countTotal
                orDict[key]['percValid'] = percValid
                if (countValid>0):
                    orDict[key]['percOutliers'] = 1 - percValid
                else:
                    orDict[key]['percOutliers'] = 0

                # Save raster with no outliers
                raster_collection[key] = self.create_dataset(raster[0],self.crops[key]['transform'])
                outliers_collection[key] = self.create_dataset(outliers[0],self.crops[key]['transform'])
                del raster, outliers
            else:
                print(f'Missing Stats for Lake {key}')
        self.raster_collection = raster_collection
        self.outliers_collection = outliers_collection
        self.outliers_stats = orDict
            
            
    """
    MERGE RASTER COLLECTIONS
    """
    def mergeRasterCollectionsExport(self, raster_collection, out_path):
        if (len(raster_collection)>0):
            raster_col_lst = []
            for x in ['Lugano','Como','Maggiore']:
                if x in list(raster_collection.keys()):
                    raster_col_lst.append(raster_collection[x])
            merged, transf = merge(raster_col_lst)
            merged[0][merged[0]==0]=np.nan
            self.saveMergedImage(out_path,merged[0],transf)

    """
    SAVED MERGED COLLECTION
    """
    def saveMergedImage(self, out_path, data, transf):
        profile = self.image.profile.copy()
        profile.update({
                'dtype': 'float32',
                'height': data.shape[0],
                'width': data.shape[1],
                'transform': transf
         })  

        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write_band(1, data)
    
    
    """
    CROP RASTER LAYER BY FEATURES
    """
    def cropRasterByFeatures(self, vectorData_path, nameField, band=None):
        
        crops = dict()
        shapes = wqp.importVector(vectorData_path, nameField)
        for key in shapes:
            crop_shape = dict()
            featureName = key
            featureGeometry = shapes[key]['geometry']
            try: 
                cropped_image, cropped_transform = rasterio.mask.mask(self.image, featureGeometry, crop=True, filled=True, all_touched=False, nodata=np.nan)
                crop_shape['crop'] = cropped_image
                crop_shape['transform'] = cropped_transform
                crops[key] = crop_shape
            except:
                print(f"Lake {key} does not overlay the raster layer")
        self.crops = crops

    """
    CREATE DATASET
    """
    def create_dataset(self, data, transform):
        # Receives a 2D array, a transform and a crs to create a rasterio dataset

        memfile = MemoryFile()
        dataset = memfile.open(driver='GTiff', height=data.shape[0], width=data.shape[1], count=1, crs=self.image.crs, 
                               transform=transform, dtype=data.dtype)
        dataset.write(data,1)

        return dataset
    
# Function to normalize the grid values
def normalize(array):
    """Normalizes numpy arrays into scale 0.0 - 1.0"""
    array_min, array_max = np.nanmin(array), np.nanmax(array)
    return ((array - array_min)/(array_max - array_min))

def plotBandsMosaic(src):
    num_bands = src.count
    n_cols = 3
    n_rows = math.ceil(num_bands/n_cols)
    fig, axs = plt.subplots(n_rows, 3, figsize=(12,n_rows*3), sharey = True)
    n = 1
    for r in range(1,n_rows+1):
        for c in range(1,n_cols+1):
            band = axs[r-1,c-1].imshow(src.read(n), cmap='viridis')
            axs[r-1,c-1].set_title(f'Band - {n}')
            fig.colorbar(band, ax=axs[r-1,c-1])
            fig.tight_layout(pad=1.0)
            n = n + 1
