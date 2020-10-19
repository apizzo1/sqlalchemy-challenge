#  sqlalchemy-challenge

## Challenge Details

This challenge started with completing an analysis of climate data from a sqlite file using Python and SQL Alchemy. Next, a Flask application was created to display the results of the climate analysis that was completed.

### Python and SQL Alchemy Analysis of Climate Data

To start, 

## Some important notes:

1. For Temperature Analysis I, I decided to use a paired t-test. This is because the data is based on the same stations in the same locations, but at different times of the year. The data is based on the same groups and therefore a paired test should be used. My t-test indicated a value of 0.00012. This indicates that the difference in means between the temperature averages in June and the temperature averages in December is statistically significant.

2. I only used the Stations.csv for the analysis in Temperature Analysis II - in this section, I performed a join on the Measurement and Station data sets so I could return the station names, as well as their IDs. In all other sections, I only returned station IDs, since returning the station name did not seem to be needed.

### For the Flask section:

3. For the precipitation dictionary that is returned, this was based on the query performed in the jupyter notebook task for the Precipitation Analysis. Therefore, all stations were used. Since this challenge asked us to specifically "Convert the query results to a dictionary using date as the key and prcp as the value" this means that only one value was given per date, even if multiple stations reported precipitation on a particular date. The dictionary key (in this case, date) must be unique, and therefore, each time a repeat date is added to the dictionary, it just overwrites the previous one.

4. When the temperature observations were to be returned, I chose to return as a dictionary rather than a list. I felt this formatting was a little easier to read and would be more useful to a user.

5. For the section with user input dates, I used the data from all the stations for the requested date range, since no specific station was requested.
