import lib
import os 
import os.path
import collections


from threading import Thread
from Queue import Queue
import opensfm_interface


from opensfm_modified import new_pairs_selection
import threading
import sys

from timeit import default_timer as timer
from opensfm_modified import submodel_creation
import traceback

import json

from opendm import photo
from opendm import types
from opendm import log



def write_json(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)


def write_json_append(data, filename):
    if not os.path.isfile(filename):
        write_json(data, filename)
    else:
        with open(filename) as f:
            old_data = {}
            try:
                old_data = json.load(f)
            except Exception as e:
                print(e.message)
                pass
            except:
                pass
            data.update(old_data)

        write_json(data, filename)  

def save_images_database(photos, database_file):
    with open(database_file, 'w') as f:
        f.write(json.dumps(map(lambda p: p.__dict__, photos)))
    
    log.ODM_INFO("Wrote images database: %s" % database_file)

def load_images_database(database_file):
    # Empty is used to create types.ODM_Photo class
    # instances without calling __init__
    class Empty:
        pass

    result = []

    log.ODM_INFO("Loading images database: %s" % database_file)

    with open(database_file, 'r') as f:
        photos_json = json.load(f)
        for photo_json in photos_json:
            p = Empty()
            for k in photo_json:
                setattr(p, k, photo_json[k])
            p.__class__ = types.ODM_Photo
            result.append(p)

    return result   

