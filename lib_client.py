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

from opendm import log
from opendm import io 
from opendm import types

selfnodeid = 1

def do_task(job_queue, m_results={}):


    while True:
        
        try:
            task = job_queue.get() # returns a map 
            #print("task: " + str(task))
            if task['clientid'] == task['nodeid']:
                #print('equals self node id')

                response = False
                if task['title'] == 'upload_image':

                    #check if there is a is a submodel folder
                    #print('no need to upload for self')
		    pass



                
                if task['title'] == 'extract_exif':

                    #image path, opensfm_config, node_file_path
                  
                    #print('extract exif in self')

                    # file_path
                    #print(task['node_file_path'])

                    image_path = os.path.join(task['node_file_path'], 'images')

		    start = timer()
                    response = lib.sfm_extract_metadata_list_of_images(image_path, task['opensfm_config'], task['node_file_path'], task['imagelist'])
		    end_timer = timer()-start
		    write_json_append({'self_exif':end_timer}, os.path.join(file_path,'selfexif-compute_times.json'))
		
                    #print('response in self')
                    #print(response)

                elif task['title'] == 'detect_features':

                    #print('detect features in task queue in self')
                    # needs images 

                    # current path, ref images, opensfm_config
                    current_path = task['node_file_path']

                    ref_image = os.listdir(current_path + '/images')
		    start = timer()
                    response = lib.sfm_detect_features(ref_image, current_path  ,task['opensfm_config'], task['imagelist'])
		    end_timer = timer()-start
		    write_json_append({'self_detect':end_timer}, os.path.join(file_path,'selfdetect-compute_times.json'))
		
                    
                    
                elif task['title'] == 'feature_matching':
                    #print('feature matching')

                    # needs images
                    # image path
                    # list of images 
                    # candidate images
                    # opensfm config

		    start = timer()
                    response = lib.sfm_feature_matching(task['node_file_path'], task['ref_image'], task['cand_images'], task['opensfm_config'])
		    end_timer = timer()-start
		    #write_json_append({'self_feature_match':end_timer}, os.path.join(file_path,'selffeaturepairs-compute_times.json'))
		
                    
                elif task['title'] == 'feature_matching_pairs':

		    #print('in self pair matches')

 		    pairs = task['pairs']

                    #send the pair of feature files

                    #feature list

                    #process pairs 
                    #unique_id = []
                    #for each in pairs:
                    #    if each[0] not in unique_id:
                    #        unique_id.append(each[0])
                    #    if each[1] not in unique_id:
                    #        unique_id.append(each[1])

                   


                    
		    #print('self feature matching')
		    start = timer()
                    matches = lib.sfm_feature_matching_pairs(task['filepath'],pairs,task['opensfm_config'])
		    end_timer = timer()-start
		    write_json_append({'self_feature_match':end_timer}, os.path.join(file_path,'selffeaturepairs-compute_times.json'))


                        # save pair matches in a file 
                        # send it to client

                    #opensfm_interface.save_matches(task['filepath'], filename, pairs_matches)

                    #filename =  pair[0]+'-'+pair[1] 
                    #matches = opensfm_interface.load_matches(task['filepath'],filename)
                    #print('load matches')
                    #print(matches)
		    #print("self ecompute: "+str(len(matches)))

		    #for each in matches:
		    #	print(each)
		    #print('')

		    m_results.update(matches)
		    
		    """
                    task['lock'].acquire()
                    try:
			print('lock acquired')
                        tup = (pair[0], pair[1])
                        task['results'].update(pairs_matches)
			results
			print('updated matches')
                    except Exception as e:
                        print(e.message)
                        pass
		    except:
			print('error in lock in matching in self')

		
                    
                    task['lock'].release()
		    """
		    #print('lock release')

                elif task['title'] == 'sfm_create_tracks':
                    # needs images
                    # current path




                    #submodel version

                    #print(task['cluster'])

                    sending_match_pairs = {}
                    #print(task['results'].keys())
                    #print('here')
                    for key, value in task['results'].items():
                        #print(key)
                        if key[0] in task['cluster'] and key[1] in task['cluster']:
                            #print('key:' + str(key))
                            sending_match_pairs[key] = value

                    #print(len(sending_match_pairs))


                    #print(sending_match_pairs)
                    

                    #print(os.path.join(task['filepath'], task['submodel_path']))

                    matches_filepath =os.path.join(task['filepath'], task['submodel_path'])

                    # maybe save the results in a results file and send it 
                    submodel_path = task['submodel_path']

                    #print(submodel_path)

                    #opensfm_interface.save_matches(matches_filepath, submodel_matches, sending_match_pairs)
                    
                    #matches = opensfm_interface.load_matches(matches_filepath, submodel_matches)

                    #print(matches)

                    response = lib.sfm_create_tracks(submodel_path, task['cluster'],task['opensfm_config'], sending_match_pairs, True, task['filepath'])


                    start = timer()


                    # # need the exifs 

                    lib.sfm_opensfm_reconstruction(submodel_path, opensfm_config, True,task['filepath'] )


                    end = timer()
                    sfm_opensfm_reconstruction_time = end - start

                    start = timer()

                    lib.sfm_undistort_image(submodel_path, opensfm_config, True, task['filepath'])

                    end = timer()
                    sfm_undistort_image_time = end - start


                    start = timer()
                    
                    lib.sfm_export_visual_sfm(submodel_path, opensfm_config ,True, task['filepath'])


                    end = timer()
                    sfm_export_visualsfm_time = end - start


                    start = timer()


                    #test load
                    udata   = opensfm_interface.UndistortedDataSet(task['filepath'], task['opensfm_config'], 'undistorted')


                    for image_name in task['cluster']:
                        try:
                            #print(image_name)
                            ret = udata.load_raw_depthmap(image_name)
                        except Exception as e:
                            print(e.message)
                            print('image name bad ' + str(image_name))
                  




                    


                    
                    lib.sfm_compute_depthmaps(submodel_path, opensfm_config,  True, task['filepath'])


                    end = timer()
                    sfm_compute_depthmaps_time = end - start


                    # split merge here no problem


                    start = timer()

                    max_concurrency = 2


                    #need images

                    # delete from makescene
                    #lib.mve_makescene_function(submodel_path, max_concurrency, True, task['file_path'])



                    end = timer()
                    mve_makescene_function_time = end - start

                    start = timer()

                    #lib.mve_dense_reconstruction(submodel_path ,max_concurrency, True, task['file_path'])

                    end = timer()
                    mve_dense_reconstruction_time = end - start

                    start = timer()

                    #lib.mve_scene2pset_function(submodel_path, max_concurrency)

                    end = timer()
                    mve_mve_scene2pset_time = end - start

                    start = timer()

                    # lib.mve_cleanmesh_function(submodel_path, max_concurrency)

                    end = timer()
                    mve_mve_cleanmesh_time = end - start


                    start = timer()


                    # lib.odm_filterpoints_function(submodel_path, max_concurrency)


                    end = timer()
                    odm_filterpoint_time = end - start
                    
                    start = timer()


                    # lib.odm_mesh_function(submodel_path, max_concurrency)

                    end = timer()
                    odm_mesh_time = end - start


                    print('OpenSfm Reconstruction Total Time: ' + str(sfm_opensfm_reconstruction_time))
                    print('OpenSfm Undistort Image Total Time: ' + str(sfm_undistort_image_time))
                    print('OpenSfm Export Visual Sfm Total Time: ' + str(sfm_export_visualsfm_time))
                    print('OpenSfm Compute DepthMaps Sfm Total Time: ' + str(sfm_compute_depthmaps_time))
                    print('Mve Makescene Sfm Total Time: ' + str(mve_makescene_function_time))
                    print('Mve Dense Reconstruction Sfm Total Time: ' + str(mve_dense_reconstruction_time))
                    print('Mve Scene 2 Pset Sfm Total Time: ' + str(mve_mve_scene2pset_time))
                    print('Mve Cleanmesh Sfm Total Time: ' + str(mve_mve_cleanmesh_time))
                    print('ODM Filterpoints Total Time: ' + str(odm_filterpoint_time))
                    print('ODM Mesh Total Time: ' + str(odm_mesh_time))



                    
                elif task['title'] == 'opensfm_reconstruction':

                    # needs create tracks . csv
                    # return reconstruction.json

                    response = lib.sfm_opensfm_reconstruction(task['node_file_path'], task['opensfm_config'])
                    
                elif task['title'] == 'sfm_undistort_image':

                    response = lib.sfm_undistort_image(task['node_file_path'], task['opensfm_config'])
                    
                    
                elif task['title'] == 'export_visual_sfm':
                    #nvm file
                   
                    response = lib.sfm_export_visual_sfm(task['node_file_path'],task['opensfm_config'])

                elif task['title'] == 'compute_depthmaps':
                   
                   response = lib.sfm_compute_depthmaps(task['node_file_path']. task['opensfm_config'])
                    
                elif task['title'] == 'dense_reconstruction':

                   response = lib.mve_dense_reconstruction(task['node_file_path'])
                    
                    
                elif task['title'] == 'makescene_function':
                   response = lib.mve_makescene_function(task['node_file_path'], task['max_concurreny'])
                    
                elif task['title'] == 'scene2pset':
                    response = lib.mve_scene2pset_function(task['node_file_path'], task['max_concurreny'])
                    
                    
                elif task['title'] == 'cleanmesh':
                   response = lib.mve_cleanmesh_function(task['node_file_path'], task['max_concurreny'])
                    
                elif task['title'] == 'filterpoints':
                   response = lib.odm_filterpoints_function(task['node_file_path'], task['max_concurreny'])
                    
                elif task['title'] == 'mesh':
                   response = lib.odm_mesh_function(task['node_file_path'], task['max_concurreny'])
                                        
                elif task['title'] == 'texturing':
                    response = lib.odm_texturing_function(task['node_file_path'])
                    
            else:

                if task['title'] == 'upload_image':
                    #print('upload')
        
                    response = task['client'].upload(task['filepath'], task['list'])
                    #print(response)
                elif task['title'] == 'extract_exif':
                    #print(str(task))
                    #print('extract exif ')
                    response = task['client'].sendTask('exif', task['nodeid'], '/exif')
                    #print(response)
                elif task['title'] == 'detect_features':

                    #print('detect features in task queue')
                    # needs images 
                    response = task['client'].sendTask('detect_features', task['nodeid'], '/features')
                elif task['title'] == 'feature_matching':
                    #print('feature matching')

                    # needs images
                    respone = task['client'].sendTask('feature_matching', task['nodeid'], '/matches')
                    
                elif task['title'] == 'sfm_create_tracks':
                    #needs images

                    #print(task['cluster'])

                    sending_match_pairs = {}
                    #print(task['results'].keys())
                    #print('here')
                    for key, value in task['results'].items():
                        #print(key)
                        if key[0] in task['cluster'] and key[1] in task['cluster']:
                            #print('key:' + str(key))
                            sending_match_pairs[key] = value

                    #print(len(sending_match_pairs))


                    #print(sending_match_pairs)
                    

                    #print(os.path.join(task['filepath'], task['submodel_path']))

                    matches_filepath =os.path.join(task['filepath'], task['submodel_path'])

                    # maybe save the results in a results file and send it 
                    submodel_matches = task['submodel_path']

                    #print(submodel_matches)

                    opensfm_interface.save_matches(matches_filepath, submodel_matches, sending_match_pairs)
                    
                    #matches = opensfm_interface.load_matches(matches_filepath, submodel_matches)

                    #print(matches)

                    

                    

                    #print(' upload matches ')
                    feature_matches_response = task['client'].upload(matches_filepath, [submodel_matches+'_matches.pkl.gz'], submodel_file='matches') 


                    #print('here after feature matches send')


                    # send features 
                    # send matches
                    feature_list = []
                    for image_name in task['cluster']:
                       feature_0 = 'features/' + image_name + '.features.npz'
                       feature_list.append(feature_0)
                    
                    #print(' send features ')
                    response = task['client'].upload(task['filepath'], feature_list, 'feature', task['submodel_path'] )




                    #send images
                    response = task['client'].upload(task['filepath'], task['cluster'], 'images', task['submodel_path'])

                    
                    #send exif
                    response = task['client'].upload(task['filepath'], task['cluster'], 'exif', task['submodel_path'])


                    #send cameras.json
                    response = task['client'].upload(task['filepath'], ['camera_models.json'], 'camera_models', task['submodel_path'] )




                    # 
                    respone = task['client'].sendTask('create_tracks', task['nodeid'], '/', submodel_path=task['submodel_path'], cluster_images = task['cluster'])
                    




                elif task['title'] == 'opensfm_reconstruction':

                    # needs create tracks . csv
                    # return reconstruction.json
                    respone = task['client'].sendTask('opensfm_reconstruction', task['nodeid'], '/')
                    
                elif task['title'] == 'sfm_undistort_image':
                    respone = task['client'].sendTask('undistort_image', task['nodeid'], '/undistorted')
                    
                elif task['title'] == 'export_visual_sfm':
                    #nvm file
                    respone = task['client'].sendTask('export_visual_sfm', task['nodeid'], '/undistorted')
                    
                elif task['title'] == 'compute_depthmaps':
                    respone = task['client'].sendTask('compute_depthmaps', task['nodeid'], '/depthmaps')
                    
                elif task['title'] == 'dense_reconstruction':
                    respone = task['client'].sendTask('dense_reconstrution', task['nodeid'], '/mve')
                    
                elif task['title'] == 'makescene_function':
                    respone = task['client'].sendTask('makescene_function', task['nodeid'], '/mve')
                    
                elif task['title'] == 'scene2pset':
                    respone = task['client'].sendTask('scene2pset', task['nodeid'], '/mve')
                    
                elif task['title'] == 'cleanmesh':
                    respone = task['client'].sendTask('cleanmesh', task['nodeid'], '/mve')
                    
                elif task['title'] == 'filterpoints':
                    respone = task['client'].sendTask('odm_filterpoints', task['nodeid'], '/filterpoints')
                    
                elif task['title'] == 'mesh':
                    respone = task['client'].sendTask('odm_mesh', task['nodeid'], '/mesh')
                    
                elif task['title'] == 'texturing':
                    respone = task['client'].sendTask('odm_texturing', task['nodeid'], '/mvs')
                    
                elif task['title'] == 'feature_matching_pairs':
                    # send over the pair feature files and exif files

                    pairs = task['pairs']

                    #send the pair of feature files

                    #feature list

                    #process pairs 
                    unique_id = []
                    for each in pairs:
                        if each[0] not in unique_id:
                            unique_id.append(each[0])
                        if each[1] not in unique_id:
                            unique_id.append(each[1])

                    feature_list = []
                    exif_list  = []

                    for each_id in unique_id:
                        feature_0 = 'features/' + each_id + '.features.npz'
                        feature_list.append(feature_0)
                        exif_0 = 'exif/' + each_id + '.exif'
                        exif_list.append(exif_0)
                    response = task['client'].upload(task['filepath'], feature_list)
                    response = task['client'].upload(task['filepath'], exif_list)

                    response = task['client'].sendTask('feature_matching_pairs', task['nodeid'], '/matches', pairs)

                    filename =  task['clientid']
                    matches = opensfm_interface.load_matches(task['filepath'],filename)
		    #print('node2')
		    #print(len(matches))
		    #for each in matches:
		    #	print(each)
		    #print('')
                    #print('load matches')
                    #print(matches)
		    #print('try lock')
 		    m_results.update(matches)
		    
		    """
                    task['lock'].acquire()
		   
                    try:
                        tup = (pair[0], pair[1])
                        task['results'].update(matches)
			
			print('lock acquired and reuslt done for send ')
                    except Exception as e:
                        print(e.message)
                        pass
                   
                    task['lock'].release()
		    print('lock release for send ')
		    """
                    
                        


                #print('done')

            job_queue.task_done()
        except Exception as e:
            print(e.message)
            print(traceback.print_exc())

            print()
            sys.exit(0)
        except KeyboardInterrupt:
            sys.exit(0)

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



        

