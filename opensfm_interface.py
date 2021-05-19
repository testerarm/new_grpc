# from opensfm create_submodels

import os
import json
import gzip
import pickle
import shutil, os, glob, math

from opensfm import geo


from opensfm import config
from opensfm import io
from opensfm import exif
from opensfm import bow
from opensfm import features
from opensfm import log

from opensfm import matching
from opensfm import pairs_selection


import logging
from timeit import default_timer as timer

from networkx.algorithms import bipartite



from opensfm import tracking


import numpy as np
import pickle
import gzip

from collections import defaultdict

#from opensfm_modified import undistort


#### undistort



#### detection

def _detection_path(file_path):
        return os.path.join(file_path, 'detections')

def _detection_file(file_path, image):
        return os.path.join(_detection_path(file_path), image + '.png')

def load_detection(file_path ,image):
        """Load image detection if it exists, otherwise return None."""
        detection_file = _detection_file(file_path, image)
        if os.path.isfile(detection_file):
            detection = io.imread(detection_file, grayscale=True)
        else:
            detection = None
        return detection

#### matches 

def _matches_path(file_path):
        """Return path of matches directory"""
        return os.path.join(file_path, 'matches')

def _matches_file(file_path, image, submodel=False):
        """File for matches for an image"""
        #print('matches file')
        #print(file_path)
        #print(image)
        #print('')
        if submodel:
            return os.path.join(file_path, '{}_matches.pkl.gz'.format(image))
        #print(os.path.join(_matches_path(file_path), '{}_matches.pkl.gz'.format(image)))
        #print('last ')
        return os.path.join(_matches_path(file_path), '{}_matches.pkl.gz'.format(image))

def matches_exists(file_path, image):
        return os.path.isfile(_matches_file(file_path, image))

def load_matches(file_path, image, submodel=False):

        #print('load matches: ' + file_path)
        path = _matches_file(file_path,image, submodel)
        #print('load file' + path)


        with gzip.open(path, 'rb') as fin:
            matches = pickle.load(fin)
        return matches

def save_matches(file_path, image, matches):
        #print('save matches: ' + file_path)
        io.mkdir_p(_matches_path(file_path))
        #print(' image: ' + image)
        with gzip.open(_matches_file(file_path,image), 'wb') as fout:
            pickle.dump(matches, fout)

def find_matches(file_path,im1, im2):
        if matches_exists(file_path,im1):
            im1_matches = load_matches(file_path,im1)
            if im2 in im1_matches:
                return im1_matches[im2]
        if matches_exists(file_path,im2):
            im2_matches = load_matches(file_path,im2)
            if im1 in im2_matches:
                if len(im2_matches[im1]):
                    return im2_matches[im1][:, [1, 0]]
        return []



########### save tracks

def _tracks_graph_file(file_path, filename=None):
        """Return path of tracks file"""
       
        return os.path.join(file_path, filename or 'tracks.csv')

def load_tracks_graph(file_path, filename=None):
        """Return graph (networkx data structure) of tracks"""
        with io.open_rt(_tracks_graph_file(file_path, filename)) as fin:
            return tracking.load_tracks_graph(fin)

def tracks_exists(file_path, filename=None):
        return os.path.isfile(_tracks_graph_file(file_path, filename))

def save_tracks_graph(graph, file_path, filename=None):
        with io.open_wt(_tracks_graph_file(file_path, filename)) as fout:
            tracking.save_tracks_graph(fout, graph)


def _camera_models_file(data_path):
        """Return path of camera model file"""
        return os.path.join(data_path, 'camera_models.json')

def load_camera_models(file_path):
        """Return camera models data"""
        with io.open_rt(_camera_models_file(file_path)) as fin:
            obj = json.load(fin)
            return io.cameras_from_json(obj)

def save_camera_models(file_path, camera_models):
        """Save camera models data"""
        with io.open_wt(_camera_models_file(file_path)) as fout:
            obj = io.cameras_to_json(camera_models)
            io.json_dump(obj, fout)



def _exif_file(file_path, image):
        """
        Return path of exif information for given image
        :param image: Image name, with extension (i.e. 123.jpg)
        """
        return os.path.join(file_path, image + '.exif')

def load_exif(file_path, image):
        """Load pre-extracted image exif metadata."""
        #print('load exif: ' + str(os.path.join(file_path, 'exif')))
        with io.open_rt(_exif_file(os.path.join(file_path, 'exif'), image)) as fin:
            return json.load(fin)


