# -*- coding: utf-8 -*-
'''
Authors: Bert Coerver, Gert Mulder, Tim Hessels
         UNESCO-IHE 2016
Contact: b.coerver@unesco-ihe.org
         t.hessels@unesco-ihe.org
Repository: https://github.com/wateraccounting/wa
Module: Products/ETref
'''
# import general python modules
import numpy as np

def SlopeInfluence(DEMmap,latitude,longitude,day):
	
    '''
    This function corrects the solar radiation for the sloping terrain.
    All the formulas are based on Allen (2006)
	
    DEMmap -- path to the DEM map
    latitude -- numpy array with the latitude
    longitude -- numpy array with the longitude
    day -- Day of the year
    '''
	
    # This model calculates the amount of sunlight on a particular day for a sloping
    # terrain. The needed inputs are:
    # DEM > a DEM map
    # lat/lon > either as 2 vectors or 2 matrices
    # day > the day of the year
    # Because we do not know the height of neigbouring cells at the border of the
    # grid, these values can deviate from real values.
    # Be carefull with high latitudes (>66, polar circle)! Calculations for regions without sunset
    # (all day sun) are not calculated correctly.
    
    # Solar constant
    G = 1367.0
    
    # If lat/lon are not a matrix but a vector create matrixes
    if not latitude.shape == longitude.shape:
        latitude = np.tile(latitude.reshape(len(latitude),1),[1,len(longitude)])
        longitude = np.tile(longitude.reshape(1,len(longitude)),[len(latitude),1])
    elif len(latitude.shape) == 1 and len(longitude.shape) == 1:
        latitude = np.tile(latitude.reshape(len(latitude),1),[1,len(longitude)])
        longitude = np.tile(longitude.reshape(1,len(longitude)),[len(longitude),1])
    
    # Convert lat/lon to radians
    lat = np.radians(latitude)
    lon = np.radians(longitude)
           
    # Calculate dlat/dlon assuming a regular grid
    latdiff = np.diff(lat,axis=0) 
    dlat = np.vstack((latdiff[0,:][None,:],(latdiff[1:,:] + latdiff[0:-1,:])/2,latdiff[-1,:][None,:]))
    londiff = np.diff(lon,axis=1) 
    dlon = np.hstack((londiff[:,0][:,None],(londiff[:,1:] + londiff[:,0:-1])/2,londiff[:,-1][:,None]))
    
    # And convert to meters
    lons = np.cos(lat) * np.cos(lat) * np.sin(dlon/2) ** 2
    lats = np.sin(dlat / 2) ** 2
    dlon = 2 * np.arcsin(np.sqrt(lons)) * 6371000
    dlat = 2 * np.arcsin(np.sqrt(lats)) * 6371000
    del lats, lons
    
    # Calculate dy_lat and dy_lon, height differences in latitude and longitude directions.
    latdiff = np.diff(DEMmap,axis=0) 
    dy_lat = np.vstack((latdiff[0,:][None,:],(latdiff[1:,:] + latdiff[0:-1,:])/2,latdiff[-1,:][None,:]))
    londiff = -np.diff(DEMmap,axis=1) 
    dy_lon = np.hstack((londiff[:,0][:,None],(londiff[:,1:] + londiff[:,0:-1])/2,londiff[:,-1][:,None]))    
    
    # Calculate slope
    slope = np.arctan((np.abs(dy_lat) + np.abs(dy_lon)) / np.sqrt(dlon**2+dlat**2))
    
    # declination of earth
    delta = np.arcsin(np.sin(23.45/360*2*np.pi)*np.sin((360.0/365.0)*(day-81)/360*2*np.pi))
    # EQ 2
    D2 = 1 / (1 + 0.033* np.cos(day/365*2*np.pi))
    
    constant =  G / D2 / (2*np.pi) 
    
    # Slope direction
    with np.errstate(divide='ignore'):
        slopedir = np.arctan(dy_lon/dy_lat) 
        
        # Exception if divided by zero    
        slopedir[np.logical_and(dy_lat == 0 , dy_lon <= 0)] = np.pi / 2
        slopedir[np.logical_and(dy_lat == 0, dy_lon > 0)] = -np.pi / 2
        
        # Correction ip dy_lat > 0
        slopedir[np.logical_and(dy_lat > 0, dy_lon < 0)] = np.pi + slopedir[np.logical_and(dy_lat > 0, dy_lon < 0)]
        slopedir[np.logical_and(dy_lat > 0, dy_lon >= 0)] = -np.pi + slopedir[np.logical_and(dy_lat > 0, dy_lon >= 0)]
    
    # Now calculate the expected clear sky radiance day by day for:
    # - A horizontal surface
    # - A mountaneous surface (slopes)
    
    # Define grids
    Horizontal = np.zeros(slope.shape) * np.nan
    Sloping = np.zeros(slope.shape) * np.nan
    
    sinb = np.zeros(slope.shape) *np.nan
    sinb_hor = np.zeros(slope.shape) *np.nan
    
    f1 = np.zeros(slope.shape) *np.nan
    f2 = np.zeros(slope.shape) *np.nan
    f3 = np.zeros(slope.shape) *np.nan
    f4 = np.zeros(slope.shape) *np.nan
    f5 = np.zeros(slope.shape) *np.nan
    
    #######
    ## Horizontal (EQ 35)
    #######
    
    # Check where there is no sunrise and assign values
    Horizontal[np.abs(delta-lat) > np.pi/2] = 0 
    
    # Check whether there are areas without sunset
    ID = np.where(np.ravel(np.abs(delta+lat)) > np.pi/2)    
    sunrise = -np.pi
    sunset = np.pi
    Horizontal.flat[ID] = IntegrateHorizontal((G/(np.pi*D2)),sunrise,sunset,delta,lat.flat[ID])    

    # Calculate sunset and sunrise for all other cells    
    ID = np.where(np.isnan(np.ravel(Horizontal)))    
    bound = BoundsHorizontal(delta,lat.flat[ID])     
    Horizontal.flat[ID] = IntegrateHorizontal((G/(np.pi*D2)),-bound,bound,delta,lat.flat[ID])
    
    ws = np.arccos(-np.tan(delta)*np.tan(lat))
    a,b,c,g,h = Table2(delta,lat,slope,slopedir) 
    sinb_hor = (2*g**2*ws + 4*g*h*np.sin(ws) + h**2*(ws+0.5*np.sin(2*ws))) / (2*(g*ws+h*np.sin(ws)))    
    
    #######
    ## Sloping (EQ )
    #######
    A1,A2,B1,B2 = TwoPeriodSunnyTimes(constant,delta,slope,slopedir,lat)    

    # Check whether we have one or two periods of sunlight.
    TwoPeriod = TwoPeriods(delta,slope,lat) 
    
    ID = np.where(np.ravel(TwoPeriod == True))
    Sloping.flat[ID] = TwoPeriodSun(constant,delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    f1.flat[ID],f2.flat[ID],f3.flat[ID],f4.flat[ID],f5.flat[ID] = Table1b(A1.flat[ID],A2.flat[ID],B1.flat[ID],B2.flat[ID]) 
    
    ID = np.where(np.ravel(TwoPeriod == False))
    Sloping.flat[ID] = OnePeriodSun(constant,delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    f1.flat[ID],f2.flat[ID],f3.flat[ID],f4.flat[ID],f5.flat[ID] = Table1a(A1.flat[ID],A2.flat[ID])  

    sinb = (b*g-a*h*f1 - c*g*f2 + (0.5*b*h - a*g)*f3 + 0.25*b*h*f4 + 0.5*c*h*f5) / b*f1 - c*f2 - a*f3
    #sinb[sinb[~np.isnan(sinb)] < 0.0] = 0.0
    
    fi = 0.75 + 0.25*np.cos(slope) - (0.5*slope/np.pi)

    return(Horizontal,Sloping, sinb, sinb_hor, fi, slope, np.where(np.ravel(TwoPeriod == True)))

def Table1a(sunrise,sunset):
    f1 = np.sin(sunset) - np.sin(sunrise)
    f2 = np.cos(sunset) - np.cos(sunrise)
    f3 = sunset - sunrise
    f4 = np.sin(2*sunset) - np.sin(2*sunrise)
    f5 = np.sin(sunset)**2 - np.sin(sunrise)**2
    return f1, f2, f3, f4, f5
    
def Table1b(w1,w2,w1b,w2b):
    f1 = np.sin(w2b) - np.sin(w1) + np.sin(w2) - np.sin(w1b)
    f2 = np.cos(w2b) - np.cos(w1) + np.cos(w2) - np.cos(w1b)
    f3 = w2b - w1 + w2 - w1b
    f4 = np.sin(2*w2b) - np.sin(2*w1) + np.sin(2*w2) - np.sin(2*w1b)
    f5 = np.sin(w2b)**2 - np.sin(w1)**2 + np.sin(w2)**2 - np.sin(w1b)**2
    return f1, f2, f3, f4, f5

def Table2(delta,lat,slope,slopedir):
    a = np.sin(delta)*np.cos(lat)*np.sin(slope)*np.cos(slopedir) - np.sin(delta)*np.sin(lat)*np.cos(slope)
    b = np.cos(delta)*np.cos(lat)*np.cos(slope) + np.cos(delta)*np.sin(lat)*np.sin(slope)*np.cos(slopedir)
    c = np.cos(delta)*np.sin(slopedir)*np.sin(slope)
    g = np.sin(delta)*np.sin(lat)
    h = np.cos(delta)*np.cos(lat)
    
    return a,b,c,g,h

def SunHours(delta,slope,slopedir,lat):
    # Define sun hours in case of one sunlight period
    
    a,b,c = Constants(delta,slope,slopedir,lat)
    riseSlope, setSlope = BoundsSlope(a,b,c)  
    bound = BoundsHorizontal(delta,lat)  

    Calculated = np.zeros(slope.shape, dtype = bool)    
    RiseFinal = np.zeros(slope.shape)    
    SetFinal = np.zeros(slope.shape)
    
    # First check sunrise is not nan
    # This means that their is either no sunrise (whole day night) or no sunset (whole day light)
    # For whole day light, use the horizontal sunrise and whole day night a zero..
    Angle4 = AngleSlope(a,b,c,-bound)    
    RiseFinal[np.logical_and(np.isnan(riseSlope),Angle4 >= 0)] = -bound[np.logical_and(np.isnan(riseSlope),Angle4 >= 0)]
    Calculated[np.isnan(riseSlope)] = True 
    
    # Step 1 > 4    
    Angle1 = AngleSlope(a,b,c,riseSlope)
    Angle2 = AngleSlope(a,b,c,-bound)    
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(Angle2 < Angle1+0.001 ,Angle1 < 0.001),Calculated == False) == True),a.shape)
    RiseFinal.flat[ID] = riseSlope.flat[ID]
    Calculated.flat[ID] = True
    # step 5 > 7
    Angle3 = AngleSlope(a,b,c,-np.pi - riseSlope)
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(-bound<(-np.pi-riseSlope),Angle3 <= 0.001),Calculated == False) == True),a.shape) 
    RiseFinal.flat[ID] = -np.pi -riseSlope.flat[ID]
    Calculated.flat[ID] = True
    
    # For all other values we use the horizontal sunset if it is positive, otherwise keep a zero   
    RiseFinal[Calculated == False] = -bound[Calculated == False] 
    
    # Then check sunset is not nan or < 0 
    Calculated = np.zeros(slope.shape, dtype = bool)     
    
    Angle4 = AngleSlope(a,b,c,bound)    
    SetFinal[np.logical_and(np.isnan(setSlope),Angle4 >= 0)] = bound[np.logical_and(np.isnan(setSlope),Angle4 >= 0)]
    Calculated[np.isnan(setSlope)] = True     
    
    # Step 1 > 4    
    Angle1 = AngleSlope(a,b,c,setSlope)
    Angle2 = AngleSlope(a,b,c,bound)    
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(Angle2 < Angle1+0.001,Angle1 < 0.001),Calculated == False) == True),a.shape)
    SetFinal.flat[ID] = setSlope.flat[ID]
    Calculated.flat[ID] = True
    # step 5 > 7
    Angle3 = AngleSlope(a,b,c,np.pi - setSlope)
    
    ID = np.ravel_multi_index(np.where(np.logical_and(np.logical_and(bound>(np.pi-setSlope),Angle3 <= 0.001),Calculated == False) == True),a.shape) 
    SetFinal.flat[ID] = np.pi - setSlope.flat[ID]
    Calculated.flat[ID] = True
    
    # For all other values we use the horizontal sunset if it is positive, otherwise keep a zero   
    SetFinal[Calculated == False] = bound[Calculated == False]   
    
    #    Angle4 = AngleSlope(a,b,c,bound)    
    #    SetFinal[np.logical_and(Calculated == False,Angle4 >= 0)] = bound[np.logical_and(Calculated == False,Angle4 >= 0)]

    # If Sunrise is after Sunset there is no sunlight during the day
    SetFinal[SetFinal <= RiseFinal] = 0
    RiseFinal[SetFinal <= RiseFinal] = 0
    
    return(RiseFinal,SetFinal)