if __name__ == '__main__':
    
    #lib.FileServer(8888, 1, 'node1').start(8888)

    start_time = timer()

    # multiple node process



    

    thread_lock = threading.Lock()

    try:

	match_results = {}
        job_queue = Queue()
        num_threads = 4
        for i in range(num_threads):
            worker = Thread(target=do_task, args=(job_queue,match_results))
            worker.setDaemon(True)
            worker.start()


        nodeid = 1
	#nodeid_list = [1,2,3,4]
        #nodeid_map = {2: '5001', 1: 'self', 3: '50052', 4: '50051'}
	nodeid_list = [1,2]
        nodeid_map = {2: '5001', 1: 'self'}
       

	node_client = {}
        #nodes_available = {2: True}
        max_concurrency = 4
	node_imagelist = {}
	node_imagelist[1] = []
	node_imagelist[2] = []
	node_imagelist[3] = []
	node_imagelist[4] = []

	
        for each_node in nodeid_map:
            if (each_node == nodeid):
                continue
	    #fe80::ba6c:4e2:b8cc:a62b]
            #client = lib.FileClient('localhost:' + nodeid_map[each_node], nodeid)
	    if (each_node == 2):
	    	client = lib.FileClient('10.10.10.3:' + nodeid_map[each_node], nodeid)
	    if (each_node == 3):
	    	client = lib.FileClient('10.10.10.4:' + nodeid_map[each_node], nodeid)
	    if (each_node == 4):
	    	client = lib.FileClient('10.10.10.5:' + nodeid_map[each_node], nodeid)
            node_client[each_node] = client

        images_filepath = '/home/vm1/Desktop/ODM/grpc_stages/node1'  #file path of current node images
        file_path = images_filepath + '/'
        opensfm_config = opensfm_interface.setup_opensfm_config(file_path)
        active_number_of_nodes = 2
        photos_name = collections.defaultdict(lambda : "None")
        photo_list =  os.listdir(os.path.join(images_filepath, 'images'))
        #print(photo_list)

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
       


        #parallel functions



        for name in photo_list:
            if os.path.isfile(name):
                photos_name[name] = 'not send'
        num_photos = len(photo_list)

        photos_per_node = num_photos / active_number_of_nodes 
        #print(photos_per_node)
        photos_rem = num_photos % active_number_of_nodes

        current_photo_pointer = 0
	end = photos_per_node

        start = timer()

        for eachnode in nodeid_list:
            if (photos_rem > 0):
                new_photos_for_node = photos_per_node + photos_rem
                photolist = photo_list[current_photo_pointer:new_photos_for_node]
                current_photo_pointer+=new_photos_for_node
                #print(str(eachnode) + " : " + str(photolist))
                if eachnode == nodeid:
                    job_map = {'title': 'upload_image',  'nodeid': nodeid, 'list': photolist, 'filepath': images_filepath+'/images', 'clientid': eachnode}
                    node_imagelist[eachnode].append(photolist)
                    job_queue.put(job_map)
                else:
                    job_map = {'title': 'upload_image', 'client': node_client[eachnode], 'nodeid': nodeid, 'list': photolist, 'filepath': images_filepath+'/images', 'clientid': eachnode}
                    node_imagelist[eachnode].append(photolist)
                    job_queue.put(job_map)
                photos_rem = 0
                
                #esponse = client.upload(, is_dir=True)

                # send to this node 
            else:
                end_pointer = current_photo_pointer+photos_per_node
                if end_pointer > num_photos:
                    end_pointer = num_photos
                photolist = photo_list[current_photo_pointer:end_pointer]
                current_photo_pointer+=photos_per_node
                #print(str(eachnode) + " : " +  str(photolist))
                if eachnode == nodeid:
                    job_map = {'title': 'upload_image', 'nodeid': nodeid,'list': photolist, 'filepath': images_filepath+'/images', 'clientid': eachnode}
                    node_imagelist[eachnode].append(photolist)
                    job_queue.put(job_map)
                    
                    #continue
                else:
                    job_map = {'title': 'upload_image', 'nodeid': nodeid,'client': node_client[eachnode], 'list': photolist, 'filepath': images_filepath+'/images', 'clientid': eachnode}
                    node_imagelist[eachnode].append(photolist)

                    job_queue.put(job_map)
           
               
                #send regular number of photos

        job_queue.join()
        

        end = timer()
        upload_image_time = end - start
        #print(upload_image_time)
	#sys.exit(1)
	

        #extract sift

        #print('here in extract exif')
        #print('here 2')
        #print(node_imagelist)
        

        start = timer()

        for each in nodeid_list:
            print('extract exif node')
            if each == nodeid:
                print('same here')
                job_task_extract_exif = {'title': 'extract_exif', 'nodeid': nodeid, 'clientid': each, "imagelist": node_imagelist[each][0] , 'node_file_path': images_filepath, 'opensfm_config': opensfm_config }
                print('after same here')
            else:
                job_task_extract_exif = {'title': 'extract_exif', 'client': node_client[each], 'nodeid': nodeid, 'clientid': each}
            job_queue.put(job_task_extract_exif)
        
        #print('here after extract')

        #call join to wait
        job_queue.join()

        end = timer()
        exif_extraction_time = end - start


	

        

        #print('here in dectect feature')

    
        # detect_features


        start = timer()

        #for each

		


	
        for each in nodeid_list:
            if each == nodeid:
                job_task_detect = {'title': 'detect_features',  'nodeid': nodeid, 'clientid': each, 'imagelist': node_imagelist[each][0], 'node_file_path': images_filepath, 'opensfm_config': opensfm_config}
            else:
                 job_task_detect = {'title': 'detect_features', 'client': node_client[each], 'nodeid': nodeid, 'clientid': each, 'imagelist': node_imagelist[each][0], 'node_file_path': images_filepath, 'opensfm_config': opensfm_config}
            job_queue.put(job_task_detect)

      
        job_queue.join()
	

        end = timer()
        detect_features_time = end - start
	#sys.exit(1)

        #print('matching features')


        # match features 

        # job_task_detect = {'title': 'feature_matching', 'client': node_client[2], 'nodeid': 1}
        # job_queue.put(job_task_detect)
        # job_task_detect = {'title': 'feature_matching', 'client': node_client[3], 'nodeid': 1}
        # job_queue.put(job_task_detect)

        #// feature matching 


        # for each image 

        # generate pairs 
        # loop through the task for the pairs 

        
       

        # match through the pairs
        # save the results
        # append to the file





        #job_queue.join()

        start = timer()
         

        #print('after queue join filepath')
  

        ref_images = os.listdir(file_path +'/images')
        #print(ref_images)
        cand_images = ref_images
        exifs = {im: opensfm_interface.load_exif(file_path,im) for im in ref_images}

        #print(exifs)
       

        #print(file_path)
        

        pairs, preport = new_pairs_selection.match_candidates_from_metadata( file_path, 
        ref_images, cand_images, exifs, opensfm_config)

        #print('here')
        #print(pairs)
	#print('len of pairs ' + str(pairs))

        results = {}
        #for each pair 
        #for each node

        #go through all the nodes


        # start value for the client number
	thread_list = list()
        node_client_num = 1
	

	current = 0
        end = len(pairs)/(len(nodeid_list))
	#print('first end ' + str(end))
	#print('before feature matching paris')
	#print(len(pairs))

        for number in range(len(nodeid_list)):
	    #print('current ' + str(current))
	    #print('end ' + str(end))
            n = pairs[current:end]
	    #print("Number in the range " + str(number) + " len " + str(len(n)))
            
            if nodeid_list[number] == nodeid:
                job_task = {'title': 'feature_matching_pairs', 'nodeid': 1,  'filepath': file_path, 'results': results, 'lock': thread_lock, 'clientid': nodeid, 'opensfm_config': opensfm_config, 'pairs': pairs[current:end] }
		#print('')
		#print(n)
		#print(len(n))
		#print('here in task for node 1')
            else:
                job_task = {'title': 'feature_matching_pairs', 'client': node_client[nodeid_list[number]], 'nodeid': 1,  'filepath': file_path, 'results': results, 'lock': thread_lock, 'clientid': nodeid_list[number], 'pairs':pairs[current:end]}
		#print('here in node 2')
		#print(n)
		#print(len(n))
		#print('')
                node_client_num = number + 1  
            job_queue.put(job_task)
            current = end
            if number+1 != len(nodeid_list)-1:
                end =  (len(pairs)/(len(nodeid_list))) * (2+number) 
                print(end)
            else:
                end = len(pairs)


	#sys.exit(1)


        job_queue.join()

	#print('end of match results from feature')

	#print(len(match_results))

	#for each in match_results:
	#	print(each)

	#sys.exit(1)
	

	#for th in thread_list:
        	#t.join()
        #print('matching finished')
        #exit(1)
        #print(match_results)

        end = timer()
        feature_matching_time = end - start
            



        #file_path
        #opensfm_config
        #exifs
        #need to send the features




        #match image with paris 
	

        #group images by distance
	start_cluster = timer()



        #create image list for this node
        submodel_creation._create_image_list(photo_list, images_filepath)

        


        #cluster images
        submodel_creation._cluster_images(cluster_size, images_filepath)



        #add overlapping neighbors with distances

        submodel_creation._add_cluster_neighbors(images_filepath, distance_overlap)




        clusters = submodel_creation.load_clusters_with_neighbors(images_filepath)

	#for i , each in enumerate(clusters):
		#print('cluster num ' + str(i) + ' ' + str(len(each)))

	



        clustering_time = timer() -start_cluster

        #print('clusters here')
        #print(clusters)
        #exit(1)




        node_cluster_list = {}
        node_id_cluster_id = {}

        # create tracks 
        # have to be single computation

        # tracks graph // add_node in union find 
        # get all the tracks then merge them

        #print('create tracks')

        start = timer()



        # can use distribute merge approach here 
        # loop through each cluster, 
        # pass a cluster to each node
        
        node_num = 0
        for i , each in enumerate(clusters):
            tup = (i, nodeid_list[node_num])
            node_cluster_list[tup] = each
            node_id_cluster_id[i] = nodeid_list[node_num]
            node_num = (node_num+1) % len(nodeid_list)

        #print(node_cluster_list)
        #print(node_id_cluster_id)

        


        # features 
        # matches 

        # make a submodel folder for each one

        # for each node cluster list
        # create tracks 
        # send results 

        start = timer()


      

	results = match_results

        current_node_submodel = None
        current_node_submodel_key = None
        all_submodel_path = []
        for key, value in node_cluster_list.items():
            submodel_num = 'submodel_' + str(key[0])
            submodel_path = os.path.join(file_path, 'submodel_' + str(key[0]))
            all_submodel_path.append(submodel_path)
            if not os.path.isdir(submodel_path):
                os.mkdir(submodel_path)

            if key[1] == nodeid:
               #pass
                
                current_node_submodel = key[0]
                current_node_submodel_key = key
                #print('current node num: ' + str(current_node_submodel))
                #job_task = {'title': 'sfm_create_tracks', 'nodeid': nodeid, 'filepath': file_path, 'results': results,  'clientid': key[1], 'opensfm_config': opensfm_config, 'cluster': value, 'submodel_path': submodel_path}
                #job_queue.put(job_task)
            else:
                #pass
                #print('key: ' + str(key) + ' submodel path: ' + str(submodel_path))
                job_task = {'title': 'sfm_create_tracks', 'client': node_client[key[1]], 'nodeid': nodeid,  'filepath': file_path, 'results': results,  'clientid': key[1], 'cluster': value, 'submodel_path': submodel_num}  
                job_queue.put(job_task)
	#job_queue.join()
	#sys.exit(1)

	
        start = timer()
	start_cluster_compute_time = timer()

        sending_match_pairs = {}
        #print(results.keys())
        
        #print(node_cluster_list[current_node_submodel_key])
        
        for key, value in results.items():
            #print(key)
            if key[0] in node_cluster_list[current_node_submodel_key] and key[1] in node_cluster_list[current_node_submodel_key]:
                #print('key:' + str(key))
                sending_match_pairs[key] = value

	start = timer()
        submodel_path = os.path.join(file_path, 'submodel_' + str(0)) #current_node_submodel

        #print(' before sfm create tracks')


        response = lib.sfm_create_tracks(submodel_path, node_cluster_list[current_node_submodel_key],opensfm_config, sending_match_pairs, True, file_path)


        end = timer()
        create_tracks_time = end - start


        start = timer()


        # need the exifs 

        lib.sfm_opensfm_reconstruction(submodel_path, opensfm_config, True, file_path)


        end = timer()
        sfm_opensfm_reconstruction_time = end - start

        start = timer()

        lib.sfm_undistort_image(submodel_path, opensfm_config, True, file_path)

        end = timer()
        sfm_undistort_image_time = end - start


        start = timer()
                    
        lib.sfm_export_visual_sfm(submodel_path, opensfm_config ,True, file_path)


        end = timer()
        sfm_export_visualsfm_time = end - start

        start = timer()

        #.sfm_compute_depthmaps(submodel_path, opensfm_config,  True, file_path)

        
        end = timer()
        sfm_compute_depthmaps_time = end - start

        start = timer()

        max_concurrency = 4


        #need images

        # delete from makescene
        lib.mve_makescene_function(submodel_path, max_concurrency, True, file_path)



        end = timer()
        mve_makescene_function_time = end - start

        start = timer()

        lib.mve_dense_reconstruction(submodel_path ,max_concurrency, True, file_path)

        end = timer()
        mve_dense_reconstruction_time = end - start

        start = timer()

        lib.mve_scene2pset_function(submodel_path, max_concurrency,  True, file_path)

        end = timer()
        mve_mve_scene2pset_time = end - start

        start = timer()

        lib.mve_cleanmesh_function(submodel_path, max_concurrency)

        end = timer()
        mve_mve_cleanmesh_time = end - start


        start = timer()


        lib.odm_filterpoints_function(submodel_path, max_concurrency)


        end = timer()
        odm_filterpoint_time = end - start
        
        start = timer()

	from opendm import io
	images_database_file = io.join_paths(submodel_path, 'images.json')
	photo_list = node_cluster_list[current_node_submodel_key]
	
	photos = []
        if not io.file_exists(images_database_file):
            files = photo_list
	    images_dir = io.join_paths(file_path,'images')
            if len(files)>0:
                # create ODMPhoto list
                path_files = [io.join_paths(images_dir, f) for f in files]

                
		dataset_list = io.join_paths(file_path,'img_list')
                with open(dataset_list, 'w') as dataset_list:
                    log.ODM_INFO("Loading %s images" % len(path_files))
                    for f in path_files:
                        photos += [types.ODM_Photo(f)]
                        dataset_list.write(photos[-1].filename + '\n')

                # Save image database for faster restart
                lib.save_images_database(photos, images_database_file)
            else:
                log.ODM_ERROR('Not enough supported images in %s' % images_dir)
                exit(1)
        else:
            # We have an images database, just load it
            photos = lib.load_images_database(images_database_file)

        log.ODM_INFO('Found %s usable images' % len(photos))
	from opendm import system 
	system.mkdir_p(os.path.join(submodel_path, 'opensfm'))
        # Create reconstruction object
        reconstruction = types.ODM_Reconstruction(photos)
	opensfm_interface.invent_reference_lla(images_filepath,  photo_list,os.path.join(submodel_path, 'opensfm'))
	
	system.mkdir_p(os.path.join(submodel_path,'odm_georeferencing'))
	odm_georeferencing = io.join_paths(submodel_path, 'odm_georeferencing')
	odm_georeferencing_coords = io.join_paths(odm_georeferencing, 'coords.txt')
	
	reconstruction.georeference_with_gps(photos, odm_georeferencing_coords, True)
	odm_geo_proj = io.join_paths(odm_georeferencing, 'proj.txt')
	reconstruction.save_proj_srs(odm_geo_proj) 
	from opendm.osfm import OSFMContext 
	octx = OSFMContext(os.path.join(submodel_path, 'opensfm'))
	print('----------Export geocroods--------')
	octx.run('export_geocoords --transformation --proj \'%s\'' % reconstruction.georef.proj4())
	print('----------Export Geocoords Ppppp--------')


	
	



        lib.odm_mesh_function(opensfm_config,submodel_path, max_concurrency, reconstruction)

        #lib.odm_mesh_function(submodel_path, max_concurrency)

        end = timer()
        odm_mesh_time = end - start

        start = timer()


        lib.odm_texturing_function(submodel_path)

        end = timer()
        odm_texturing_time = end - start

	import orthophoto
	start = timer()
	# georeference
	# georeferenceing 
	import odm_georeferencing
	
	
	import config
	opendm_config = config.config()
	tree = {}
	odm_georeferencing.process(opendm_config, tree, reconstruction, submodel_path)

	
	orthophoto.process(opendm_config, submodel_path, 4, reconstruction)

	end = timer()
        odm_orthophoto_time = end - start
	print('odm_orthophoto time: ' + ' ' + str(odm_orthophoto_time))


        print('self processing id done')

	#self node processing time
	end_cluster = timer()
	total_cluster_compute =  end_cluster-start_cluster_compute_time 


        job_queue.join()

	start = timer()

        #take all the submodel mesh_path
        #merge them the orthopthotos and convert to png
	from opendm import orthophoto
	orthophoto_list = []
	rename_list = []

	for key, value in node_cluster_list.items():
            submodel_num = 'submodel_' + str(key[0])
            submodel_path = os.path.join(file_path, 'submodel_' + str(key[0]))
	    if key == current_node_submodel_key:
		filename1 = os.path.join(submodel_path, 'orthophoto' ,'odm_orthophoto.original.tif')
		orthophoto_list.append(os.path.join(submodel_path, 'orthophoto' ,'odm_orthophoto.original.tif'))
		orthophoto.generate_png(filename1)

		filename2 = os.path.join(submodel_path, 'orthophoto', 'odm_orthophoto.original.png')
		filename3 = os.path.join(submodel_path, 'orthophoto' ,'ortho'+str(submodel_num) +'.png')
		os.rename(filename2, filename3)
		rename_list.append(filename3)
		
	    else:
		filename1 = os.path.join(submodel_path, 'odm_orthophoto.original.tif')
            	orthophoto_list.append(os.path.join(submodel_path, 'odm_orthophoto.original.tif'))
		orthophoto.generate_png(filename1)
		filename2 = os.path.join(submodel_path, 'odm_orthophoto.original.png')
		filename3 = os.path.join(submodel_path, 'ortho'+str(submodel_num ) +'.png')
		os.rename(filename2, filename3)
		rename_list.append(filename3)
		
		
	#resize each image

	from PIL import Image 
	r_list = []
	for i in range(len(rename_list)):
		img = Image.open(rename_list[i])

		new_img = img.resize((1200,1200),Image.ANTIALIAS)
		new_img.save('rortho'+str(i)+'.png')
		r_list.append('rortho'+str(i)+'.png')
		
		
	
	
	#stitch them
	import pano
	pano.run(r_list)

	
	



    


        end = timer()
        stitching_time = end - start
	print(stitching_time)
	#image is save in same directory as finalimage.jpg

	# use yolo here 
	#./darknet detector test obj.data yolov4-newcustom.cfg yolov4-newcustom1_last.weights sofwinres.png '
	
	start_yolo = timer()
	import subprocess
	process = subprocess.Popen(['./darknet/darknet', 'detector', 'test', './darknet/obj.data','./darknet/yolov4-newcustom.cfg','./darknet/yolov4-newcustom1_last.weights', 'cropfinalimage.png', '-thresh', '0.5'], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	stdout, stderr = process.communicate()
	print(stderr)
	print(stdout)
	process.wait()

	yolo_time = timer()-start_yolo


	

        # nx compose (two graphs)
        print('finished')

	
  



        
        end_timer = timer()
        total_time =  end_timer - start_time


        print('########################')

        

        print('End Results: ')

        print('Upload Image Total Time: ' + str(upload_image_time))
        print('Exif Extraction Total Time: ' + str(exif_extraction_time))
        print('Detect Features Total Time: ' + str(detect_features_time))
        print('Feature Matching Total Time: ' + str(feature_matching_time))
	print('Clustering  Total Time: ' + str(clustering_time))

        print('Create Tracks Total Time: ' + str(create_tracks_time))
        print('OpenSfm Reconstruction Total Time: ' + str(sfm_opensfm_reconstruction_time))
        print('OpenSfm Undistort Image Total Time: ' + str(sfm_undistort_image_time))
        print('OpenSfm Export Visual Sfm Total Time: ' + str(sfm_export_visualsfm_time))
        print('OpenSfm Compute DepthMaps Sfm Total Time: ' + str(sfm_compute_depthmaps_time))
        print('Mve Makescene Sfm Total Time: ' + str(mve_makescene_function_time))
        print('Mve Dense Reconstruction Sfm Total Time: ' + str(mve_dense_reconstruction_time))
        print('Mve Scene 2 Pset Sfm Total Time: ' + str(mve_mve_scene2pset_time))
        print('Mve Cleanmesh Sfm Total Time: ' + str(mve_mve_cleanmesh_time))
	
        print('ODM Filterpoints Total Time: ' + str(odm_filterpoint_time))
        print('ODM Mesh Total Time: ' + str(odm_mesh_time))
        print('ODM Texturing Total Time: ' + str(odm_texturing_time))
	print('odm_orthophoto time: ' + ' ' + str(odm_orthophoto_time))
	print('Current Cluster Compute Time: ' + str(total_cluster_compute))
	print('Stitching Time: ' + str(stitching_time))
	print('Yolo Time: ' + str(yolo_time))
        
        
        print('Total Time: ' + str(total_time))

        timer_map = {}
        nodeids = str(nodeid)
        
        timer_map['upload_image_time-'+nodeids] = upload_image_time
        timer_map['exif_extraction-'+nodeids] = exif_extraction_time
        timer_map['detect_features'+nodeids] = detect_features_time
        timer_map['feature_matching'+nodeids] = feature_matching_time
        

        timer_map['sfm_create_tracks_time-'+nodeids] = create_tracks_time
        timer_map['sfm_open_reconstruction-'+nodeids] = sfm_opensfm_reconstruction_time
        timer_map['sfm_undistort-'+nodeids] = sfm_undistort_image_time
        timer_map['sfm_export_visualsfm-'+nodeids] = sfm_export_visualsfm_time
        timer_map['sfm_compute_depthmap-'+nodeids] = sfm_compute_depthmaps_time
        timer_map['mve_makescence_time-'+nodeids] = mve_makescene_function_time
        timer_map['mve_dense_recon_time-'+nodeids] = mve_dense_reconstruction_time
        timer_map['mve_scence2pset_time-'+nodeids] = mve_mve_scene2pset_time
        timer_map['mve_cleanmesh_time-'+nodeids] =  mve_mve_cleanmesh_time
        timer_map['odm_filerpoints-'+nodeids] =  odm_filterpoint_time
        timer_map['odm_mesh-'+nodeids] =  odm_mesh_time
        timer_map['odm_texturing-'+nodeids] =  odm_texturing_time


        timer_map['total_time-'+nodeids] =  total_time


        #write time into json file timer
        write_json_append(timer_map, os.path.join(file_path,str(nodeid)+'-compute_times.json'))

        print('#######################')
	
        


        #execute a task on the server
    except Exception as e:
        print(e.message)
        print(traceback.print_exc())


    except KeyboardInterrupt:
        print('keyboard interrupt')
        sys.exit(0)







