def save_exif(file_path, image, data):
        io.mkdir_p(file_path)
        #print(file_path)
        with io.open_wt(_exif_file(file_path, image)) as fout:
            print('dump')
            io.json_dump(data, fout)


def _camera_models_file(file_path):
        """Return path of camera model file"""
        return os.path.join(file_path, 'camera_models.json')

def save_camera_models(file_path, camera_models):
        """Save camera models data"""
        with io.open_wt(_camera_models_file(file_path)) as fout:
            obj = io.cameras_to_json(camera_models)
            io.json_dump(obj, fout)

def open_image_file(image_path):
        """Open image file and return file object."""
        return open(image_path, 'rb')



def open_image_size(image_path):
        """Height and width of the image."""
        return io.image_size(image_path)

#############################################   
# 
# 
# 
# 
#      

def get_config_file_path(filepath):
    """
        filepath: image file path
    """

    return io.join_paths(filepath, 'config.yaml')


def setup_opensfm_config(filepath):
    """
        filepath: image file path

        opensfm configuration for this image
    """
    
    return config.opensfm_load_config(filepath)



def load_opensfm_config(filepath):
    """
        filepath: image file path
    """

    # calls opensfm config.py
    return config.load_config(filepath)



def extract_metadata_image(image_path, opensfm_config):
    # EXIF data in Image
    #print(' extract meta from path: ' + str(image_path))

    d = exif.extract_exif_from_file(open_image_file(image_path))

    # Override projection type if needed (Use auto projection type)
    # if opensfm_config['camera_projection_type'] != 'AUTO':
    #     opensfm_config['projection_type'] = opensfm_config['camera_projection_type'].lower()

    # Image Height and Image Width
    if d['width'] <= 0 or not opensfm_config['use_exif_size']:
        d['height'], d['width'] = open_image_size(image_path)

    d['camera'] = exif.camera_id(d)

    return d



################################ detect features



def load_image(image_path, unchanged=False, anydepth=False):
        """Load image pixels as numpy array.

        The array is 3D, indexed by y-coord, x-coord, channel.
        The channels are in RGB order.
        """
        return io.imread(image_path, unchanged=unchanged, anydepth=anydepth)

def segmentation_ignore_values(image, opensfm_config):
        """List of label values to ignore.

        Pixels with this labels values will be masked out and won't be
        processed when extracting features or computing depthmaps.
        """
        return opensfm_config.get('segmentation_ignore_values', [])

def _segmentation_path(file_path):
        return os.path.join(file_path, 'segmentations')

def _segmentation_file(file_path, image):
        return os.path.join(_segmentation_path(file_path), image + '.png')

def load_segmentation(filepath, image):
        """Load image segmentation if it exists, otherwise return None."""
        segmentation_file = _segmentation_file(filepath, image)
        if os.path.isfile(segmentation_file):
            segmentation = io.imread(segmentation_file, grayscale=True)
        else:
            segmentation = None
        return segmentation


def load_segmentation_mask(filepath, image, opensfm_config):
        """Build a mask from segmentation ignore values.

        The mask is non-zero only for pixels with segmentation
        labels not in segmentation_ignore_values.
        """
        ignore_values = segmentation_ignore_values(image, opensfm_config)
        if not ignore_values:
            return None

        segmentation = load_segmentation(filepath, image)
        if segmentation is None:
            return None

        return _mask_from_segmentation(segmentation, ignore_values)

def _mask_from_segmentation(segmentation, ignore_values):
        mask = np.ones(segmentation.shape, dtype=np.uint8)
        for value in ignore_values:
            mask &= (segmentation != value)
        return mask

def _load_mask_list(self):
        """Load mask list from mask_list.txt or list masks/ folder."""
        mask_list_file = os.path.join(self.data_path, 'mask_list.txt')
        if os.path.isfile(mask_list_file):
            with io.open_rt(mask_list_file) as fin:
                lines = fin.read().splitlines()
            self._set_mask_list(lines)
        else:
            self._set_mask_path(os.path.join(self.data_path, 'masks'))

def load_mask(mask_files, image):
        """Load image mask if it exists, otherwise return None."""
        if image in mask_files:
            mask_path = mask_files[image]
            mask = io.imread(mask_path, grayscale=True)
            if mask is None:
                raise IOError("Unable to load mask for image {} "
                              "from file {}".format(image, mask_path))
        else:
            mask = None
        return mask

