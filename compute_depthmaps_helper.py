from opensfm_modified import compute_depthmaps

def open_compute_depthmaps(file_path, opensfm_config, self_compute=False, self_path=''):
    cd = compute_depthmaps.ComputeDepthMapsCommand()
    cd.run(file_path, opensfm_config, self_compute, self_path)

