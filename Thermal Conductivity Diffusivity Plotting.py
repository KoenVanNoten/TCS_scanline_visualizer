# # coding: utf-8

##       S-RA: Temperature - TC - TD plotter
##       Koen VAN NOTEN
##       Geological Survey of Belgium
##       v1.0: 28 February 2018 - TC plotter
##       v1.1: 13 March 2018 - TC - TC-TD - TD plotter
##       v1.2: 18 September 2018: Let user decide to make a TC or a TC and TC/TD plotter
##             20 September 2018: no more -990.90 errors anymore + XXX_position request added

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MultipleLocator
import matplotlib.gridspec as gridspec
import pylab as P
import timeit

start = timeit.default_timer()

###################################################################
### SAVE THIS PYTHON SCRIPT IN THE FOLDER OF THE TC TXT FILES   ###
###           DEFINE THE PRE-SETS OF THE PLOTS                  ###
###################################################################


# Which borehole
measurement = ['084W1478', 'Waregem', '217.20']

# What's the number of the scanline ?
place = 1

#How many measurements: default = 3
TC_rep = np.arange(1, 4, 1)  # how many TC measurements were performed in the TC module: 1-3
TD_rep = np.arange(4, 7, 1)  # how many TD measurements were performed in the TD module: 4-6

### Do you want only a TC plot (returns 1 TC profile) or do also want the TC-TD module plots (returns 1 TC and 2 TC-TD profiles)
### If Also_TD = True: it returns both TC and TD profiles
Also_TD = True

### Do you want to set the maximum x position of the whole plot set automatic of manually?
### True if automatic  #False if manually
xposition = True
poss_max = 330  # If manually, define the maximum length of the scan (=position after the last standard)

### If XXX_position is True, give me the 5 mean TC values (from the 3 .txt files) before and after the given XXX position (in mm distance on the TCS)
XXX_position = True
XXX = 250

### Do you want to find the position value where Temperature quickly rises to find 0-point of the sample on the TCS ?
T_sampling = True   # if True: find automatic min and max T values before and after sample_zero
sample_zero = 100    # Give expected position
dist_treshhold = 15  # print distance before and after the 0-position (in mm)

### Colors to plot the TC and TD measurements. Nr of colors need to be the same as nr of
### repetitive measurements. E.g. if only 2 TC measurements, remove a color. Default = 3 measurements
colors_TC = ['green', 'purple', 'orange']
colors_TD = ['grey', 'red', 'darkslateblue']

### Temperature boundaries: range in between the temperature profile needs to be plotted
T_auto = 1 # = True: find automatic min and max Temperature values
Tmin = 20
Tmax = 26

### X-scale of the normalised histogram
hist_auto = True # = True: find automatic min and max histogram value
histo_max = 0.5   # define Maximum of the normalised histogram (sum of all values = 1)
bin_width = 0.05  # width of the bin in the histogram

### Do you want to set the TC and/or TD scale automatic of define it manually?
TCscale = True  # True if automatic; False if manually
range = 0.5  # If automatic: set range above and below the max. TC/TD value
TCmin = 1.9  # If manually, define TC - TD boundaries
TCmax = 3.1
TDmin = 0.5
TDmax = 1.5

#############################################
### From here starts the automatic script ###
#############################################

borehole = measurement[0]
borehole_loc = measurement[1]
depth = measurement[2]

# Select data in the TC / TD .txt file
SC_pos = "SensorCold_Position (mm)"
SH_pos = "SensorHot_Position (mm)"
SC_T = "SensorCold_Temperature (C)"
SH_T = "SensorHot_Temperature (C)"
SHy_T = "SensorHoty:_Temperature (C)"
names = ["Platform: Position (mm)", "Source_Position (mm)", "Source_U (V)", "Source_I (A)", "Source_P (W)",
         SC_pos, "SensorCold_Voltage (mV)", SC_T, SH_pos, "SensorHot_Voltage (mV)", SH_T,
         "Velocity (mm/s)", "NumPerInterval", "Num", "Time (s)"]
