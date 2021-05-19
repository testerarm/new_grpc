
from opensfm_modified import export_visualsfm


#### export visualsfm


def open_export_visualsfm(file_path, opensfm_config):
    ev = export_visualsfm.VisualSFMCommand()
    ev.run(file_path, opensfm_config)