def load_combined_mask(filepath,opensfm_config ,mask_files, image):
        """Combine binary mask with segmentation mask.

        Return a mask that is non-zero only where the binary
        mask and the segmentation mask are non-zero.
        """
        mask = load_mask(mask_files, image)
        smask = load_segmentation_mask(filepath,image,opensfm_config)
        return _combine_masks(mask, smask)

def _combine_masks(mask, smask):
        if mask is None:
            if smask is None:
                return None
            else:
                return smask
        else:
            if smask is None:
                return mask
            else:
                return mask & smask

def load_features_mask(filepath, image, image_path, points, mask_files, opensfm_config):
        """Load a feature-wise mask.

        This is a binary array true for features that lie inside the
        combined mask.
        The array is all true when there's no mask.
        """
        if points is None or len(points) == 0:
            return np.array([], dtype=bool)

        mask_image = load_combined_mask(filepath, opensfm_config, mask_files, image)
        if mask_image is None:
            #logger.debug('load_im No segmentation for {}, no features masked.'.format(image))
            return np.ones((points.shape[0],), dtype=bool)

        exif = load_exif(file_path, image)
        width = exif["width"]
        height = exif["height"]
        orientation = exif["orientation"]

        new_height, new_width = mask_image.shape
        ps = upright.opensfm_to_upright(
            points[:, :2], width, height, orientation,
            new_width=new_width, new_height=new_height).astype(int)
        mask = mask_image[ps[:, 1], ps[:, 0]]

        n_removed = np.sum(mask == 0)
        # logger.debug('Masking {} / {} ({:.2f}) features for {}'.format(
        #     n_removed, len(mask), n_removed / len(mask), image))

        return np.array(mask, dtype=bool)

def _feature_file(feature_path, image):
        """
        Return path of feature file for specified image
        :param image: Image name, with extension (i.e. 123.jpg)
        """
        return os.path.join(feature_path, image + '.features.npz')

def _feature_file_legacy(feature_path, image):
        """
        Return path of a legacy feature file for specified image
        :param image: Image name, with extension (i.e. 123.jpg)
        """
        return os.path.join(feature_path, image + '.npz')

def load_features(feature_path, image, config):
        if os.path.isfile(_feature_file_legacy(feature_path, image)):
            return features.load_features(_feature_file_legacy(feature_path,image), config)
        return features.load_features(_feature_file(feature_path,image), config)

def _save_features(feature_path, opensfm_config, filepath, points, descriptors, colors=None):
        io.mkdir_p(feature_path)
        features.save_features(filepath, points, descriptors, colors, opensfm_config )

def save_features(feature_path, opensfm_config, image, points, descriptors, colors):

        _save_features(feature_path, opensfm_config, _feature_file(feature_path, image),points, descriptors, colors)


def _words_file(feature_path, image):
        return os.path.join(feature_path, image + '.words.npz')

def words_exist(feature_path, image):
        return os.path.isfile(_words_file(feature_path,image))

def load_words(feature_path, image_path):
    s = np.load(_words_file(feature_path,image_path))
    return s['words'].astype(np.int32)

def save_words(feature_path, image, words):
        np.savez_compressed(_words_file(feature_path,image), words=words.astype(np.uint16))


def detect(feature_path ,image_path,image ,opensfm_config):


    log.setup()

    need_words = opensfm_config['matcher_type'] == 'WORDS' or opensfm_config['matching_bow_neighbors'] > 0
    #has_words = not need_words or data.words_exist(image)
    #has_features = data.features_exist(image)

    # if has_features and has_words:
    #     logger.info('Skip recomputing {} features for image {}'.format(
    #         data.feature_type().upper(), image))
    #     return

    #logger.info('Extracting {} features for image {}'.format(data.feature_type().upper(), image))

    p_unmasked, f_unmasked, c_unmasked = features.extract_features(
        load_image(image_path), opensfm_config)

    #p_unmasked is points
    mask_files = defaultdict(lambda : None)
    fmask = load_features_mask(feature_path,image, image_path, p_unmasked, mask_files, opensfm_config)

    p_unsorted = p_unmasked[fmask]
    f_unsorted = f_unmasked[fmask]
    c_unsorted = c_unmasked[fmask]

    if len(p_unsorted) == 0:
        #logger.warning('No features found in image {}'.format(image))
        return

    size = p_unsorted[:, 2]
    order = np.argsort(size)
    p_sorted = p_unsorted[order, :]
    f_sorted = f_unsorted[order, :]
    c_sorted = c_unsorted[order, :]
    save_features(feature_path, opensfm_config,image, p_sorted, f_sorted, c_sorted)

    if need_words:
        bows = bow.load_bows(opensfm_config)
        n_closest = opensfm_config['bow_words_to_match']
        closest_words = bows.map_to_words(
            f_sorted, n_closest, opensfm_config['bow_matcher_type'])
        save_words(feature_path,image_path, closest_words)

    # end = timer()
    # report = {
    #     "image": image,
    #     "num_features": len(p_sorted),
    #     "wall_time": end - start,
    # }
    # data.save_report(io.json_dumps(report), 'features/{}.json'.format(image))



