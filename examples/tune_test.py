# -*- coding: utf-8 -*-
"""
Tune test
=========

An example of transform on a tune test.
"""

import matplotlib.pyplot as plt

import WrightTools as wt
from WrightTools import datasets

p = datasets.PyCMDS.w1_wa_000
data = wt.data.from_PyCMDS(p)

fig, gs = wt.artists.create_figure(width='double', cols=[1, 1, 'cbar'])

# as taken
ax = plt.subplot(gs[0, 0])
ax.pcolor(data.w1__e__wm.full, data.wa.full, data.array_signal)
wt.artists.set_ax_labels(xlabel=data.w1__e__wm.label, ylabel=data.wa.label)
ax.set_title('as taken', fontsize=20)

# transformed
ax = plt.subplot(gs[0, 1])
data.transform(['w1', 'wa-w1'])
ax.pcolor(data.w1.full, data.wa__m__w1.full, data.array_signal)
wt.artists.set_ax_labels(xlabel=data.w1.label, ylabel=data.wa__m__w1.label)
ax.set_title('transformed', fontsize=20)

# colorbar
cax = plt.subplot(gs[0, -1])
wt.artists.plot_colorbar(cax, label='amplitude')
