import geojson
import pandas as pd
from shapely.geometry import MultiPolygon, asShape

with open('DPW_StreetSweepingAreas.geojson') as f:
    fc = geojson.loads(f.read(), object_hook=geojson.GeoJSON.to_instance)

df = pd.DataFrame([{'name': f.properties['SweepArea'], 
                    'geometry' : asShape(f.geometry)} for f in fc.features])

# Combine the split geometries into MultiPolygons.
# D1, D2 as well as J1, J2, J3.  Leave the single areas as regular Polygons
grouped = df.groupby(df['name'].str[0])['geometry']
df_geoms = grouped.agg(lambda x: MultiPolygon(list(x)) if len(x) > 1
                       else x.iloc[0])

# Now grab the table from the city's website
dfs = pd.read_html('http://www.cambridgema.gov/theworks/ourservices/streetcleaning/schedulesandroutes.aspx', infer_types=False, index_col=[0, 1], header=0)
df = dfs[0]
# Appreciate those last two lines.  Pandas is awesome.

schedule = df.ix[:, 'Apr':]

# Special days are indicated by the full month and day. Just check length.
special = schedule.apply(lambda x: x.str.len() > 2)
canceled = schedule.apply(lambda x: x.str.contains('canceled'))

# Prepend the month names to the date.
schedule[~special] = schedule.columns.values + ' ' + schedule + ' 2013'

# Fill in with random date since it will make the parsing easier later
schedule[canceled] = '1/1/2013'

# Convert all values to datetimes. Let to_datetime() take care of parsing.
# Then re-format as abbreviated month and day. This puts everything in a
# common format since the original data contains a mix of full month names
# and different abbreviations
schedule = schedule.apply(pd.to_datetime)
schedule = schedule.applymap(lambda x: x.strftime('%b %d'))
schedule[canceled] = pd.np.nan  # Put back in the missing data

# Put an asterisk in front of special days and combine all days as a list
schedule[special] = '*' + schedule[special]
schedule = schedule.apply(lambda x: ', '.join(x[x.notnull()]), axis=1)

# Re-orient so that the index is district and the columns are Even, Odd
schedule = schedule.unstack(level=1)

# Create a summary field that looks like "Odd: 1st Wed, Even: 1st Thur"
df.reset_index(level=1, inplace=True)
summary = (df['Side'] + ': ' + df['Day']).groupby(level=0).agg(', '.join)

# Piece all the data together in one DataFrame
# For some reason here I have to reference Odd and Even from schedule
data = pd.concat([df_geoms, summary, schedule['Even'], schedule['Odd']], axis=1)
data.columns = ['geometry', 'Summary', 'Even', 'Odd']
data['District'] = data.index

# Convert the geometry to the GeoJSON representation. GeoPandas might help
# here?
features = []
for id_, row in data.iterrows():
    props = row[['District', 'Summary', 'Even', 'Odd']].to_dict()
    feature = geojson.Feature(id=id_, geometry=row['geometry'], properties=props)
    features.append(feature)

fc = geojson.FeatureCollection(features)
with open('cambridge_sweep_areas.geojson', 'w') as f:
    f.write(geojson.dumps(fc))