names_TD = names + ["SensorHoty:_Voltage (mV)", SHy_T]

# Empty data used for storing the means etc...
means = []
means_TC_TD = []
means_TD = []
hists = []
n_max = []
hists_TC_TD = []
hists_TD = []
locs = []
locs_TC_TD = []
TCs = []
TC_TDs = []
TDs = []
poss = []
poss_TC_TD = []
n_TC = []
n_TC_TD = []
n_TD = []

### Function to plot 1 histogram from 1 .txt file
def histogram_loop(TC_TD, name, hists, means):
    bins = np.arange(0., 10, bin_width)
    n, bins, patches = P.hist(TC_TD, bins, normed=0, histtype='bar', rwidth=1, alpha=0.0,
                              orientation='horizontal', fill='white', edgecolor='white', stacked=True)
    print("     ", name, "mean = ", round(np.mean(TC_TD), 3))
    print("     ", name, "modus = ", round(bins[np.argmax(n)] + 0.025, 3))
    hists.append(round(bins[np.argmax(n)] + 0.025, 3))
    means.append(round(np.mean(TC_TD), 3))

### Function to plot 1 TC or TD plot true the points derived from 1 .txt file
def TC_TD_plotter_loop(ax, TC_TD, name, color):    #for each .txt file, plot 1 histogram
    ax.plot(pos_processed, TC_TD, lw=0.8, color=color)
    mean = round(np.mean(TC_TD), 3)
    plt.axhline(mean, ls='--', linewidth=0.4,
                zorder=-100, label=(name + " %s" % place + '.%s' % i + ': %s' % mean), color='white')
    plt.legend(loc='upper left', fontsize=7, ncol=1)

### Function to quickly scale all x-axes
def xlocator(ax, xmajloc, xminloc):
    ax.xaxis.set_major_locator(MultipleLocator(base=xmajloc))
    ax.xaxis.set_minor_locator(MultipleLocator(base=xminloc))

### Function to quickly scale all y-axes
def ylocator(ax, ymajloc, yminloc):
    ax.yaxis.set_major_locator(MultipleLocator(base=ymajloc))
    ax.yaxis.set_minor_locator(MultipleLocator(base=yminloc))

### Function to round the limits of the plot to x5
def round5(x):
    return int(round(x * 2, -1)) / 2

### Function to plot the TC or TD histogram from text files generated in the TC or TD module
def TC_TD_histogram(ax, TC_TDs, name, mean, color, TC_value):
    weights = []
    bins = np.arange(0.0, 10, bin_width)
    for i in np.arange(0, len(TC_TDs), 1):
        weight = np.ones_like(TC_TDs[i]) / float(len(TC_TDs[i]))
        weights.append(weight / len(TC_TDs))
    n_counts, bins, patches = P.hist(TC_TDs, bins, stacked=1,
                                     fill='transparant', edgecolor='white', zorder=-500, lw=0.)
    n, bins, patches = P.hist(TC_TDs, bins, weights=weights, histtype='bar', rwidth=1,
                              orientation='horizontal', stacked=1, color=color, edgecolor='black', zorder=100, lw=0.35)
    plt.axhline(bins[np.argmax(n[len(TC_TDs) - 1])] + 0.025, linewidth=0.5, zorder=-100, color='red')

    print(name + " nr of observations: %s" % int(sum(n_counts[len(TC_TDs) - 1])))
    print(name + " Modus =  %s" % (bins[np.argmax(n[len(TC_TDs) - 1])] + 0.025))
    xlocator(ax, 0.2, 0.05)  # x-scale of the normed histogram

    if hist_auto:
        n_max.append(round(np.max(n),2))

    if np.max(TC_TDs[len(TC_TDs) - 1]) - np.min(TC_TDs[len(TC_TDs) - 1]) > 5:
        ylocator(ax, 2, 1)
    else:
        ylocator(ax, 1, .2)
    if TCscale:
        if name == "TC_TD":
            plt.ylim(np.min(TC_value[len(TC_value) - 1]) - range, np.max(TC_value[len(TC_value) - 1]) + range)
        else:
            plt.ylim(np.min(TC_TDs[len(TC_TDs) - 1]) - range, np.max(TC_TDs[len(TC_TDs) - 1]) + range)
    else:
        if name == "TD":
            plt.ylim(TDmin, TDmax)
        else:
            plt.ylim(TCmin, TCmax)
    plt.axhline(np.mean(mean), linewidth=0.5, zorder=-100, color='blue')

    plt.axhline(-100, color='white', label='n = %s' % int(sum(n_counts[len(TC_TDs) - 1])))
    ax.yaxis.tick_right()
    plt.legend(loc='upper right', fontsize=7, frameon=False)