def OnePeriodSun(constant,delta,slope,slopedir,lat):
    # Initialize function 
    sunrise,sunset = SunHours(delta,slope,slopedir,lat) 
    
    # Finally calculate resulting values
    Vals = IntegrateSlope(constant,sunrise,sunset,delta,slope,slopedir,lat)    
    
    return(Vals)

def TwoPeriodSunnyTimes(constant,delta,slope,slopedir,lat):
    # First derive A1 and A2 from the normal procedure    
    A1,A2 = SunHours(delta,slope,slopedir,lat)
    
    # Then calculate the other two functions.
    # Initialize function    
    
    a,b,c = Constants(delta,slope,slopedir,lat)
    riseSlope, setSlope = BoundsSlope(a,b,c)  
    
    B1 = np.maximum(riseSlope,setSlope)
    B2 = np.minimum(riseSlope,setSlope)
    
    Angle_B1 = AngleSlope(a,b,c,B1)
    Angle_B2 = AngleSlope(a,b,c,B2) 
    
    B1[abs(Angle_B1) > 0.001] = np.pi - B1[abs(Angle_B1) > 0.001]
    B2[abs(Angle_B2) > 0.001] = -np.pi - B2[abs(Angle_B2) > 0.001]    
    
    # Check if two periods really exist
    ID = np.ravel_multi_index(np.where(np.logical_and(B2 >= A1, B1 <= A2) == True),a.shape)
    Val = IntegrateSlope(constant,B2.flat[ID],B1.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    ID = ID[Val < 0]
    
    return A1,A2,B1,B2

def TwoPeriodSun(constant,delta,slope,slopedir,lat):
    # First derive A1 and A2 from the normal procedure    
    A1,A2 = SunHours(delta,slope,slopedir,lat)
    
    # Then calculate the other two functions.
    # Initialize function    
    
    a,b,c = Constants(delta,slope,slopedir,lat)
    riseSlope, setSlope = BoundsSlope(a,b,c)  
    
    B1 = np.maximum(riseSlope,setSlope)
    B2 = np.minimum(riseSlope,setSlope)
    
    Angle_B1 = AngleSlope(a,b,c,B1)
    Angle_B2 = AngleSlope(a,b,c,B2) 
    
    B1[abs(Angle_B1) > 0.001] = np.pi - B1[abs(Angle_B1) > 0.001]
    B2[abs(Angle_B2) > 0.001] = -np.pi - B2[abs(Angle_B2) > 0.001]    
    
    # Check if two periods really exist
    ID = np.ravel_multi_index(np.where(np.logical_and(B2 >= A1, B1 >= A2) == True),a.shape)
    Val = IntegrateSlope(constant,B2.flat[ID],B1.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    ID = ID[Val < 0]
    
    # Finally calculate resulting values
    Vals = np.zeros(B1.shape)

    Vals.flat[ID] = (IntegrateSlope(constant,A1.flat[ID],B2.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])  + 
                       IntegrateSlope(constant,B1.flat[ID],A2.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID]))
    ID = np.ravel_multi_index(np.where(Vals == 0),a.shape)   
    Vals.flat[ID] = IntegrateSlope(constant,A1.flat[ID],A2.flat[ID],delta,slope.flat[ID],slopedir.flat[ID],lat.flat[ID])
    
    return(Vals)

