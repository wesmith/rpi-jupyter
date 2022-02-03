#! /home/smithw/.tensorflow2/bin/python
# use python in (TF2) venv on acer: opencv installed there

# video_data_to_process.py
# WESmith 02/02/22


import change_detection_from_file as cd


'''
data_2022_0128 = {'basedir': '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house',
                  'subdir':  '2022_0128',
                  'mask':    'masks/2022_0128_104425_003.MP4.mask_2022_0201_212059.jpg',
                  'desc':    'very windy day! needs a mask',
                  'proc_range':   ('2022_0128_104425_003.MP4', '2022_0128_183227_159.MP4'),
                  'resdir':   'results'}

data_2022_0130 = {'basedir': '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house',
                  'subdir':  '2022_0130',
                  'mask':    None,
                  'desc':    'moderately windy: needs a mask',
                  'proc_range':   ('2022_0130_095940_173.MP4', '2022_0130_181743_339.MP4'),
                  'resdir':   'results'}

data_2022_0131 = {'basedir': '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house',
                  'subdir':  '2022_0131',
                  'mask':    None,
                  'desc':    'calm',
                  'old_range':   ('2022_0131_115846_353.MP4', '2022_0131_145549_412.MP4'),
                  'proc_range':   ('2022_0131_145849_413.MP4', '2022_0131_181648_479.MP4')}
'''

data_2022_0201 = {'basedir':           '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house',
                  'subdir':             '2022_0201',
                  'proc_range':   ('2022_0201_095506_492.MP4', '2022_0201_181907_660.MP4'),
                  'resdir':              'results',
                  'desc':               'calm day',
                  'mask':               None,
                  'fps_of_vid':         30,
                  'sec_per_vid':        180,
                  'num':                20,
                  'skip':               30,
                  'row_frac':           0.9,
                  'col_frac':           0.3}

data_2022_0202  = {'basedir':      '/media/smithw/SEAGATE-FAT/dashcam/Movie/from_house',
                  'subdir':       '2022_0202',
                  'proc_range':   ('2022_0202_101439_665.MP4', '2022_0202_182042_827.MP4'),
                  'resdir':       'results',
                  'desc':         'windy day: needs a mask',
                  'mask':         'masks/2022_0202_150243_761.MP4.mask_2022_0202_211605.jpg',
                  'fps_of_vid':   30,
                  'sec_per_vid':  180,
                  'num':          20,
                  'skip':         30,
                  'row_frac':     0.9,
                  'col_frac':     0.3}

# change-detection parameters
params_default = {'scale':        0.5,
                  'framecount':   15,
                  'blur_size':    3,
                  't_val':        5,
                  'alpha':        0.5,
                  'frameshow':    False}

data   = data_2022_0202
params = params_default

vp = cd.VideoProcess(data, params)
vp.show_filelist()
total, dt = vp.run()

print('\n{:0.2f} sec ({:0.2f} min) to process {} frames, or {:0.2f} frames/sec\n'.\
      format(dt, dt/60., total, total/dt))
