import numpy as np
import datetime
from dateutil.relativedelta import relativedelta


# we now need to work on the dates
# got through entire list and return those within the given point and range
# first checks finest resolution is a day
# frist and last should be outliers
def select_dates(dates,time_u,time_w,diag = False):
    window = False
    dates_u = []
    # extra check for aligning frst date
    # then we need an empty extended entry
    print(time_u - dates[0])
    if (time_u - dates[0] ).days   == 0:
        dates_u.append([])

    for n,d in enumerate(dates):
        # go along list checking if we get passed time_u

        if ((time_u - d ).days -1 < 0) and not window:
            window = True
#             print(d.strftime('%Y%m%d'))
            # we also need the 'bracket slices'
            # either side of the date in interest
            # so to interpolate when there isn't any
            if n > 0: dates_u.append(dprev)  

        if window: dates_u.append(d)    

        if (time_u + time_w) < d:
#             print(d.strftime('%Y%m%d'))
            window = False
            break
        dprev = d
    # if we've reached the end and swe're still windowing, add an empty entry
    if window:
        dates_u.append([])
    if diag:
        [print(d.strftime('%Y%m%d')) for d in dates_u if type(d)==dt.datetime]
    if len(dates_u)==1:
        dnew = [[],dates_u[0],[]]
        dates_u = dnew
    return dates_u



#### strangely spaced daily data to monthly weightings
# datesQ ,  query list or data points
# time_u , beginning of window we want
# time_w, shape of window
# datesQ will contain a list of dates that exceed the window, 
#        first comes before, last comes after
# need to return d_load (dates to load, can be many)
#        return wi (weights of loadings, can be many)
def get_load_points(datesQ,time_u,time_w,diag=False):
    def date_weight2(time_q,time_0,time_1):
        ### between two dates (or hitting one)
        if time_0 == []:
            return 0.0,1.0
        elif time_1 == []:
            return 1.0,0.0
        dgap = (time_1-time_0).days
        dgap0 = (time_q- time_0).days
        w0 = 1-dgap0/dgap 
        w1 = dgap0/dgap 
        return w0, w1
    wi = np.zeros([len(datesQ)])
    if diag:
        print('datesQ length = '+str(np.shape(datesQ)[0]))
        if np.shape(datesQ)[0] ==1:
            print(datesQ[0].strftime('%Y%m%d'))
    # then we're doing some sort of days interp so use the endpoints
    # go along every day in time_u + time_w
    # find the dates each d is in
    # get the weights for those days and count
    ndays = ((time_u+time_w) - time_u).days + 1
    # days window indexes
    its = 0
    ite = 1
    for nd in range(ndays):
        ### update day is passed
        d = time_u + relativedelta(days=nd)
        if d>datesQ[ite]:
            its+=1
            ite+=1
            if diag:
                print('date update,',d.strftime('%Y%m%d'))
        ### calc weights
        w0,w1 = date_weight2(d,datesQ[its],datesQ[ite])
        #### update
        wi[its] += w0
        wi[ite] += w1
    wtot = wi.sum()
    wi = wi/wtot
    return wi