### Function to plot the TC or TD values from the text files generated in the TC or TD module
def TC_TD_plot(ax, TC_TDs, name, mean, poss, max, TC_value):
    print(name + " Mean =  %s" % round(np.mean(mean), 3))
    bins = np.arange(0.0, 10, bin_width)
    n, bins, patches = P.hist(TC_TDs, bins, stacked=1,
                              fill='transparant', edgecolor='white', zorder=-500, lw=0.)

    # finding middle value of the maximum cumulative histogram
    TC_TD_hist = round(bins[np.argmax(n[len(TC_TDs) - 1])] + 0.025,3)
    plt.axhline(TC_TD_hist, linewidth=0.5, zorder=-100, color='red', label="Modus: %s" % TC_TD_hist)

    xlocator(ax, 50, 10)
    if np.max(TC_TDs[len(TC_TDs) - 1]) - np.min(TC_TDs[len(TC_TDs) - 1]) > 5:
        ylocator(ax, 2, 1)
    else:
        ylocator(ax, 1, .2)
    if name == "TC":
        plt.ylabel('TC \n(W/(m.K))')
    if name == "TC_TD":
        plt.ylabel('TC \n(W/(m.K))')
    if name == "TD":
        plt.ylabel('TD \n' + r'(mm$^{\rm 2}$/s)')
    if xposition:
        xmax = round5(np.max(df[SH_pos])) - 1
        plt.xlim(0, xmax)
    else:
        plt.xlim(0, max)
    if TCscale:
        if name == "TC_TD":
            plt.ylim(np.min(TC_value[len(TC_value) - 1]) - range, np.max(TC_value[len(TC_value) - 1] + range))
        else:
            plt.ylim(np.min(TC_TDs[len(TC_TDs) - 1]) - range, np.max(TC_TDs[len(TC_TDs) - 1]) + range)
    else:
        if name == "TC":
            plt.ylim(TCmin, TCmax)
        if name == "TC_TD":
            plt.ylim(TCmin, TCmax)
        if name == "TD":
            plt.ylim(TDmin, TDmax)
    plt.grid(lw=0.4, zorder=-200)
    plt.axhline(np.mean(mean), linewidth=0.5,
                zorder=-100, label="Mean: %s" % round(np.mean(mean), 3), color='blue')

    if name == "TC":
        plt.axvline(np.min(poss[len(TC_TDs) - 1]), color='grey', linewidth=0.8, zorder=-100)
        plt.axvline(np.max(poss[len(TC_TDs) - 1]), color='grey', linewidth=0.8, zorder=-100)
    else:
        plt.axvline(np.min(poss[len(TC_TDs) - 1]), color='grey', linewidth=0.8, zorder=-100, ls='--')
        plt.axvline(np.max(poss[len(TC_TDs) - 1]), color='grey', linewidth=0.8, zorder=-100, ls='--')
    legend = plt.legend(loc='upper left', fontsize=7, ncol=1)
    frame = legend.get_frame()
    frame.set_facecolor('white')
    frame.set_facecolor('1')
    frame.set_alpha(1.0)


