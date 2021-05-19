from opensfm_modified import export_ply


def open_export_ply(file_path, opensfm_config, self_compute=False, self_path=''):
    cd = export_ply.Command()
    cd.run(file_path, opensfm_config, self_compute, self_path)