####################### Feature Matching 










def _reference_lla_path(file_path):
        return os.path.join(file_path, 'reference_lla.json')


def invent_reference_lla(file_path,images=None,submodel_path=''):
        lat, lon, alt = 0.0, 0.0, 0.0
        wlat, wlon, walt = 0.0, 0.0, 0.0
	save_path = file_path
	if submodel_path != '':
		save_path = submodel_path
        if images is None: 
            print('Noimages in invent reference lla')
        for image in images:
            d = load_exif(file_path,image)
            if 'gps' in d and 'latitude' in d['gps'] and 'longitude' in d['gps']:
                w = 1.0 / max(0.01, d['gps'].get('dop', 15))
                lat += w * d['gps']['latitude']
                lon += w * d['gps']['longitude']
                wlat += w
                wlon += w
                if 'altitude' in d['gps']:
                    alt += w * d['gps']['altitude']
                    walt += w

        if not wlat and not wlon:
            for gcp in _load_ground_control_points(None):
                lat += gcp.lla[0]
                lon += gcp.lla[1]
                alt += gcp.lla[2]
                wlat += 1
                wlon += 1
                walt += 1

        if wlat: lat /= wlat
        if wlon: lon /= wlon
        if walt: alt /= walt
        reference = {'latitude': lat, 'longitude': lon, 'altitude': 0}  # Set altitude manually.
        save_reference_lla(save_path, reference)
        return reference

def save_reference_lla(file_path, reference):
        with io.open_wt(_reference_lla_path(file_path)) as fout:
            io.json_dump(reference, fout)

def load_reference_lla(file_path):
        with io.open_rt(_reference_lla_path(file_path)) as fin:
            return io.json_load(fin)

def load_reference(file_path):
        """Load reference as a topocentric converter."""
        lla = load_reference_lla(file_path)
        return geo.TopocentricConverter(
            lla['latitude'], lla['longitude'], lla['altitude'])

def reference_lla_exists(file_path):
        return os.path.isfile(_reference_lla_path(file_path))




################################ reconstruction part





def _reconstruction_file(file_path,filename):
        """Return path of reconstruction file"""
        return os.path.join(file_path, filename or 'reconstruction.json')

def reconstruction_exists(file_path, filename=None):
        return os.path.isfile(_reconstruction_file(file_path,filename))

def load_reconstruction(file_path, filename=None):
        with io.open_rt(_reconstruction_file(file_path,filename)) as fin:
            reconstructions = io.reconstructions_from_json(io.json_load(fin))
        return reconstructions

def save_reconstruction(file_path,reconstruction, filename=None, minify=False):
        with io.open_wt(_reconstruction_file(file_path,filename)) as fout:
            io.json_dump(io.reconstructions_to_json(reconstruction), fout, minify)


################## load ground control points

def _ground_control_points_file(file_path):
        return os.path.join(file_path, 'ground_control_points.json')

def _gcp_list_file(file_path):
        return os.path.join(file_path, 'gcp_list.txt')

def load_ground_control_points(file_path, images):
        """Load ground control points.

        It uses reference_lla to convert the coordinates
        to topocentric reference frame.
        """

        reference = load_reference(file_path)
        return _load_ground_control_points(file_path,reference, images)

def _load_ground_control_points(file_path, reference, images):
        """Load ground control points.

        It might use reference to convert the coordinates
        to topocentric reference frame.
        If reference is None, it won't initialize topocentric data,
        thus allowing loading raw data only.
        """
        exif = {image: load_exif(file_path,image) for image in images}

        gcp = []
        if os.path.isfile(_gcp_list_file(file_path)):
            with io.open_rt(_gcp_list_file(file_path)) as fin:
                gcp = io.read_gcp_list(fin, reference, exif)

        pcs = []
        if os.path.isfile(_ground_control_points_file(file_path)):
            with io.open_rt(_ground_control_points_file(file_path)) as fin:
                pcs = io.read_ground_control_points(fin, reference)

        return gcp + pcs