def Constants(delta,slope,slopedir,lat):
    # Equation 11
    a = np.sin(delta)*np.cos(lat)*np.sin(slope)*np.cos(slopedir) - np.sin(delta)*np.sin(lat)*np.cos(slope)
    b = np.cos(delta)*np.cos(lat)*np.cos(slope) + np.cos(delta)*np.sin(lat)*np.sin(slope)*np.cos(slopedir)
    c = np.cos(delta)*np.sin(slope)*np.sin(slopedir)
    return(a,b,c)

def AngleSlope(a,b,c,time):
    angle = -a + b*np.cos(time) + c*np.sin(time)
    return(angle)
    
def AngleHorizontal(delta,lat,time):
    angle = np.sin(delta)*np.sin(lat)+np.cos(delta)*np.cos(lat)*np.cos(time)
    return(angle)

def BoundsSlope(a,b,c):
    #Equation 13
    Div = (b**2+c**2)   
    Div[Div <= 0] = 0.00001
    sinB = (a*c + b*np.sqrt(b**2+c**2-a**2)) / Div
    sinA = (a*c - b*np.sqrt(b**2+c**2-a**2)) / Div
    
    sinB[sinB < -1] = -1; sinB[sinB > 1] = 1
    sinA[sinA < -1] = -1; sinA[sinA > 1] = 1
    
    sunrise = np.arcsin(sinA)
    sunset = np.arcsin(sinB)
    return(sunrise,sunset)
    