### Making the figure now
if Also_TD:
    gs = gridspec.GridSpec(4, 2, hspace=0.0, wspace=0.05, height_ratios=[2, 1, 1, 1], width_ratios=[8, 1])
    fig = plt.figure(figsize=(7, 7))
else:
    gs = gridspec.GridSpec(2, 2, hspace=0.0, wspace=0.05, height_ratios=[2, 1], width_ratios=[8, 1])
    fig = plt.figure(figsize=(7, 5))

### Loop over the individual TC measurements (text files x.1 to x.3)
for i, color in zip(TC_rep, colors_TC):
    in_filespec_TC = borehole + ' - %s' % depth + ' - %s' % place + ".%s" % i + ".tx0"
    print(in_filespec_TC)

    # Set the empty TC data to store
    pos_processed = []
    SC_T_processed = []
    SH_T_processed = []
    pos_np = []
    T_np = []
    TC = []

    with open(in_filespec_TC) as file:
        for line in file:
            if line.startswith('p4'):
                split = line.strip().split()
                pos_processed.append(split[1])
                SC_T_processed.append(split[2])
                SH_T_processed.append(split[3])
                TC.append(split[4])
            if line.startswith('p0'):
                split = line.strip().split()
                pos_np.append(split[1])
                T_np.append(split[3])
    pos_processed = np.array(pos_processed[2:])
    pos_processed = pos_processed.astype(np.float)
    SC_T_processed = np.array(SC_T_processed[2:])
    SC_T_processed = SC_T_processed.astype(np.float)
    SH_T_processed = np.array(SH_T_processed[2:])
    SH_T_processed = SH_T_processed.astype(np.float)

    TC = np.array(TC[2:])
    TC = TC.astype(np.float)

    # gather all TC data
    TCs.append(TC)
    locs.append('%s' % place + '.%s' % i)
    poss.append(pos_processed)

    # define the TC histogram
    ax3 = plt.subplot(gs[3])
    histogram_loop(TC, "TC", hists, means)

    # Make the TC plotter
    ax2 = plt.subplot(gs[2])
    TC_TD_plotter_loop(ax2, TC, "TC", color)

    # make the temperature plot
    ax0 = plt.subplot(gs[0])
    df = pd.read_csv(in_filespec_TC, comment="\"", delim_whitespace=True, names=names, header=None,
                     usecols=np.arange(len(names)) + 1)
    df = df.dropna()
    df = df[:-1]
    df.index = df["Platform: Position (mm)"]
    plt.plot(df[SC_pos], df[SC_T], label="SC%s" % place + '.%s' % i, lw=1, color=color)
    plt.plot(df[SH_pos], df[SH_T], label="SH%s" % place + '.%s' % i, lw=1, color=color)
    plt.legend()

    # Print the position where temperatures starts rising near the sample
    if T_sampling:
        for i in np.arange(sample_zero + 43 - dist_treshhold, sample_zero + 53 - dist_treshhold, 1):
            print("     Hot Sensor T at", pos_np[i], "mm =", T_np[i], "°C")

if XXX_position:
    poss = np.array(poss)
    # print poss.mean(0)
    for index, item in enumerate(poss.mean(0)):
        if item > XXX - 4 and item < XXX + 5  :
            print("Mean TC at", round(item,2), "mm = ", TC[index], " W/(m.K)")