if __name__ == '__main__':
    
    #lib.FileServer(8888, 1, 'node1').start(8888)

    start_time = timer()

    # one node process



    try:


        nodeid = 1
        nodeid_list = [1]
        node_client = {}
        

        node_imagelist = {}
        node_imagelist[1] = []
        node_imagelist[2] = []




        nodes_available = {2: True}
        max_concurrency = 4


        images_filepath = '/home/vm1/Desktop/ODM/grpc_stages/node1'  #file path of current node images
        file_path = images_filepath + '/'
        opensfm_config = opensfm_interface.setup_opensfm_config(file_path)
        active_number_of_nodes = 1
        photos_name = collections.defaultdict(lambda : "None")
        photo_list =  os.listdir(os.path.join(images_filepath, 'images'))
        print(photo_list)

        image_sent_nodes = collections.defaultdict(lambda : 'none')

        cluster_size = len(photo_list) / active_number_of_nodes # images per node
        distance_overlap = 10 # meters overlap of images


        #directories created:

        #exif
        #features
        #filterpoints
        #matches
        #mesh
        #mve
        #mvs
        #undistorted
       


  

        #extract metadata 

        camera_models = {}
        current_path = images_filepath

        opensfm_config = opensfm_interface.setup_opensfm_config(current_path)
        photo_list =  os.listdir(os.path.join(images_filepath, 'images'))
        image_path = os.path.join(current_path, 'images')
        distance_overlap = 10 



        start = timer()

        #exif extraction
	
        response = lib.sfm_extract_metadata_list_of_images(image_path, opensfm_config, current_path, photo_list)


        end = timer()
        exif_extraction_time = end - start

        # feature extraction

        start = timer()
        response = lib.sfm_detect_features(photo_list, current_path  ,opensfm_config)


        end = timer()
        detect_features_time = end - start

        #feature matching

        start = timer()

        lib.sfm_feature_matching(current_path, photo_list, photo_list, opensfm_config)

        end = timer()
        feature_matching_time = end - start

        start = timer()


        response = lib.sfm_create_tracks(current_path, photo_list,opensfm_config)


        end = timer()
        create_tracks_time = end - start


        start = timer()


        # need the exifs 

        lib.sfm_opensfm_reconstruction(current_path, opensfm_config)


        end = timer()
        sfm_opensfm_reconstruction_time = end - start

        start = timer()
        lib.sfm_undistort_image(current_path, opensfm_config)

        end = timer()
        sfm_undistort_image_time = end - start


        start = timer()
                    
        lib.sfm_export_visual_sfm(current_path, opensfm_config)


        end = timer()
        sfm_export_visualsfm_time = end - start

        start = timer()


	#export ply
	

        #lib.sfm_compute_depthmaps(current_path, opensfm_config)

	lib.export_ply_function(images_filepath, opensfm_config)

        end = timer()
        sfm_export_ply_time = end - start




        start = timer()

        max_concurrency = 4


        #need images

        # delete from makescene
        lib.mve_makescene_function(current_path, max_concurrency)



        end = timer()
        mve_makescene_function_time = end - start

        start = timer()

        lib.mve_dense_reconstruction(current_path ,max_concurrency)

        end = timer()
        mve_dense_reconstruction_time = end - start

        start = timer()

        lib.mve_scene2pset_function(current_path, max_concurrency)

        end = timer()
        mve_mve_scene2pset_time = end - start

        start = timer()

        lib.mve_cleanmesh_function(current_path, max_concurrency)

        end = timer()
        mve_mve_cleanmesh_time = end - start


        start = timer()


        lib.odm_filterpoints_function(current_path, max_concurrency)


        end = timer()
        odm_filterpoint_time = end - start
        
        start = timer()

	from opendm import io
	images_database_file = io.join_paths(current_path, 'images.json')
	
        if not io.file_exists(images_database_file):
            files = photo_list
	    images_dir = io.join_paths(file_path,'images')
            if files:
                # create ODMPhoto list
                path_files = [io.join_paths(images_dir, f) for f in files]

                photos = []
		dataset_list = io.join_paths(file_path,'img_list')
                with open(dataset_list, 'w') as dataset_list:
                    log.ODM_INFO("Loading %s images" % len(path_files))
                    for f in path_files:
                        photos += [types.ODM_Photo(f)]
                        dataset_list.write(photos[-1].filename + '\n')

                # Save image database for faster restart
                save_images_database(photos, images_database_file)
            else:
                log.ODM_ERROR('Not enough supported images in %s' % images_dir)
                exit(1)
        else:
            # We have an images database, just load it
            photos = load_images_database(images_database_file)

        log.ODM_INFO('Found %s usable images' % len(photos))

        # Create reconstruction object
        reconstruction = types.ODM_Reconstruction(photos) 


        lib.odm_mesh_function(opensfm_config,current_path, max_concurrency, reconstruction)

        end = timer()
        odm_mesh_time = end - start


        start = timer()


        lib.odm_texturing_function(current_path)

        end = timer()
        odm_texturing_time = end - start

	
	import orthophoto
	start = timer()

	
	from opendm import system 
	system.mkdir_p(os.path.join(current_path,'opensfm'))
	opensfm_interface.invent_reference_lla(images_filepath,  photo_list,os.path.join(current_path, 'opensfm'))
	system.mkdir_p(os.path.join(current_path,'odm_georeferencing'))
	odm_georeferencing = io.join_paths(current_path, 'odm_georeferencing')
	odm_georeferencing_coords = io.join_paths(odm_georeferencing, 'coords.txt')

	reconstruction.georeference_with_gps(photos, odm_georeferencing_coords, True)
	odm_geo_proj = io.join_paths(odm_georeferencing, 'proj.txt')
	reconstruction.save_proj_srs(odm_geo_proj) 
	from opendm.osfm import OSFMContext 
	octx = OSFMContext(os.path.join(current_path, 'opensfm'))
	print('----------Export geocroods--------')
	octx.run('export_geocoords --transformation --proj \'%s\'' % reconstruction.georef.proj4())
	print('----------Export Geocoords Ppppp--------')
	
	
	import config
	opendm_config = config.config()
	tree = {}
	import odm_georeferencing
	odm_georeferencing.process(opendm_config, tree, reconstruction, current_path)

	orthophoto.process(opendm_config, current_path, 4, reconstruction)
 
	
        

	orthophoto_path = '/home/vm1/Desktop/ODM/grpc_stages/node1/orthophoto/odm_orthophoto.original.tif'
	from opendm import orthophoto
	orthophoto.generate_png(orthophoto_path)


	from PIL import Image 

	o_image = '/home/vm1/Desktop/ODM/grpc_stages/node1/orthophoto/odm_orthophoto.original.png'
	r_image = '/home/vm1/Desktop/ODM/grpc_stages/node1/orthophoto/odm_orthophoto_resize.png'
	
	img = Image.open(o_image)

	new_img = img.resize((1200,1200),Image.ANTIALIAS)
	new_img.save(r_image)
		
	end = timer()
	odm_orthophoto_time = end - start

	
	start_yolo = timer()
	import subprocess
	process = subprocess.Popen(['./darknet/darknet', 'detector', 'test', './darknet/obj.data','./darknet/yolov4-newcustom.cfg','./darknet/yolov4-newcustom1_last.weights', r_image, '-thresh', '0.5'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	print(stderr)
	print(stdout)
	process.wait()

	yolo_time = timer()-start_yolo
	


        # for each in ref_image:
        #     opensfm_interface.detect(current_path+'features', current_path+each,each ,opensfm_config)


        # #opensfm_interface.detect(current_path+'features', current_path+'DJI_0019.JPG','DJI_0019.JPG' ,opensfm_config)




        # #feature matching

       

        # pairs_matches, preport = new_matching.match_images(current_path, ref_image, cand_images, opensfm_config)
        # new_matching.save_matches(current_path, ref_image, pairs_matches)
        # print('matching')
        



        # #create tracks first

        # features, colors = tracking.load_features(current_path+'features', ref_image, opensfm_config)
        # matches = tracking.load_matches(current_path, ref_image)
        # graph = tracking.create_tracks_graph(features, colors, matches,
        #                                      opensfm_config)

        # opensfm_interface.save_tracks_graph(graph, current_path)



        # #reconstruction


        # # load tracks graph

        # graph = opensfm_interface.load_tracks_graph(current_path)
        # report, reconstructions = reconstruction.incremental_reconstruction(current_path, graph, opensfm_config)

        # opensfm_interface.save_reconstruction(current_path,reconstructions)
        # #opensfm_interface.save_report(io.json_dumps(report), 'reconstruction.json')
      
        # outputs = {}
        # photos = []
        # from opendm import photo
        # from opendm import types
        
        # for each in ref_image:
        #     photos += [types.ODM_Photo(current_path+each)]
          
        
        # # get match image sizes
        # outputs['undist_image_max_size'] = max(
        #     gsd.image_max_size(photos, 5.0, current_path+'reconstruction.json'),
        #     0.1
        # )        
        # print(outputs)

        # #undistort image dataset: 

        # opensfm_interface.opensfm_undistort(current_path, opensfm_config)


        # #export visualsfm

        # opensfm_interface.open_export_visualsfm(current_path, opensfm_config)

        # #compute depthmaps 

        # opensfm_interface.open_compute_depthmaps(current_path, opensfm_config)

      
        # #mve stage 1 makescene

        # #input compute depthmaps file
        
        # mve_file_path = '/home/j/ODM-master/grpc_stages/node1/mve'
        # nvm_file = '/home/j/ODM-master/grpc_stages/node1/undistorted/reconstruction.nvm'
        # mve_interface.mve_makescene(nvm_file, mve_file_path, 2)


        # #mve stage 2 dense reconstruction

        # mve_interface.mve_dense_recon(outputs['undist_image_max_size'], mve_file_path, 2)

        # #mve stage 3 scene2pset_path
        # mve_model = io.join_paths(mve_file_path, 'mve_dense_point_cloud.ply')
        # mve_interface.mve_scene2pset(mve_file_path, mve_model,outputs['undist_image_max_size'],2)

        # #mve stage 4 clean_mesh
        # mve_interface.mve_cleanmesh(0.6, mve_model, 2)



        # # filterpoint cloud
        # odm_filterpoints = '/home/j/ODM-master/grpc_stages/node1/filterpoints'
        # filterpoint_cloud = io.join_paths(odm_filterpoints, "point_cloud.ply")

        # filterpoint_interface.filter_points(odm_filterpoints, mve_model, filterpoint_cloud,2)

        #meshing stage
        #odm_mesh_folder= '/home/j/ODM-master/grpc_stages/node1/mesh'
        #odm_mesh_ply = io.join_paths(odm_mesh_folder, "odm_mesh.ply")
        #mesh_interface.mesh_3d(odm_mesh_folder, odm_mesh_ply, filterpoint_cloud, 2)

        # #texturing stage

        #mvs_folder= '/home/j/ODM-master/grpc_stages/node1/mvs'
        #mvs_texturing.mvs_texturing(odm_mesh_ply, mvs_folder, nvm_file)       
        print('finished')
  



        
        end_timer = timer()
        total_time = end_timer - start_time


        print('########################')

        

        print('End Results: ')
        #print('Upload Image Total Time: ' + str(upload_image_time))
        print('Exif Extraction Total Time: ' + str(exif_extraction_time))
        print('Detect Features Total Time: ' + str(detect_features_time))
        print('Feature Matching Total Time: ' + str(feature_matching_time))

        print('Create Tracks Total Time: ' + str(create_tracks_time))
        print('OpenSfm Reconstruction Total Time: ' + str(sfm_opensfm_reconstruction_time))
        print('OpenSfm Undistort Image Total Time: ' + str(sfm_undistort_image_time))
        print('OpenSfm Export Visual Sfm Total Time: ' + str(sfm_export_visualsfm_time))
        print('OpenSfm Export Ply Sfm Total Time: ' + str(sfm_export_ply_time))
        print('Mve Makescene Sfm Total Time: ' + str(mve_makescene_function_time))
        print('Mve Dense Reconstruction Sfm Total Time: ' + str(mve_dense_reconstruction_time))
        print('Mve Scene 2 Pset Sfm Total Time: ' + str(mve_mve_scene2pset_time))
        print('Mve Cleanmesh Sfm Total Time: ' + str(mve_mve_cleanmesh_time))
        print('ODM Filterpoints Total Time: ' + str(odm_filterpoint_time))
        print('ODM Mesh Total Time: ' + str(odm_mesh_time))
        print('ODM Texturing Total Time: ' + str(odm_texturing_time))
        print('odm_orthophoto:' + ' ' + str(odm_orthophoto_time))
	print('yolo time: ' + str(yolo_time))
        
        print('Total Time: ' + str(total_time))

        timer_map = {}
        nodeids = str(nodeid)
        
        #timer_map['upload_image_time-'+nodeids] = upload_image_time
        timer_map['exif_extraction-'+nodeids] = exif_extraction_time
        timer_map['detect_features'+nodeids] = detect_features_time
        timer_map['feature_matching'+nodeids] = feature_matching_time
        

        timer_map['sfm_create_tracks_time-'+nodeids] = create_tracks_time
        timer_map['sfm_open_reconstruction-'+nodeids] = sfm_opensfm_reconstruction_time
        timer_map['sfm_undistort-'+nodeids] = sfm_undistort_image_time
        timer_map['sfm_export_visualsfm-'+nodeids] = sfm_export_visualsfm_time
        timer_map['sfm_compute_depthmap-'+nodeids] = sfm_export_ply_time
        timer_map['mve_makescence_time-'+nodeids] = mve_makescene_function_time
        timer_map['mve_dense_recon_time-'+nodeids] = mve_dense_reconstruction_time
        timer_map['mve_scence2pset_time-'+nodeids] = mve_mve_scene2pset_time
        timer_map['mve_cleanmesh_time-'+nodeids] =  mve_mve_cleanmesh_time
        timer_map['odm_filerpoints-'+nodeids] =  odm_filterpoint_time
        timer_map['odm_mesh-'+nodeids] =  odm_mesh_time
        timer_map['odm_texturing-'+nodeids] =  odm_texturing_time


        timer_map['total_time-'+nodeids] =  total_time


        #write time into json file timer
        write_json(timer_map, os.path.join(file_path,str(nodeid)+'-compute_times.json'))

        print('#######################')
        


        #execute a task on the server
    except Exception as e:
        print(e.message)
        print(traceback.print_exc())


    except KeyboardInterrupt:
        print('keyboard interrupt')
        sys.exit(0)







