def image_as_array(image):
        logger.warning("image_as_array() is deprecated. Use load_image() instead.")
        return load_image(image)

def mask_as_array(image):
        logger.warning("mask_as_array() is deprecated. Use load_mask() instead.")
        return load_mask({},image)





class UndistortedDataSet(object):
    """Accessors to the undistorted data of a dataset.

    Data include undistorted images, masks, and segmentation as well
    the undistorted reconstruction, tracks graph and computed depth maps.

    All data is stored inside a single folder which should be a subfolder
    of the base, distorted dataset.
    """
    def __init__(self,file_path ,opensfm_config ,undistorted_subfolder, self_compute=False, self_path=''):
        """Init dataset associated to a folder."""
        self.config = opensfm_config
        self.subfolder = undistorted_subfolder
        self.data_path = os.path.join(file_path, self.subfolder)
        self.path = file_path
        self.self_compute = self_compute
        self.self_path = os.path.join(file_path, self.subfolder)
        print(self.data_path)

    def _undistorted_image_path(self):
        return os.path.join(self.data_path, 'images')

    def _undistorted_image_file(self, image):
        """Path of undistorted version of an image."""
        image_format = self.config['undistorted_image_format']
        if ' ' in image:
            image = image.replace(' ', '') + hex(hash(image))
        filename = image + '.' + image_format
        return os.path.join(self._undistorted_image_path(), filename)

    def load_undistorted_image(self, image):
        """Load undistorted image pixels as a numpy array."""
        return io.imread(self._undistorted_image_file(image))

    def save_undistorted_image(self, image, array):
        """Save undistorted image pixels."""
        io.mkdir_p(self._undistorted_image_path())
        io.imwrite(self._undistorted_image_file(image), array)

    def undistorted_image_size(self, image):
        """Height and width of the undistorted image."""
        return io.image_size(self._undistorted_image_file(image))

    def _undistorted_mask_path(self):            
        return os.path.join(self.data_path, 'masks')

    def _undistorted_mask_file(self, image):
        """Path of undistorted version of a mask."""
        return os.path.join(self._undistorted_mask_path(), image + '.png')

    def undistorted_mask_exists(self, image):
        """Check if the undistorted mask file exists."""
        return os.path.isfile(self._undistorted_mask_file(image))

    def load_undistorted_mask(self, image):
        """Load undistorted mask pixels as a numpy array."""
        return io.imread(self._undistorted_mask_file(image), grayscale=True)

    def save_undistorted_mask(self, image, array):
        """Save the undistorted image mask."""
        io.mkdir_p(self._undistorted_mask_path())
        io.imwrite(self._undistorted_mask_file(image), array)

    def _undistorted_detection_path(self):
        return os.path.join(self.data_path, 'detections')

    def _undistorted_detection_file(self, image):
        """Path of undistorted version of a detection."""
        return os.path.join(self._undistorted_detection_path(), image + '.png')

    def undistorted_detection_exists(self, image):
        """Check if the undistorted detection file exists."""
        return os.path.isfile(self._undistorted_detection_file(image))

    def load_undistorted_detection(self, image):
        """Load an undistorted image detection."""
        return io.imread(self._undistorted_detection_file(image),
                         grayscale=True)

    def save_undistorted_detection(self, image, array):
        """Save the undistorted image detection."""
        io.mkdir_p(self._undistorted_detection_path())
        io.imwrite(self._undistorted_detection_file(image), array)

    def _undistorted_segmentation_path(self):
        return os.path.join(self.data_path, 'segmentations')

    def _undistorted_segmentation_file(self, image):
        """Path of undistorted version of a segmentation."""
        return os.path.join(self._undistorted_segmentation_path(), image + '.png')

    def undistorted_segmentation_exists(self, image):
        """Check if the undistorted segmentation file exists."""
        return os.path.isfile(self._undistorted_segmentation_file(image))

    def load_undistorted_segmentation(self, image):
        """Load an undistorted image segmentation."""
        return io.imread(self._undistorted_segmentation_file(image),
                         grayscale=True)

    def save_undistorted_segmentation(self, image, array):
        """Save the undistorted image segmentation."""
        io.mkdir_p(self._undistorted_segmentation_path())
        io.imwrite(self._undistorted_segmentation_file(image), array)

    def load_undistorted_segmentation_mask(self, image):
        """Build a mask from the undistorted segmentation.

        The mask is non-zero only for pixels with segmentation
        labels not in segmentation_ignore_values.
        """
        ignore_values = segmentation_ignore_values(image, self.config)
        if not ignore_values:
            return None

        segmentation = self.load_undistorted_segmentation(image)
        if segmentation is None:
            return None

        return _mask_from_segmentation(segmentation, ignore_values)

    def load_undistorted_combined_mask(self, image):
        """Combine undistorted binary mask with segmentation mask.

        Return a mask that is non-zero only where the binary
        mask and the segmentation mask are non-zero.
        """
        mask = None
        if self.undistorted_mask_exists(image):
            mask = self.load_undistorted_mask(image)
        smask = None
        if self.undistorted_segmentation_exists(image):
            smask = self.load_undistorted_segmentation_mask(image)
        return _combine_masks(mask, smask)

    def _depthmap_path(self):
        return os.path.join(self.data_path, 'depthmaps')

    def _depthmap_file(self, image, suffix):
        """Path to the depthmap file"""
        #print('depthmap file path: '+ str(self._depthmap_path()) + " " + str(image + '.' + suffix))
        return os.path.join(self._depthmap_path(), image + '.' + suffix)

    def raw_depthmap_exists(self, image):
        return os.path.isfile(self._depthmap_file(image, 'raw.npz'))

    def save_raw_depthmap(self, image, depth, plane, score, nghbr, nghbrs):
        io.mkdir_p(self._depthmap_path())
        filepath = self._depthmap_file(image, 'raw.npz')


        
        np.savez_compressed(filepath, depth=depth, plane=plane, score=score, nghbr=nghbr, nghbrs=nghbrs)
        
        #self.load_raw_depthmap(image)


    def load_raw_depthmap(self, image):
        #print('load raw: ' + str(self._depthmap_file(image, 'raw.npz')))
        o = np.load(self._depthmap_file(image, 'raw.npz'))
        return o['depth'], o['plane'], o['score'], o['nghbr'], o['nghbrs']

    def clean_depthmap_exists(self, image):
        return os.path.isfile(self._depthmap_file(image, 'clean.npz'))

    def save_clean_depthmap(self, image, depth, plane, score):
        io.mkdir_p(self._depthmap_path())
        filepath = self._depthmap_file(image, 'clean.npz')

        
        np.savez_compressed(filepath, depth=depth, plane=plane, score=score)

    def load_clean_depthmap(self, image):
        #print('load clean depth map')

        o = np.load(self._depthmap_file(image, 'clean.npz'))
        return o['depth'], o['plane'], o['score']

    def pruned_depthmap_exists(self, image):
        return os.path.isfile(self._depthmap_file(image, 'pruned.npz'))

    def save_pruned_depthmap(self, image, points, normals, colors, labels, detections):
        io.mkdir_p(self._depthmap_path())
        filepath = self._depthmap_file(image, 'pruned.npz')
        np.savez_compressed(filepath,
                            points=points, normals=normals,
                            colors=colors, labels=labels,
                            detections=detections)

    def load_pruned_depthmap(self, image):
        try:
            print('load pruned depthmap')


            o = np.load(self._depthmap_file(image, 'pruned.npz'))
        
            if 'detections' not in o:
                return o['points'], o['normals'], o['colors'], o['labels'], np.zeros(o['labels'].shape)
            else:
                return o['points'], o['normals'], o['colors'], o['labels'], o['detections']
        except Exception as e:
            print(e.message)
            print(image)

    def load_undistorted_tracks_graph(self):
        return load_tracks_graph(self.data_path ,os.path.join('tracks.csv'))

    def save_undistorted_tracks_graph(self, graph):
        return save_tracks_graph(graph,self.data_path ,os.path.join('tracks.csv'))

    def load_undistorted_reconstruction(self):
        return load_reconstruction(self.data_path ,
            filename=os.path.join('reconstruction.json'))

    def save_undistorted_reconstruction(self, reconstruction):
        io.mkdir_p(self.data_path)

        return save_reconstruction(self.data_path,
            reconstruction, filename=os.path.join('reconstruction.json'))






