# Loop over the individual TC_TD and TD measurements (text files x.4 to x.6)
if Also_TD:
    for i, color_TD in zip(TD_rep, colors_TD):
        # use data from TD module
        in_filespec_TD = borehole + ' - %s' % depth + ' - %s' % place + ".%s" % i + ".tx0"
        pos_processed = []
        SC_T_processed = []
        SH_T_processed = []
        TC_TD = []
        TD = []

        print(in_filespec_TD)


        with open(in_filespec_TD) as file2:
            for line in file2:
                if line.startswith('p9 " TD after final correction'):
                    next(file2)
                elif line.startswith('p9 "Sample 1 = ' + borehole):
                    next(file2)
                elif line.startswith('p9'):
                    split = line.strip().split()
                    pos_processed.append(split[1])
                    SC_T_processed.append(split[2])
                    SH_T_processed.append(split[3])
                    TC_TD.append(split[4])
                    TD.append(split[7])
                if line.startswith('p0'):
                    split = line.strip().split()
                    pos_np.append(split[1])
                    T_np.append(split[3])
        pos_processed = np.array(pos_processed)
        pos_processed = pos_processed.astype(np.float)
        SC_T_processed = np.array(SC_T_processed)
        SC_T_processed = SC_T_processed.astype(np.float)
        SH_T_processed = np.array(SH_T_processed)
        SH_T_processed = SH_T_processed.astype(np.float)
        TC_TD = np.array(TC_TD)
        TC_TD = TC_TD.astype(np.float)
        TD = np.array(TD)
        TD = TD.astype(np.float)

        # gather all TC_TD and TD data
        TC_TDs.append(TC_TD)
        TDs.append(TD.astype(np.float))
        locs_TC_TD.append('%s' % place + '.%s' % i)
        poss_TC_TD.append(pos_processed)

        # define the TC_TD histogram
        ax5 = plt.subplot(gs[5])
        histogram_loop(TC_TD, "TC_TD", hists_TC_TD, means_TC_TD)

        # Make the TC_TD plotter
        ax4 = plt.subplot(gs[4])
        TC_TD_plotter_loop(ax4, TC_TD, "TC", color_TD)

        # define the TD histogram
        ax7 = plt.subplot(gs[7])
        histogram_loop(TD, "TD", hists_TD, means_TD)

        # Make the TD plotter
        ax6 = plt.subplot(gs[6])
        TC_TD_plotter_loop(ax6, TD, "TD", color_TD)

        # make the termperature plot
        ax0 = plt.subplot(gs[0])
        df = pd.read_csv(in_filespec_TD, comment="\"", delim_whitespace=True, names=names_TD, header=None,
                         usecols=np.arange(len(names_TD)) + 1)
        df = df.dropna()
        df.index = df["Platform: Position (mm)"]
        plt.plot(df[SC_pos], df[SC_T], label="SC%s" % place + '.%s' % i, lw=1, ls='-.', color=color_TD)
        plt.plot(df[SH_pos], df[SHy_T], label="SHy%s" % place + '.%s' % i, lw=1, ls='-.', color=color_TD)
        plt.plot(df[SH_pos], df[SH_T], label="SH%s" % place + '.%s' % i, lw=1, ls='-.', color=color_TD)
        plt.legend()

        # Print the treshhold temperatures
        if T_sampling:
            for i in np.arange(sample_zero + 43 - dist_treshhold, sample_zero + 53 - dist_treshhold, 1):
                print("     Hot Sensor T at", pos_np[i], "=", T_np[i], "°C")

xmax = np.max(df[SH_pos])
bins = np.arange(0., 10, 0.05)

## plot the Temperature profiles
ax0 = plt.subplot(gs[0])
xlocator(ax0, 50, 10)
ylocator(ax0, 1, 0.5)
if xposition:
    xmax = round5(np.max(df[SH_pos])) - 1
    print('')
    print(" ######## MEAN ALL DATA ######")
    print("Maximum xposition : ", round5(np.max(df[SH_pos])) - 1)

    plt.xlim(0, xmax)
else:
    plt.xlim(0, poss_max)

if T_auto:
    T_min_auto = np.min(df[SC_T]) - 2
    T_max_auto = np.max(df[SH_T]) +0.5
    plt.ylim(T_min_auto, T_max_auto)
else:
    plt.ylim(Tmin, Tmax)
