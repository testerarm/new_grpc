import os
import struct
import pipes

from opendm import io
from opendm import log
from opendm import types
from opendm import system
from opendm import context
from opendm.cropper import Cropper
from opendm import point_cloud


def process(args, tree, reconstruction, current_path):
	odm_orthophoto = io.join_paths(current_path, 'orthophoto')
	odm_orthophoto_path = odm_orthophoto
	odm_orthophoto_render = io.join_paths(odm_orthophoto_path, 'odm_orthophoto_render.tif')
	odm_orthophoto_tif = io.join_paths(odm_orthophoto_path, 'odm_orthophoto.tif')
	odm_orthophoto_corners = io.join_paths(odm_orthophoto_path, 'odm_orthophoto_corners.tif')
	odm_orthophoto_log = io.join_paths(odm_orthophoto_path, 'odm_orthophoto_log.tif')		
        odm_orthophoto_tif_log = io.join_paths(odm_orthophoto_path, 'gdal_translate_log.txt')
	odm_25dgeoreferencing = io.join_paths(current_path, 'odm_georeferencing')
	odm_georeferencing = io.join_paths(current_path, 'odm_georeferencing')

	odm_georeferencing_coords = io.join_paths(
            odm_georeferencing, 'coords.txt')
        odm_georeferencing_gcp = io.find('gcp_list.txt', current_path)
        odm_georeferencing_gcp_utm = io.join_paths(odm_georeferencing, 'gcp_list_utm.txt')
        odm_georeferencing_utm_log = io.join_paths(
            odm_georeferencing, 'odm_georeferencing_utm_log.txt')
        odm_georeferencing_log = 'odm_georeferencing_log.txt'
        odm_georeferencing_transform_file = 'odm_georeferencing_transform.txt'
        odm_georeferencing_proj = 'proj.txt'
        odm_georeferencing_model_txt_geo = 'odm_georeferencing_model_geo.txt'
        odm_georeferencing_model_obj_geo = 'odm_textured_model_geo.obj'
        odm_georeferencing_xyz_file = io.join_paths(
            odm_georeferencing, 'odm_georeferenced_model.csv')
        odm_georeferencing_las_json = io.join_paths(
            odm_georeferencing, 'las.json')
        odm_georeferencing_model_laz = io.join_paths(
            odm_georeferencing, 'odm_georeferenced_model.laz')
        odm_georeferencing_model_las = io.join_paths(
            odm_georeferencing, 'odm_georeferenced_model.las')
        odm_georeferencing_dem = io.join_paths(
            odm_georeferencing, 'odm_georeferencing_model_dem.tif')

        opensfm_reconstruction = io.join_paths(current_path,'reconstruction.json')
	odm_texturing = io.join_paths(current_path,'mvs')
	odm_textured_model_obj = io.join_paths(odm_texturing, 'odm_textured_model.obj')
	images_dir = io.join_paths(current_path, 'images')
        tree = tree
	opensfm_bundle = os.path.join(current_path, 'opensfm', 'bundle_r000.out')
	opensfm_bundle_list = os.path.join(current_path, 'opensfm', 'list_r000.out')
	opensfm_transformation = os.path.join(current_path, 'opensfm', 'geocoords_transformation.txt')
	filtered_point_cloud = os.path.join(current_path, 'filterpoints', 'point_cloud.ply')
        

        doPointCloudGeo = True
        transformPointCloud = True
        verbose =''

        class nonloc:
            runs = []

        def add_run(primary=True, band=None):
            subdir = ""
            if not primary and band is not None:
                subdir = band

            # Make sure 2.5D mesh is georeferenced before the 3D mesh
            # Because it will be used to calculate a transform
            # for the point cloud. If we use the 3D model transform,
            # DEMs and orthophoto might not align!
	    b = True
            if b:
                nonloc.runs += [{
                    'georeferencing_dir': os.path.join(odm_georeferencing, subdir),
                    'texturing_dir': os.path.join(odm_texturing, subdir),
                }]
            
            if not args.skip_3dmodel and (primary or args.use_3dmesh):
                nonloc.runs += [{
                    'georeferencing_dir': odm_georeferencing,
                    'texturing_dir': os.path.join(odm_texturing, subdir),
                }]
        
        if reconstruction.multi_camera:
            for band in reconstruction.multi_camera:
                primary = band == reconstruction.multi_camera[0]
                add_run(primary, band['name'].lower())
        else:
            add_run()

        #progress_per_run = 100.0 / len(nonloc.runs)
        #progress = 0.0

        for r in nonloc.runs:
            if not io.dir_exists(r['georeferencing_dir']):
                system.mkdir_p(r['georeferencing_dir'])

            odm_georeferencing_model_obj_geo = os.path.join(r['texturing_dir'], odm_georeferencing_model_obj_geo)
            odm_georeferencing_model_obj = os.path.join(r['texturing_dir'], odm_textured_model_obj)
            odm_georeferencing_log = os.path.join(r['georeferencing_dir'], odm_georeferencing_log)
            odm_georeferencing_transform_file = os.path.join(r['georeferencing_dir'], odm_georeferencing_transform_file)
            odm_georeferencing_model_txt_geo_file = os.path.join(r['georeferencing_dir'], odm_georeferencing_model_txt_geo)
	    pio = True
	    
	    if pio:
            #if not io.file_exists(odm_georeferencing_model_obj_geo) or \
               #not io.file_exists(odm_georeferencing_model_laz)

                # odm_georeference definitions
		
                kwargs = {
                    'bin': context.odm_modules_path,
                    'input_pc_file': filtered_point_cloud,
                    'bundle': opensfm_bundle,
                    'imgs': images_dir,
                    'imgs_list': opensfm_bundle_list,
                    'model': odm_georeferencing_model_obj,
                    'log': odm_georeferencing_log,
                    'input_trans_file': opensfm_transformation,
                    'transform_file': odm_georeferencing_transform_file,
                    'coords': odm_georeferencing_coords,
                    'output_pc_file': odm_georeferencing_model_laz,
                    'geo_sys': odm_georeferencing_model_txt_geo_file,
                    'model_geo': odm_georeferencing_model_obj_geo,
                    'verbose': verbose
                }

                if transformPointCloud:
                    kwargs['pc_params'] = '-inputPointCloudFile {input_pc_file} -outputPointCloudFile {output_pc_file}'.format(**kwargs)

                    if reconstruction.is_georeferenced():
                        kwargs['pc_params'] += ' -outputPointCloudSrs %s' % pipes.quote(reconstruction.georef.proj4())
                    else:
                        log.ODM_WARNING('NO SRS: The output point cloud will not have a SRS.')
                else:
                    kwargs['pc_params'] = ''
 
                if io.file_exists(opensfm_transformation) and io.file_exists(odm_georeferencing_coords):
                    log.ODM_INFO('Running georeferencing with OpenSfM transformation matrix')
                    system.run('{bin}/odm_georef -bundleFile {bundle} -inputTransformFile {input_trans_file} -inputCoordFile {coords} '
                               '-inputFile {model} -outputFile {model_geo} '
                               '{pc_params} {verbose} '
                               '-logFile {log} -outputTransformFile {transform_file} -georefFileOutputPath {geo_sys}'.format(**kwargs))
                elif io.file_exists(odm_georeferencing_coords):
		    print('running georeferencing')
                    log.ODM_INFO('Running georeferencing with generated coords file.')
                    system.run('{bin}/odm_georef -bundleFile {bundle} -inputCoordFile {coords} '
                               '-inputFile {model} -outputFile {model_geo} '
                               '{pc_params} {verbose} '
                               '-logFile {log} -outputTransformFile {transform_file} -georefFileOutputPath {geo_sys}'.format(**kwargs))
                else:
                    log.ODM_WARNING('Georeferencing failed. Make sure your '
                                    'photos have geotags in the EXIF or you have '
                                    'provided a GCP file. ')
                    doPointCloudGeo = False # skip the rest of the georeferencing

                if doPointCloudGeo:
                    reconstruction.georef.extract_offsets(odm_georeferencing_model_txt_geo_file)
                    point_cloud.post_point_cloud_steps(args, tree)
                    
                    if args.crop > 0:
                        log.ODM_INFO("Calculating cropping area and generating bounds shapefile from point cloud")
                        cropper = Cropper(odm_georeferencing, 'odm_georeferenced_model')
                        
                        decimation_step = 40 if args.fast_orthophoto or args.use_opensfm_dense else 90
                        
                        # More aggressive decimation for large datasets
                        if not args.fast_orthophoto:
                            decimation_step *= int(len(reconstruction.photos) / 1000) + 1

                        cropper.create_bounds_gpkg(odm_georeferencing_model_laz, args.crop, 
                                                    decimation_step=decimation_step)

                    # Do not execute a second time, since
                    # We might be doing georeferencing for
                    # multiple models (3D, 2.5D, ...)
                    doPointCloudGeo = False
                    transformPointCloud = False
            else:
                log.ODM_WARNING('Found a valid georeferenced model in: %s'
                                % odm_georeferencing_model_laz)

            if args.optimize_disk_space and io.file_exists(odm_georeferencing_model_laz) and io.file_exists(filtered_point_cloud):
                os.remove(filtered_point_cloud)
            
            #progress += progress_per_run
            #self.update_progress(progress)
