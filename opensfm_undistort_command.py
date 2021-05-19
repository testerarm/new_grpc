from opensfm_modified import undistort


def opensfm_undistort(file_path, opensfm_config, self_compute=False, self_path=''):
    u =undistort.UndistortCommand()
    if self_compute:
        u.run(file_path, opensfm_config, self_compute, self_path)
    else:
        u.run(file_path, opensfm_config)