def TwoPeriods(delta,slope,lat):
    # Equation 7
    TwoPeriod = (np.sin(slope) > np.ones(slope.shape)*np.sin(lat)*np.sin(delta)+np.cos(lat)*np.cos(delta))
    return(TwoPeriod)
    
def BoundsHorizontal(delta,lat):
    # This function calculates sunrise hours based on earth inclination and latitude
    # If there is no sunset or sunrise hours the values are either set to 0 (polar night)
    # or pi (polar day)    
    bound = np.arccos(-np.tan(delta)*np.tan(lat))
    bound[abs(delta+lat) > np.pi/2] = np.pi
    bound[abs(delta-lat) > np.pi/2] = 0
    
    return(bound)

def IntegrateHorizontal(constant,sunrise,sunset,delta,lat):
    # Equation 4 & 6
    ws = np.arccos(-np.tan(delta)*np.tan(lat))
    integral = constant * (np.sin(delta)*np.sin(lat)*ws + np.cos(delta)*np.cos(lat)*np.sin(ws))
#    integral = constant * (np.sin(delta)*np.sin(lat)*(sunset-sunrise) 
#                + np.cos(delta)*np.cos(lat)*(np.sin(sunset)-np.sin(sunrise)))
    return(integral)

def IntegrateNormal(constant,sunrise,sunset):
    integral = constant * (sunset - sunrise)
    return(integral)

def IntegrateSlope(constant,sunrise,sunset,delta,slope,slopedir,lat):
    # Equation 5 & 6
    integral = constant * (np.sin(delta)*np.sin(lat)*np.cos(slope)*(sunset-sunrise) 
                - np.sin(delta)*np.cos(lat)*np.sin(slope)*np.cos(slopedir)*(sunset-sunrise)
                + np.cos(delta)*np.cos(lat)*np.cos(slope)*(np.sin(sunset)-np.sin(sunrise))
                + np.cos(delta)*np.sin(lat)*np.sin(slope)*np.cos(slopedir)*(np.sin(sunset)-np.sin(sunrise))
                - np.cos(delta)*np.sin(slope)*np.sin(slopedir)*(np.cos(sunset)-np.cos(sunrise)))
    return(integral)