plt.grid(lw=0.4, zorder=-200)
plt.ylabel("Temperature \n(" + u"\u00b0" + "C)")
ax0.axes.xaxis.set_ticklabels([])  # don't show the x-labels for the first plot

### Plot vertical grey lines between those locations where the TC / TD sample measurements are done on the TCS
plt.axvline(np.min(poss[len(TCs) - 1]), color='grey', linewidth=0.8, zorder=-100)
plt.axvline(np.max(poss[len(TCs) - 1]), color='grey', linewidth=0.8, zorder=-100)
if Also_TD:
    plt.axvline(np.min(poss_TC_TD[len(TC_TDs) - 1]), color='grey', ls='--', linewidth=0.8, zorder=-100)
    plt.axvline(np.max(poss_TC_TD[len(TC_TDs) - 1]), color='grey', ls='--', linewidth=0.8, zorder=-100)
if Also_TD:
    plt.legend(ncol = 5, loc=8, fontsize=7)
else:
    plt.legend(ncol = 3, loc=8, fontsize=7)

########### Call all the functions

## TC Histogram plot
ax3 = plt.subplot(gs[3])
TC_TD_histogram(ax3, TCs, "TC", means, colors_TC, TCs)
if hist_auto:
    plt.xlim(0, np.max(n_max)+0.05)
    if np.max(n_max) < 0.1:
        xlocator(ax3, 0.1, 0.05)  # x-scale of the normed histogram
    else:
        xlocator(ax3, 0.2, 0.05)
else:
     plt.xlim(0, histo_max)
ax3.xaxis.set_ticks_position('top')
if Also_TD == False:
    plt.xlabel('Frequency')

## TC plot
ax2 = plt.subplot(gs[2])
TC_TD_plot(ax2, TCs, "TC", means, poss, poss_max, TCs)
if Also_TD:
    ax2.axes.xaxis.set_ticklabels([])  # hide x-label if TD plot follows
else:
    plt.xlabel('Position (mm)')

if Also_TD:
    ## TC_TD Histogram plot
    ax5 = plt.subplot(gs[5])
    TC_TD_histogram(ax5, TC_TDs, "TC_TD", means_TC_TD, colors_TD, TCs)
    if hist_auto:
        plt.xlim(0, np.max(n_max) + 0.05)
    else:
        plt.xlim(0, histo_max)
    ax5.axes.xaxis.set_ticklabels([])  # hide x-label

    ## TC_TD plot
    ax4 = plt.subplot(gs[4])
    TC_TD_plot(ax4, TC_TDs, "TC_TD", means_TC_TD, poss_TC_TD, poss_max, TCs)
    ax4.axes.xaxis.set_ticklabels([])  # hide x-label

    ## TD Histogram plot
    ax7 = plt.subplot(gs[7])
    TC_TD_histogram(ax7, TDs, "TD", means_TD, colors_TD, TCs)
    if hist_auto:
        plt.xlim(0, np.max(n_max) + 0.05)
    else:
        plt.xlim(0, histo_max)
    plt.xlabel('Frequency')

    ## TD plot
    ax6 = plt.subplot(gs[6])
    TC_TD_plot(ax6, TDs, "TD", means_TD, poss_TC_TD, poss_max, TCs)
    plt.xlabel('Position (mm)')

#Define Title of the plot
ax0 = plt.subplot(gs[0])
if Also_TD:
    plt.title("TC/TD analysis of " + borehole + " " + borehole_loc + ', ' + depth + ' m - %s' % place)
else:
    plt.title("TC analysis of " + borehole + " " + borehole_loc + ', ' + depth + ' m - %s' % place)

# Figure will be saved in the map of the raw measurements
if Also_TD:
    plt.savefig(borehole + ' - ' + depth + ' - %s' % place + '-TC-TD.png', dpi=600)
else:
    plt.savefig(borehole + ' - ' + depth + ' - %s' % place + '-TC.png', dpi=600)


stop = timeit.default_timer()
print('Computation Time: ', stop - start)
plt.show()