      # same 


        # load camera models 
        # reconstruction

        # same 

        # compute image pairs 
        # for each pairs 
        # reconstruction base on image pairs shots
        
        # start = timer()


        # # need the exifs 

        # lib.sfm_opensfm_reconstruction(file_path, opensfm_config)


        # end = timer()
        # sfm_opensfm_reconstruction_time = end - start

        # start = timer()

        # lib.sfm_undistort_image(file_path, opensfm_config)

        # end = timer()
        # sfm_undistort_image_time = end - start


        # start = timer()
        
        # lib.sfm_export_visual_sfm(file_path, opensfm_config)


        # end = timer()
        # sfm_export_visualsfm_time = end - start


        # start = timer()

        # lib.sfm_compute_depthmaps(file_path, opensfm_config)


        # end = timer()
        # sfm_compute_depthmaps_time = end - start


        # # split merge here no problem


        # start = timer()



        # # delete from makescene
        # lib.mve_makescene_function(file_path, 2)



        # end = timer()
        # mve_makescene_function_time = end - start

        # start = timer()

        # lib.mve_dense_reconstruction(file_path, 2)

        # end = timer()
        # mve_dense_reconstruction_time = end - start

        # start = timer()

        # lib.mve_scene2pset_function(file_path, 2)

        # end = timer()
        # mve_mve_scene2pset_time = end - start

        # start = timer()

        # lib.mve_cleanmesh_function(file_path,2)

        # end = timer()
        # mve_mve_cleanmesh_time = end - start


        # start = timer()


        # lib.odm_filterpoints_function(file_path, 2)


        # end = timer()
        # odm_filterpoint_time = end - start
        
        # start = timer()


        # lib.odm_mesh_function(file_path,2)

        # end = timer()
        # odm_mesh_time = end - start
        
        

        # job
        # merge for odm_texturing function
        # start = timer()
        # lib.odm_texturing_function(file_path)

        # end = timer()
        # odm_texturing_time = end - start




        # needs features _load 
        # needs feature matching 
        # needs list of images 




        #undistort , # load reconstruction
        # load images 
        # for each shot in reconstruction shot values 
        # #for each subshots 
        # undistort detection






        #export visual sfm 

        # 


        # compute depthmaps

        




        

        # need exif file
        # images 
        #  

        # job_task_detect = {'title': 'detect_features', 'client': node_client[2], 'nodeid': 1}
        # job_queue.put(job_task_detect)



        # job_task_detect = {'title': 'detect_features', 'client': node_client[3], 'nodeid': 1}
        # job_queue.put(job_task_detect)

        # job_queue.join()



        #feature matching





        # client = lib.FileClient('localhost:8080')
        # # demo for file uploading
        # in_file_name = 'IMG_2331.JPG'
        # response = client.upload('dataset/images/images/**', is_dir=True)
        # print("response" + str(response))


        #lib.mve_dense_reconstruction(images_filepath)